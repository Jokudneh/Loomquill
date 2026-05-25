from pydantic import BaseModel, Field
import pytest
import os
import copy

from flytekit import task, workflow

@pytest.fixture(autouse=True)
def prepare_env_variable():
    try:
        origin_env = copy.deepcopy(os.environ.copy())
        os.environ["FLYTE_USE_OLD_DC_FORMAT"] = "True"
        yield
    finally:
        os.environ = origin_env


def test_dataclasss_in_pydantic_basemodel():
    from dataclasses import dataclass

    @dataclass
    class InnerBM:
        a: int = -1
        b: float = 3.14
        c: str = "Hello, Flyte"
        d: bool = False
