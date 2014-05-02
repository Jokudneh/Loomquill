"""Manages an async event loop on another thread. Developers should only require to call
sync to use the managed loop:

from flytekit.tools.asyn import run_sync

async def async_add(a: int, b: int) -> int:
    return a + b

result = run_sync(async_add, a=10, b=12)
"""

import asyncio
import atexit
import functools
import os
import threading
from contextlib import contextmanager
from typing import Any, Awaitable, Callable, TypeVar

from typing_extensions import ParamSpec

from flytekit.loggers import logger

T = TypeVar("T")

P = ParamSpec("P")


@contextmanager
def _selector_policy():
    original_policy = asyncio.get_event_loop_policy()
