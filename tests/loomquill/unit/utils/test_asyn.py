import os
import threading
import sys

import mock
import pytest
import asyncio
from typing import List, Dict, Optional
from asyncio import get_running_loop
from functools import partial
from flytekit.utils.asyn import run_sync, loop_manager

from contextvars import ContextVar


async def async_add(a: int, b: int) -> int:
    return a + b


def test_run_async_function():
    result = run_sync(async_add, a=10, b=12)
    assert result == 22


def sync_sub(a: int, b: int) -> int:
    return a - b


async def async_sub(a: int, b: int) -> int:
    loop = get_running_loop()
    return await loop.run_in_executor(None, partial(sync_sub, a=a, b=b))


def test_run_sync_in_async():
    result = run_sync(async_sub, a=10, b=12)
    assert result == -2


async def async_multiply_inner(a: int, b: int) -> int:
    return a * b


def sync_sub_that_calls_sync(a: int, b: int) -> int:
