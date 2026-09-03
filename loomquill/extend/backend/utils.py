import asyncio
import functools
import inspect
from typing import Callable, Coroutine

from flyteidl.core.execution_pb2 import TaskExecution

import flytekit
from flytekit.models.task import TaskTemplate


def mirror_async_methods(func: Callable, **kwargs) -> Coroutine:
    if inspect.iscoroutinefunction(func):
        return func(**kwargs)
    return asyncio.get_running_loop().run_in_executor(None, functools.partial(func, **kwargs))


def convert_to_flyte_phase(state: str) -> TaskExecution.Phase:
