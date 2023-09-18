from typing import Optional, TypedDict


class QueueOption(TypedDict):
    queue_name: Optional[str]
    max_attempt: Optional[int]
    concurrency: Optional[int]
