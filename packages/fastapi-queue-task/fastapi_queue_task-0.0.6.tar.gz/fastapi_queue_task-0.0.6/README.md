# FastAPI queue

## How to use

1. Instance the class `Queue` with `redis` instance and `options`

```python
# queue_config.py

from fastapi_queue_task import Queue
from redis.asyncio.utils import from_url

redis = from_url(
    f"redis://#REDIS_HOST:#REDIS_PORT/#REDIS_DATABASE_NAME",
    encoding="utf-8",
    decode_responses=True,
)
queue = Queue(redis, {'concurrency': 10, 'max_attempt': 3})
queue.run()
```

2. The `Queue` class expose 2 methods that we can use:

```python
# mail_service.py
from queue_config.py import queue

await queue.add_class_to_queue(
    name="TASK_NAME",
    data=CustomClass(),
)

await queue.add_to_queue(name="TASK_NAME", data={})
```

## How to test in testpypi

1. Increase the version in `pyproject.toml`
2. Run command

```bash
$ . ./build_and_test.sh
```

## How to publish new version

1. Increase the version in `pyproject.toml`
2. Run command

```bash
$ . ./build_and_publish.sh
```
