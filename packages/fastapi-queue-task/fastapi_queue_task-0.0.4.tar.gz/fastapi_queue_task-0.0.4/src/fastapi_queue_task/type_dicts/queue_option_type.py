from typing import TypedDict


class QueueOption(TypedDict):
    max_attempt: int
    concurrency: int
