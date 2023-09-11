import reactivex

from elm_framework_helpers.operators.retry_with_delay import resettable_counter, retry_with_delay

retry_with_backoff = retry_with_delay(resettable_counter([0, 0, 1, 2, 5], infinite_behavior="loop"), reset_after=reactivex.empty())

__all__ = [
    "retry_with_backoff",
]