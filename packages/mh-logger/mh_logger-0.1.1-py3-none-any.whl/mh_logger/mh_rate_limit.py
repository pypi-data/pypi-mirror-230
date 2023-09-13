from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Thread
from typing import Any, Dict, Optional

from mh_logger import LoggingManager

global_logger = LoggingManager(__name__)


@dataclass
class UserRate:
    user_id: str
    rate_id: str
    rate: int
    rate_limit: int


class ValidateRateLimit:
    def __init__(
        self,
        rate_id: str,
        rate_limit: int,
        timedelta_: timedelta,
        service_name: str,
        project: str,
        resource_type: str = "cloud_run_revision",
        location: str = "us-central1",
        logger: Optional[LoggingManager] = None,
    ):
        self.rate_id = rate_id
        self.rate_limit = rate_limit
        self.timedelta_ = timedelta_
        self.service_name = service_name
        self.project = project
        self.resource_type = resource_type
        self.location = location
        if logger:
            self._logger = logger
        else:
            self._logger = global_logger

    def validate_user_rate(self, user_id: str) -> None:
        approx_user_rate = self.get_approx_user_rate(user_id, self.rate_id)
        if approx_user_rate is not None and approx_user_rate < self.rate_limit:
            return
        raise Exception(
            f"""
Usage rate :: {approx_user_rate} exceeds rate_limit :: {self.rate_limit}
with rate_id :: {self.rate_id} for user_id :: {user_id}.
        """
        )

    def update_user_rate(self, user_id: str) -> None:
        """
        WARNING: This method is expensive.
                 The more filters in `list_entries`, the better.

        Retrieves all log entries for a given set of filters
        and counts them against the rate_limit.
        """

        # We need the raw GCP logging client, as opposed to the wrapper
        gcp_logging_client = self._logger.gcp_logging_client
        if not gcp_logging_client:
            # Local dev most likely
            return

        time_window_start = datetime.now(timezone.utc) - self.timedelta_
        # Returns all logging entries for timestamp >= time_window_start
        # WARNING: This method is expensive. The more filters, the better.
        usage_logs = list(
            gcp_logging_client.list_entries(
                resource_names=[f"projects/{self.project}"],
                filter_=f"""
                    jsonPayload.rate_id = {self.rate_id}
                    AND resource.type = "{self.resource_type}"
                    AND resource.labels.service_name = "{self.service_name}"
                    AND resource.labels.location = "{self.location}"
                    AND jsonPayload.user_id = {user_id}
                    AND timestamp >= "{time_window_start.isoformat()}"
                """,
                order_by="timestamp desc",  # Assumption: This is expensive
                max_results=self.rate_limit,
            )
        )

        self.save_user_rate(
            UserRate(user_id, self.rate_id, len(usage_logs), self.rate_limit)
        )

    def __call__(
        self,
        user_id: str,
        request: Dict[str, Any],
        downstream_method,
        url,
    ):
        "Validates user usage and logs it."
        self.validate_user_rate(user_id)  # Throws

        self._logger.info(
            url.path,
            rate_id=self.rate_id,
            module=downstream_method.__module__,
            method=downstream_method.__name__,
            endpoint=url.path,
            request=request,
            user_id=user_id,
        )

        # Will run in the background
        Thread(target=self.update_user_rate, args=[user_id]).start()

    @abstractmethod
    def get_approx_user_rate(
        self, user_id: str, rate_id: str
    ) -> Optional[int]:
        ...

    @abstractmethod
    def save_user_rate(self, user_rate: UserRate) -> None:
        ...
