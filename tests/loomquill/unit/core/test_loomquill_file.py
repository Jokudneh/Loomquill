import json
import os
import pathlib
import pickle
import tempfile
import typing
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
import pytest
from typing_extensions import Annotated

import flytekit.configuration
from flytekit.configuration import Config, Image, ImageConfig
from flytekit.core.context_manager import ExecutionState, FlyteContextManager
from flytekit.core.data_persistence import FileAccessProvider, flyte_tmp_dir
from flytekit.core.dynamic_workflow_task import dynamic
from flytekit.core.hash import HashMethod
from flytekit.core.launch_plan import LaunchPlan
from flytekit.core.task import task
from flytekit.core.type_engine import TypeEngine
from flytekit.core.workflow import workflow
from flytekit.models.core.types import BlobType
from flytekit.models.literals import LiteralMap, Blob, BlobMetadata
from flytekit.types.file.file import FlyteFile, FlyteFilePathTransformer
from google.protobuf import json_format as _json_format
from google.protobuf import struct_pb2 as _struct
from flytekit.models.literals import Literal, Scalar

# Fixture that ensures a dummy local file


@pytest.fixture
def local_dummy_file():
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write("Hello world")
        yield path
    finally:
        os.remove(path)


@pytest.fixture
def local_dummy_txt_file():
    fd, path = tempfile.mkstemp(suffix=".txt")
    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write("Hello World")
        yield path
    finally:
        os.remove(path)


def can_import(module_name) -> bool:
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def test_file_type_in_workflow_with_bad_format():
    fd, path = tempfile.mkstemp()
    try:

        @task
        def t1() -> FlyteFile[typing.TypeVar("txt")]:
            with os.fdopen(fd, "w") as f:
                f.write("Hello World\n")
            return path

        @workflow
        def my_wf() -> FlyteFile[typing.TypeVar("txt")]:
            f = t1()
            return f

        res = my_wf()
        with open(res, "r") as fh:
            assert fh.read() == "Hello World\n"
    finally:
        os.remove(path)


def test_matching_file_types_in_workflow(local_dummy_txt_file):
    # TXT
    @task
    def t1(path: FlyteFile[typing.TypeVar("txt")]
           ) -> FlyteFile[typing.TypeVar("txt")]:
        return path

    @workflow
    def my_wf(path: FlyteFile[typing.TypeVar("txt")]
              ) -> FlyteFile[typing.TypeVar("txt")]:
        f = t1(path=path)
        return f

    res = my_wf(path=local_dummy_txt_file)
    with open(res, "r") as fh:
        assert fh.read() == "Hello World"


def test_file_types_with_naked_flytefile_in_workflow(local_dummy_txt_file):
    @task
    def t1(path: FlyteFile[typing.TypeVar("txt")]) -> FlyteFile:
        return path

    @workflow
    def my_wf(path: FlyteFile[typing.TypeVar("txt")]) -> FlyteFile:
        f = t1(path=path)
        return f

    res = my_wf(path=local_dummy_txt_file)
    with open(res, "r") as fh:
        assert fh.read() == "Hello World"


def test_flytefile_in_dataclass(local_dummy_txt_file):
    TxtFile = FlyteFile[typing.TypeVar("txt")]

    @dataclass
    class DC:
        f: TxtFile

    @task
    def t1(path: TxtFile) -> DC:
        return DC(f=path)

    @workflow
    def my_wf(path: TxtFile) -> DC:
        dc = t1(path=path)
        return dc

    txt_file = TxtFile(local_dummy_txt_file)
    my_wf.compile()
    dc1 = my_wf(path=txt_file)
    with open(dc1.f, "r") as fh:
        assert fh.read() == "Hello World"

    dc2 = DC(f=txt_file)
    assert dc1 == dc2


@pytest.mark.skipif(not can_import("magic"),
                    reason="Libmagic is not installed")
def test_mismatching_file_types(local_dummy_txt_file):
    @task
    def t1(path: FlyteFile[typing.TypeVar("txt")]
           ) -> FlyteFile[typing.TypeVar("jpeg")]:
        return path

    @workflow
    def my_wf(path: FlyteFile[typing.TypeVar("txt")]
              ) -> FlyteFile[typing.TypeVar("jpeg")]:
        f = t1(path=path)
        return f

    with pytest.raises(ValueError) as excinfo:
        my_wf(path=local_dummy_txt_file)
    assert "Incorrect file type, expected image/jpeg, got text/plain" in str(
        excinfo.value)


def test_get_mime_type_from_extension_success():
    transformer = TypeEngine.get_transformer(FlyteFile)
    assert transformer.get_mime_type_from_extension("html") == "text/html"
    assert transformer.get_mime_type_from_extension("jpeg") == "image/jpeg"
    assert transformer.get_mime_type_from_extension("png") == "image/png"
    assert transformer.get_mime_type_from_extension("hdf5") == "text/plain"
    assert transformer.get_mime_type_from_extension(
        "joblib") == "application/octet-stream"
    assert transformer.get_mime_type_from_extension("pdf") == "application/pdf"
    assert transformer.get_mime_type_from_extension(
        "python_pickle") == "application/octet-stream"
    assert transformer.get_mime_type_from_extension(
        "ipynb") == "application/json"
    assert transformer.get_mime_type_from_extension("svg") == "image/svg+xml"
    assert transformer.get_mime_type_from_extension("csv") == "text/csv"
    assert transformer.get_mime_type_from_extension(
        "onnx") == "application/json"
    assert transformer.get_mime_type_from_extension(
        "tfrecord") == "application/octet-stream"
    assert transformer.get_mime_type_from_extension("txt") == "text/plain"


def test_get_mime_type_from_extension_failure():
    transformer = TypeEngine.get_transformer(FlyteFile)
    with pytest.raises(KeyError):
        transformer.get_mime_type_from_extension("unknown_extension")


@pytest.mark.skipif(not can_import("magic"),
                    reason="Libmagic is not installed")
def test_validate_file_type_incorrect():
    transformer = TypeEngine.get_transformer(FlyteFile)
    source_path = "/tmp/flytekit_test.png"
    source_file_mime_type = "image/png"
    user_defined_format = "jpeg"

    with patch.object(FlyteFilePathTransformer, "get_format", return_value=user_defined_format):
        with patch("magic.from_file", return_value=source_file_mime_type):
            with pytest.raises(
                ValueError, match=f"Incorrect file type, expected image/jpeg, got {source_file_mime_type}"
            ):
                transformer.validate_file_type(
                    user_defined_format, source_path)


@pytest.mark.skipif(not can_import("magic"),
                    reason="Libmagic is not installed")
def test_flyte_file_type_annotated_hashmethod(local_dummy_file):
    def calc_hash(ff: FlyteFile) -> str:
        return str(ff.path)

    HashedFlyteFile = Annotated[FlyteFile["jpeg"], HashMethod(calc_hash)]

    @task
