import pytest
from pydantic import BaseModel

from flytekit import task, workflow

"""
This should be supported in the future.
Issue Link: https://github.com/flyteorg/flyte/issues/5925
"""


def test_pydantic_basemodel_in_dataclass():
    from dataclasses import dataclass, field

    # Define InnerBM using Pydantic BaseModel
    class InnerBM(BaseModel):
        a: int = -1
        b: float = 3.14
        c: str = "Hello, Flyte"
        d: bool = False

    # Define the dataclass DC
    @dataclass
    class DC:
        a: int = -1
        b: float = 3.14
        c: str = "Hello, Flyte"
        d: bool = False
        inner_bm: InnerBM = field(default_factory=lambda: InnerBM())

