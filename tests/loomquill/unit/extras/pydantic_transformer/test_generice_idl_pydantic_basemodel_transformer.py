import copy
import os
import tempfile
from enum import Enum
from typing import Dict, List, Optional
from unittest.mock import patch

import pytest
from google.protobuf import json_format as _json_format
from google.protobuf import struct_pb2 as _struct
from pydantic import BaseModel, Field

from flytekit import task, workflow
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.type_engine import TypeEngine
from flytekit.models.literals import Literal, Scalar
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile
from flytekit.types.schema import FlyteSchema
from flytekit.types.structured import StructuredDataset


@pytest.fixture(autouse=True)
def prepare_env_variable():
    try:
        origin_env = copy.deepcopy(os.environ.copy())
        os.environ["FLYTE_USE_OLD_DC_FORMAT"] = "True"
        yield
    finally:
        os.environ = origin_env


class Status(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@pytest.fixture
def local_dummy_file():
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write("Hello FlyteFile")
        yield path
    finally:
        os.remove(path)


@pytest.fixture
def local_dummy_directory():
    temp_dir = tempfile.TemporaryDirectory()
    try:
        with open(os.path.join(temp_dir.name, "file"), "w") as tmp:
            tmp.write("Hello FlyteDirectory")
        yield temp_dir.name
    finally:
        temp_dir.cleanup()


def test_flytetypes_in_pydantic_basemodel_wf(local_dummy_file, local_dummy_directory):
    class InnerBM(BaseModel):
        flytefile: FlyteFile = Field(
            default_factory=lambda: FlyteFile(local_dummy_file)
        )
        flytedir: FlyteDirectory = Field(
            default_factory=lambda: FlyteDirectory(local_dummy_directory)
        )

    class BM(BaseModel):
        flytefile: FlyteFile = Field(
            default_factory=lambda: FlyteFile(local_dummy_file)
        )
        flytedir: FlyteDirectory = Field(
            default_factory=lambda: FlyteDirectory(local_dummy_directory)
        )
        inner_bm: InnerBM = Field(default_factory=lambda: InnerBM())

    @task
    def t1(path: FlyteFile) -> FlyteFile:
        return path

    @task
    def t2(path: FlyteDirectory) -> FlyteDirectory:
        return path

    @workflow
    def wf(bm: BM) -> (FlyteFile, FlyteFile, FlyteDirectory, FlyteDirectory):
        f1 = t1(path=bm.flytefile)
        f2 = t1(path=bm.inner_bm.flytefile)
        d1 = t2(path=bm.flytedir)
        d2 = t2(path=bm.inner_bm.flytedir)
        return f1, f2, d1, d2

    o1, o2, o3, o4 = wf(bm=BM())
    with open(o1, "r") as fh:
        assert fh.read() == "Hello FlyteFile"

    with open(o2, "r") as fh:
        assert fh.read() == "Hello FlyteFile"

    with open(os.path.join(o3, "file"), "r") as fh:
        assert fh.read() == "Hello FlyteDirectory"

    with open(os.path.join(o4, "file"), "r") as fh:
        assert fh.read() == "Hello FlyteDirectory"


def test_all_types_in_pydantic_basemodel_wf(local_dummy_file, local_dummy_directory):
    class InnerBM(BaseModel):
        a: int = -1
        b: float = 2.1
        c: str = "Hello, Flyte"
        d: bool = False
        e: dict = Field(default_factory=lambda: {"key": "value"})
        f: FlyteFile = Field(default_factory=lambda: FlyteFile(local_dummy_file))
        g: FlyteDirectory = Field(
            default_factory=lambda: FlyteDirectory(local_dummy_directory)
        )
