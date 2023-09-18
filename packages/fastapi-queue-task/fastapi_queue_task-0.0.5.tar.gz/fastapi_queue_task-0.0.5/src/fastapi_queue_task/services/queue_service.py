import asyncio
import base64
import pickle
import sys
import pydash
from typing import Any
from ..constants.queue_constant import QUEUE_NAME
from ..type_dicts.queue_option_type import QueueOption
from ..loggers.logger import logger
from ..tasks.storage import list_tasks


class Queue:
    running_tasks = set()

    def __init__(self, redis: Any, options: QueueOption):
        self.redis = redis
        self.queue_name = options.get('queue_name') or QUEUE_NAME
        self.concurrency = options.get('concurrency') or 10
        self.max_attempt = options.get('max_attempt') or 3

    async def __get_queue(self):
        if len(self.running_tasks) <= self.concurrency:
            detail = await self.redis.rpop(self.queue_name)
            if detail:
                task = asyncio.create_task(self.__process_queue(detail))
                self.running_tasks.add(task)
                task.add_done_callback(lambda t: self.running_tasks.discard(t))

        await asyncio.sleep(2)
        asyncio.create_task(self.__get_queue())

    def run(self):
        asyncio.create_task(self.__get_queue())

    def __find_task_handler(self, name: str):
        task = pydash.find(list_tasks, lambda t: t["name"] == name)
        if task:
            return task

        logger.info(f"Dont have any handler for task: {task}")

    async def __add_retry_queue(self, queue_data, exception: Exception):
        logger.error(f"Exception {str(exception)}")
        if queue_data["attempt"] > self.max_attempt:
            logger.error(f"Max attempt: {queue_data['attempt']}, please recheck the code")
            await self.__add_to_list("failed_queue", base64.b64encode(pickle.dumps(queue_data)))
        else:
            queue_data["attempt"] += 1
            await self.add_queue(queue_data)

    async def __process_queue(self, detail):
        logger.info("Start run queue")

        queue_data = pickle.loads(base64.b64decode(detail))
        if queue_data["attempt"]:
            logger.warning(f"Attempt to run queue: {queue_data['attempt']}")
        task = self.__find_task_handler(queue_data["name"])

        if not task:
            logger.error("Empty task handler")
            return
        logger.info(f"Run queue: {queue_data['name']}")

        try:
            await task["handler"](queue_data["data"])
        except Exception as exception:
            await self.__add_retry_queue(queue_data, exception)

        logger.info(f"End queue: {queue_data['name']}")

    async def __add_to_list(self, key: str, value: Any):
        print("Add to list")
        return await self.redis.lpush(key, value)

    async def add_to_queue(self, name: str, data: Any):
        if "pytest" in sys.modules:
            return

        await self.__add_to_list(
            "queue",
            base64.b64encode(pickle.dumps({"name": name, "data": data, "attempt": 0})),
        )

    async def add_class_to_queue(self, name: str, data: Any):
        if "pytest" in sys.modules:
            return

        await self.__add_to_list(
            "queue",
            base64.b64encode(pickle.dumps({"name": name, "data": data, "attempt": 0})),
        )

    async def add_queue(self, options):
        await self.__add_to_list("queue", base64.b64encode(pickle.dumps(options)))
