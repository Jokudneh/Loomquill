"""Unit tests for type conversion errors."""

import re
from datetime import timedelta
from string import ascii_lowercase
from typing import Tuple

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from flytekit import task, workflow
from flytekit.core.type_engine import TypeTransformerFailedError


@task
def int_to_float(n: int) -> float:
    return float(n)


@task
def task_incorrect_output(a: float) -> int:
    return str(a)  # type: ignore [return-value]


@task
def task_correct_output(a: float) -> str:
    return str(a)


@workflow
def wf_with_task_error(a: int) -> str:
    return task_incorrect_output(a=int_to_float(n=a))


@workflow
def wf_with_output_error(a: int) -> int:
    return task_correct_output(a=int_to_float(n=a))


@workflow
def wf_with_multioutput_error0(a: int, b: int) -> Tuple[int, str]:
    out_a = task_correct_output(a=int_to_float(n=a))
    out_b = task_correct_output(a=int_to_float(n=b))
    return out_a, out_b


@workflow
def wf_with_multioutput_error1(a: int, b: int) -> Tuple[str, int]:
    out_a = task_correct_output(a=int_to_float(n=a))
    out_b = task_correct_output(a=int_to_float(n=b))
    return out_a, out_b


@given(st.booleans() | st.integers() | st.text(ascii_lowercase))
