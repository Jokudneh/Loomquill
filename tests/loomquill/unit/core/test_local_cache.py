import datetime
import pathlib
import pickle
import re
import subprocess
import sys
import textwrap
import typing
from dataclasses import dataclass
from typing import Dict, List

import pytest
from dataclasses_json import DataClassJsonMixin
from pytest import fixture
from typing_extensions import Annotated

import flytekit
from flytekit.core.base_sql_task import SQLTask
from flytekit.core.base_task import kwtypes
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.dynamic_workflow_task import dynamic
from flytekit.core.hash import HashMethod
from flytekit.core.local_cache import LocalTaskCache, _calculate_cache_key, _recursive_hash_placement
from flytekit.core.task import TaskMetadata, task
from flytekit.core.testing import task_mock
from flytekit.core.type_engine import TypeEngine
from flytekit.core.workflow import workflow
from flytekit.models.literals import Literal, LiteralCollection, LiteralMap, Primitive, Scalar
from flytekit.models.types import LiteralType, SimpleType
from flytekit.types.schema import FlyteSchema

# Global counter used to validate number of calls to cache
n_cached_task_calls = 0


@fixture(scope="function", autouse=True)
def setup():
    global n_cached_task_calls
    n_cached_task_calls = 0

    LocalTaskCache.initialize()
    LocalTaskCache.clear()


@pytest.mark.serial
def test_to_confirm_that_cache_keys_include_function_name():
    """
    This test confirms that the function name is part of the cache key. It does so by defining 2 tasks with
    identical parameters and metadata (i.e. cache=True and cache version).
    """

    @task(cache=True, cache_version="v1")
    def f1(n: int) -> int:
        global n_cached_task_calls
        n_cached_task_calls += 1

        return n

    @task(cache=True, cache_version="v1")
    def f2(n: int) -> int:
        global n_cached_task_calls
        n_cached_task_calls += 1

        return n + 1

    @workflow
    def wf(n: int) -> typing.Tuple[int, int]:
        n_f1 = f1(n=n)
        n_f2 = f2(n=n)
        return n_f1, n_f2

    # This is demonstrating that calls to f1 and f2 are cached by input parameters.
    assert wf(n=1) == (1, 2)


@pytest.mark.serial
def test_single_task_workflow():
    @task(cache=True, cache_version="v1")
    def is_even(n: int) -> bool:
        global n_cached_task_calls
        n_cached_task_calls += 1
        return n % 2 == 0

    @task(cache=False)
    def uncached_task(a: int, b: int) -> int:
        return a + b

    @workflow
    def check_evenness(n: int) -> bool:
        uncached_task(a=n, b=n)
        return is_even(n=n)

    assert n_cached_task_calls == 0
    assert check_evenness(n=1) is False
    # Confirm task is called
    assert n_cached_task_calls == 1
    assert check_evenness(n=1) is False
    # Subsequent calls of the workflow with the same parameter do not bump the counter
    assert n_cached_task_calls == 1
    assert check_evenness(n=1) is False
    assert n_cached_task_calls == 1

    # Run workflow with a different parameter and confirm counter is bumped
    assert check_evenness(n=8) is True
    assert n_cached_task_calls == 2
    # Run workflow again with the same parameter and confirm the counter is not bumped
    assert check_evenness(n=8) is True
    assert n_cached_task_calls == 2


@pytest.mark.serial
def test_cache_can_be_disabled(monkeypatch):
    monkeypatch.setenv("FLYTE_LOCAL_CACHE_ENABLED", "false")

    @task(cache=True, cache_version="v1")
    def is_even(n: int) -> bool:
        global n_cached_task_calls
        n_cached_task_calls += 1
        return n % 2 == 0

    assert n_cached_task_calls == 0
    # Run once and check that the counter is increased
    assert is_even(n=1) is False
    assert n_cached_task_calls == 1

    # Run again and check that the counter is increased again i.e. no caching
    assert is_even(n=1) is False
    assert n_cached_task_calls == 2


@pytest.mark.serial
def test_cache_can_be_overwrited(monkeypatch):
    @task(cache=True, cache_version="v1")
    def is_even(n: int) -> bool:
        global n_cached_task_calls
        n_cached_task_calls += 1
        return n % 2 == 0

    assert n_cached_task_calls == 0

    # Run once and check that the counter is increased
    assert is_even(n=1) is False
    assert n_cached_task_calls == 1

    # Run again and check that the counter is not increased, i.e. cache hit
    assert is_even(n=1) is False
    assert n_cached_task_calls == 1

    # function changed
    @task(cache=True, cache_version="v1")
    def is_even(n: int) -> bool:
        global n_cached_task_calls
        n_cached_task_calls += 1
        return n % 2 == 1

    monkeypatch.setenv("FLYTE_LOCAL_CACHE_OVERWRITE", "true")

    # Run again and check that the counter is increased again, i.e. cache overwrite
    assert is_even(n=1) is True
    assert n_cached_task_calls == 2

    monkeypatch.setenv("FLYTE_LOCAL_CACHE_OVERWRITE", "false")

    # Run again and check that the counter is not increased, i.e. cache hit
    assert is_even(n=1) is True
    assert n_cached_task_calls == 2


@pytest.mark.serial
def test_shared_tasks_in_two_separate_workflows():
    @task(cache=True, cache_version="0.0.1")
    def is_odd(n: int) -> bool:
        global n_cached_task_calls
        n_cached_task_calls += 1
        return n % 2 == 1

    @workflow
    def check_oddness_wf1(n: int) -> bool:
        return is_odd(n=n)

    @workflow
    def check_oddness_wf2(n: int) -> bool:
        return is_odd(n=n)

    assert n_cached_task_calls == 0
    assert check_oddness_wf1(n=42) is False
    assert check_oddness_wf1(n=99) is True
    assert n_cached_task_calls == 2

    # The next two executions of the *_wf2 workflow are going to
    # hit the cache for the calls to `is_odd`
    assert check_oddness_wf2(n=42) is False
    assert check_oddness_wf2(n=99) is True
    assert n_cached_task_calls == 2
