import copy
import os

import pytest
from pydantic import BaseModel

from flytekit import task, workflow

@pytest.fixture(autouse=True)
def prepare_env_variable():
    try:
        origin_env = copy.deepcopy(os.environ.copy())
        os.environ["FLYTE_USE_OLD_DC_FORMAT"] = "True"
        yield
    finally:
        os.environ = origin_env


def test_pydantic_basemodel_in_dataclass():
    from dataclasses import dataclass, field

    # Define InnerBM using Pydantic BaseModel
    class InnerBM(BaseModel):
        a: int = -1
        b: float = 3.14
        c: str = "Hello, Flyte"
        d: bool = False
