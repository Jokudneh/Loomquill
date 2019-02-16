import typing
from datetime import datetime
from random import seed

import flytekit.configuration
from flytekit import dynamic, task, workflow
from flytekit.configuration import Image, ImageConfig
from flytekit.core import context_manager
from flytekit.core.condition import conditional
from flytekit.core.context_manager import ExecutionState

# seed random number generator
seed(datetime.now().microsecond)


def test_dynamic_conditional():
    @task
    def split(in1: typing.List[int]) -> (typing.List[int], typing.List[int], int):
        return in1[0 : int(len(in1) / 2)], in1[int(len(in1) / 2) + 1 :], len(in1) / 2

    # One sample implementation for merging. In a more real world example, this might merge file streams and only load
    # chunks into the memory.
    @task
    def merge(x: typing.List[int], y: typing.List[int]) -> typing.List[int]:
        n1 = len(x)
        n2 = len(y)
        result = typing.List[int]()
        i = 0
