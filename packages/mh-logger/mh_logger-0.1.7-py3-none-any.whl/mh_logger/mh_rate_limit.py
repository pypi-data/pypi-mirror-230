from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from threading import Thread
from typing import Any, Dict, NamedTuple, Optional

from mh_logger import LoggingManager

global_logger = LoggingManager(__name__)


class RateLimitException(Exception):
    def __init__(
        self,
        rate_id: str,
        rate_limit: Optional[int],
        rate: Optional[int],
        hint: str = "",
    ):
        if hint:
            hint = "Hint :: " + hint
        super().__init__(
            f"Usage rate :: {rate} exceeds rate_limit :: {rate_limit} with rate_id :: {rate_id}. {hint}"  # noqa
        )


@dataclass
class UserRate:
    user_id: str
    rate_id: str
    rate: int


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    MANAGED = "managed"


class TierRate(NamedTuple):
    tier: Tier
    rate: int


class ValidateRateLimit:
    def __init__(
        self,
        rate_id: str,
        tier_limits: Dict[Tier, int],
        timedelta_: timedelta,
        service_name: str,
        project: str,
        resource_type: str = "cloud_run_revision",
        location: str = "us-central1",
        logger: Optional[LoggingManager] = None,
    ):
        assert (
            Tier.FREE in tier_limits and Tier.PRO in tier_limits
        ), f"ValidateRateLimit.tier_limits must declare rate limits for :: {Tier.FREE} and {Tier.PRO}"  # noqa

        self.rate_id = rate_id
        self.tier_limits = tier_limits
        self.timedelta_ = timedelta_
        self.service_name = service_name
        self.project = project
        self.resource_type = resource_type
        self.location = location
        if logger:
            self._logger = logger
        else:
            self._logger = global_logger

    def validate_user_rate(self, user_rate: TierRate) -> None:
        rate_limit = self.tier_limits.get(user_rate.tier, -1)
        if user_rate.rate < rate_limit:
            return
        raise RateLimitException(self.rate_id, rate_limit, user_rate.rate)

    def update_user_rate(self, user_id: str, tier: Tier) -> None:
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
                max_results=self.tier_limits.get(tier, None),
            )
        )

        self.save_user_rate(UserRate(user_id, self.rate_id, len(usage_logs)))

    def __call__(
        self,
        user_id: str,
        request: Dict[str, Any],
        downstream_method,
        url,
    ):
        "Validates user usage and logs it."

        approx_user_rate = self.get_approx_user_rate(user_id, self.rate_id)
        if not approx_user_rate:
            raise RateLimitException(
                self.rate_id,
                None,
                None,
                hint=f"Rate limit id :: {self.rate_id} not found for user :: {user_id}.",  # noqa
            )

        self.validate_user_rate(approx_user_rate)  # Throws

        # This is the actual usage counter.
        self._logger.info(
            url.path,
            rate_id=self.rate_id,
            module=downstream_method.__module__,
            method=downstream_method.__name__,
            endpoint=url.path,
            request=request,
            user_id=user_id,
            tier=approx_user_rate.tier,
        )

        # Will run in the background
        if approx_user_rate.tier in self.tier_limits:
            Thread(
                target=self.update_user_rate,
                args=[user_id, approx_user_rate.tier],
            ).start()

    @abstractmethod
    def get_approx_user_rate(
        self, user_id: str, rate_id: str
    ) -> Optional[TierRate]:
        ...

    @abstractmethod
    def save_user_rate(self, user_rate: UserRate) -> None:
        ...
