from enum import Enum

from flytekit import task, workflow


def test_dynamic_local():
    class Color(Enum):
