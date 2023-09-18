import inspect
from abc import abstractmethod
from contextlib import AsyncExitStack
from typing import Callable, Any

from fastapi import Request
from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import get_dependant, solve_dependencies
from pydantic import ValidationError


class BaseTask:
    _task_name: str

    @abstractmethod
    async def handler(self, data):
        pass

    async def solve_depends(self, request: Request, dependant: Dependant):
        values, errors, _1, _2, _3 = await solve_dependencies(request=request, dependant=dependant)
        if errors:
            raise ValidationError(errors, None)
        if inspect.iscoroutinefunction(dependant.call):
            result = await dependant.call(**values)
        else:
            result = dependant.call(**values)

        return result

    async def init_task(self, handler: Callable, data: Any):
        async with AsyncExitStack() as cm:
            request = Request({"type": "http", "headers": [], "query_string": "", "fastapi_astack": cm})

            dependant = get_dependant(path=f"task:{self._task_name}", call=handler)

            await self.solve_depends(request, dependant)
            await self.handler(data)

    async def run(self, data):
        await self.init_task(self.__init__, data)

    @classmethod
    def makeit(cls):
        self = cls.__new__(cls)
        return self
