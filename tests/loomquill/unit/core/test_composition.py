from typing import Dict, List, NamedTuple, Optional, Union

from flytekit.core import launch_plan
from flytekit.core.task import task
from flytekit.core.workflow import workflow
from flytekit.models import literals as _literal_models


def test_wf1_with_subwf():
    @task
    def t1(a: int) -> NamedTuple("OutputsBC", t1_int_output=int, c=str):
        a = a + 2
        return a, "world-" + str(a)

    @task
    def t2(a: str, b: str) -> str:
        return b + a

    @workflow
    def my_subwf(a: int) -> (str, str):
        x, y = t1(a=a)
        u, v = t1(a=x)
        return y, v

    @workflow
    def my_wf(a: int, b: str) -> (int, str, str):
        x, y = t1(a=a).with_overrides()
        u, v = my_subwf(a=x)
        return x, u, v

    res = my_wf(a=5, b="hello ")
    assert res == (7, "world-9", "world-11")


def test_single_named_output_subwf():
    nt = NamedTuple("SubWfOutput", [("sub_int", int)])

    @task
    def t1(a: int) -> nt:
        a = a + 2
        return nt(a)

    @task
    def t2(a: int, b: int) -> nt:
        return nt(a + b)  # returns the named tuple

    @workflow
    def my_subwf(a: int) -> nt:
        x = t1(a=a)
