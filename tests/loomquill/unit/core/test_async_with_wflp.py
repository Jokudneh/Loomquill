import asyncio
import typing
import pytest

from flytekit.core.task import task, eager
from flytekit.core.workflow import workflow
from flytekit.configuration import Config
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.launch_plan import LaunchPlan
from flytekit.core.data_persistence import FileAccessProvider
from flytekit.remote.remote import FlyteRemote
from flytekit.utils.asyn import loop_manager


@task
def add_one(x: int) -> int:
    return x + 1


@task
async def a_double(x: int) -> int:
    return x * 2


@task
def double(x: int) -> int:
    return x * 2

