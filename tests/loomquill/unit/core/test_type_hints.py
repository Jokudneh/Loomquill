import dataclasses
import datetime
import functools
import os
import random
import re
import sys
import tempfile
import typing
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum

import msgpack
import pytest
from dataclasses_json import DataClassJsonMixin
from google.protobuf.struct_pb2 import Struct
from typing_extensions import Annotated, get_origin

import flytekit
import flytekit.configuration
from flytekit import Secret, SQLTask, dynamic, kwtypes, map_task
from flytekit.configuration import FastSerializationSettings, Image, ImageConfig
from flytekit.core import context_manager, launch_plan, promise
from flytekit.core.condition import conditional
from flytekit.core.constants import MESSAGEPACK
from flytekit.core.context_manager import ExecutionState
from flytekit.core.data_persistence import FileAccessProvider, flyte_tmp_dir
from flytekit.core.hash import HashMethod
from flytekit.core.node import Node
from flytekit.core.promise import NodeOutput, Promise, VoidPromise
from flytekit.core.resources import Resources
from flytekit.core.task import TaskMetadata, task
from flytekit.core.testing import patch, task_mock
from flytekit.core.type_engine import (
    RestrictedTypeError,
    SimpleTransformer,
    TypeEngine,
    TypeTransformerFailedError,
)
from flytekit.core.workflow import workflow
from flytekit.exceptions.user import (
    FlyteFailureNodeInputMismatchException,
    FlyteValidationException,
    FlyteMissingTypeException,
)
from flytekit.models import literals as _literal_models
from flytekit.models.core import types as _core_types
from flytekit.models.interface import Parameter
from flytekit.models.literals import Binary
from flytekit.models.task import Resources as _resource_models
from flytekit.models.types import LiteralType, SimpleType
from flytekit.tools.translator import get_serializable
from flytekit.types.directory import FlyteDirectory, TensorboardLogs
from flytekit.types.error import FlyteError
from flytekit.types.file import FlyteFile
from flytekit.types.pickle.pickle import FlytePickleTransformer
from flytekit.types.schema import FlyteSchema, SchemaOpenMode
from flytekit.types.structured.structured_dataset import StructuredDataset

serialization_settings = flytekit.configuration.SerializationSettings(
    project="proj",
    domain="dom",
    version="123",
    image_config=ImageConfig(Image(name="name", fqn="asdf/fdsa", tag="123")),
    env={},
)


def test_default_wf_params_works():
    @task
    def my_task(a: int):
        wf_params = flytekit.current_context()
        assert str(wf_params.execution_id) == "ex:local:local:local"
        assert flyte_tmp_dir in wf_params.raw_output_prefix

    my_task(a=3)
    assert context_manager.FlyteContextManager.size() == 1


def test_simple_input_output():
    @task
    def my_task(a: int) -> typing.NamedTuple("OutputsBC", b=int, c=str):
        ctx = flytekit.current_context()
        assert str(ctx.execution_id) == "ex:local:local:local"
        return a + 2, "hello world"

    assert my_task(a=3) == (5, "hello world")
    assert context_manager.FlyteContextManager.size() == 1


def test_forwardref_namedtuple_output():
    # This test case tests typing.NamedTuple outputs for cases where eg.
    # from __future__ import annotations is enabled, such that all type hints become ForwardRef
    @task
    def my_task(
        a: int,
    ) -> typing.NamedTuple(
        "OutputsBC", b=typing.ForwardRef("int"), c=typing.ForwardRef("str")
    ):
        ctx = flytekit.current_context()
        assert str(ctx.execution_id) == "ex:local:local:local"
        return a + 2, "hello world"

    assert my_task(a=3) == (5, "hello world")
    assert context_manager.FlyteContextManager.size() == 1


def test_annotated_namedtuple_output():
    @task
    def my_task(a: int) -> typing.NamedTuple("OutputA", a=Annotated[int, "metadata-a"]):
        return a + 2

    assert my_task(a=9) == (11,)
    assert get_origin(my_task.python_interface.outputs["a"]) is Annotated


def test_simple_input_no_output():
    @task
    def my_task(a: int):
        pass

    assert my_task(a=3) is None

    ctx = context_manager.FlyteContextManager.current_context()
    with context_manager.FlyteContextManager.with_context(
        ctx.with_new_compilation_state()
    ) as ctx:
        outputs = my_task(a=3)
        assert isinstance(outputs, VoidPromise)

    assert context_manager.FlyteContextManager.size() == 1


def test_transformer_override():
    tf = FlytePickleTransformer()

    @task
    def my_task() -> Annotated[str, tf]:
        return "Hello world"

    @workflow
    def wf() -> FlyteFile:
        return my_task()

    annotated_output = wf()

    @task
    def my_task_any() -> typing.Any:
        return "Hello world"

    @workflow
    def wf_any() -> FlyteFile:
        return my_task_any()

    any_output = wf_any()

    with open(annotated_output, "rb") as fh:
        contents_annotated = fh.read()

    with open(any_output, "rb") as fh:
        contents_any = fh.read()
    assert contents_annotated == contents_any


def test_single_output():
    @task
    def my_task() -> str:
        return "Hello world"

    assert my_task() == "Hello world"

    ctx = context_manager.FlyteContextManager.current_context()
    with context_manager.FlyteContextManager.with_context(
        ctx.with_new_compilation_state()
    ) as ctx:
        outputs = my_task()
        assert ctx.compilation_state is not None
        nodes = ctx.compilation_state.nodes
        assert len(nodes) == 1
        assert outputs.is_ready is False
        assert outputs.ref.node is nodes[0]

    assert context_manager.FlyteContextManager.size() == 1


def test_missing_output():
    @workflow
    def wf() -> str:
        return None  # type: ignore

    with pytest.raises(FlyteValidationException, match="Failed to bind output"):
        wf.compile()


def test_engine_file_output():
    basic_blob_type = _core_types.BlobType(
        format="",
        dimensionality=_core_types.BlobType.BlobDimensionality.SINGLE,
    )

    fs = FileAccessProvider(
        local_sandbox_dir="/tmp/flytetesting", raw_output_prefix="/tmp/flyteraw"
    )
    ctx = context_manager.FlyteContextManager.current_context()

    with context_manager.FlyteContextManager.with_context(
        ctx.with_file_access(fs)
    ) as ctx:
        # Write some text to a file not in that directory above
        test_file_location = "/tmp/sample.txt"
        with open(test_file_location, "w") as fh:
            fh.write("Hello World\n")

        lit = TypeEngine.to_literal(
            ctx, test_file_location, os.PathLike, LiteralType(blob=basic_blob_type)
        )

        # Since we're using local as remote, we should be able to just read the file from the 'remote' location.
        with open(lit.scalar.blob.uri, "r") as fh:
            assert fh.readline() == "Hello World\n"

        # We should also be able to turn the thing back into regular python native thing.
        redownloaded_local_file_location = TypeEngine.to_python_value(
            ctx, lit, os.PathLike
        )
        with open(redownloaded_local_file_location, "r") as fh:
            assert fh.readline() == "Hello World\n"

    assert context_manager.FlyteContextManager.size() == 1


def test_wf1():
    @task
    def t1(a: int) -> typing.NamedTuple("OutputsBC", t1_int_output=int, c=str):
        return a + 2, "world"

    @task
    def t2(a: str, b: str) -> str:
        return b + a

    @workflow
    def my_wf(a: int, b: str) -> (int, str):
        x, y = t1(a=a)
        d = t2(a=y, b=b)
        return x, d

    assert len(my_wf.nodes) == 2
    assert my_wf._nodes[0].id == "n0"
    assert my_wf._nodes[1]._upstream_nodes[0] is my_wf._nodes[0]

    assert len(my_wf.output_bindings) == 2
    assert my_wf._output_bindings[0].var == "o0"
    assert my_wf._output_bindings[0].binding.promise.var == "t1_int_output"

    nt = typing.NamedTuple("SingleNT", [("t1_int_output", float)])

    @task
    def t3(a: int) -> nt:
        return nt(a + 2)

    assert t3.python_interface.output_tuple_name == "SingleNT"
    assert t3.interface.outputs["t1_int_output"] is not None
    assert context_manager.FlyteContextManager.size() == 1


def test_wf1_run():
    @task
    def t1(a: int) -> typing.NamedTuple("OutputsBC", t1_int_output=int, c=str):
        return a + 2, "world"

    @task
    def t2(a: str, b: str) -> str:
        return b + a

    @workflow
    def my_wf(a: int, b: str) -> (int, str):
        x, y = t1(a=a)
        d = t2(a=y, b=b)
        return x, d

    x = my_wf(a=5, b="hello ")
    assert x == (7, "hello world")

    @workflow
    def my_wf2(a: int, b: str) -> (int, str):
        tup = t1(a=a)
        d = t2(a=tup.c, b=b)
        return tup.t1_int_output, d

    x = my_wf2(a=5, b="hello ")
    assert x == (7, "hello world")
    assert context_manager.FlyteContextManager.size() == 1


def test_wf1_with_overrides():
    @task
    def t1(a: int) -> typing.NamedTuple("OutputsBC", t1_int_output=int, c=str):
        return a + 2, "world"

    @task
    def t2(a: str, b: str) -> str:
        return b + a

    @workflow
    def my_wf(a: int, b: str) -> (int, str):
        x, y = t1(a=a).with_overrides(name="x")
        d = t2(a=y, b=b).with_overrides()
        return x, d

    x = my_wf(a=5, b="hello ")
    assert x == (7, "hello world")
    assert context_manager.FlyteContextManager.size() == 1


def test_wf1_with_list_of_inputs():
    @task
    def t1(a: int) -> typing.NamedTuple("OutputsBC", t1_int_output=int, c=str):
        return a + 2, "world"

    @task
    def t2(a: typing.List[str]) -> str:
        return " ".join(a)

    @workflow
    def my_wf(a: int, b: str) -> (int, str):
        xx, yy = t1(a=a)
        d = t2(a=[b, yy])
        return xx, d

    x = my_wf(a=5, b="hello")
    assert x == (7, "hello world")

    @workflow
    def my_wf2(a: int, b: str) -> int:
        x, y = t1(a=a)
        t2(a=[b, y])
        return x

    x = my_wf2(a=5, b="hello")
    assert x == 7
    assert context_manager.FlyteContextManager.size() == 1


def test_wf_output_mismatch():
    with pytest.raises(AssertionError):

        @workflow
        def my_wf(a: int, b: str) -> (int, str):
            return a

        my_wf()

    with pytest.raises(AssertionError):

        @workflow
        def my_wf2(a: int, b: str) -> int:
            return a, b  # type: ignore

        my_wf2()

    with pytest.raises(AssertionError):

        @workflow
        def my_wf3(a: int, b: str) -> int:
            return (a,)  # type: ignore

        my_wf3()

    assert context_manager.FlyteContextManager.size() == 1


def test_promise_return():
    """
    Testing that when a workflow is local executed but a local wf execution context already exists, Promise objects
    are returned wrapping Flyte literals instead of the unpacked dict.
    """

    @task
    def t1(a: int) -> typing.NamedTuple("OutputsBC", t1_int_output=int, c=str):
        a = a + 2
        return a, "world-" + str(a)

    @workflow
    def mimic_sub_wf(a: int) -> (str, str):
        x, y = t1(a=a)
        u, v = t1(a=x)
        return y, v

    ctx = context_manager.FlyteContextManager.current_context()

    with context_manager.FlyteContextManager.with_context(
        ctx.with_execution_state(
            ctx.new_execution_state().with_params(
                mode=ExecutionState.Mode.LOCAL_WORKFLOW_EXECUTION
            )
        )
    ) as ctx:
        a, b = mimic_sub_wf(a=3)

    assert isinstance(a, promise.Promise)
    assert isinstance(b, promise.Promise)
    assert a.val.scalar.value.string_value == "world-5"
    assert b.val.scalar.value.string_value == "world-7"
    assert context_manager.FlyteContextManager.size() == 1


@pytest.mark.skipif("pandas" not in sys.modules, reason="Pandas is not installed.")
def test_wf1_with_sql():
    import pandas as pd

    sql = SQLTask(
        "my-query",
        query_template="SELECT * FROM hive.city.fact_airport_sessions WHERE ds = '{{ .Inputs.ds }}' LIMIT 10",
        inputs=kwtypes(ds=datetime.datetime),
        outputs=kwtypes(results=FlyteSchema),
        metadata=TaskMetadata(retries=2),
    )

    @task
    def t1() -> datetime.datetime:
        return datetime.datetime.now()

    @workflow
    def my_wf() -> FlyteSchema:
        dt = t1()
        return sql(ds=dt)

    with task_mock(sql) as mock:
        mock.return_value = pd.DataFrame(data={"x": [1, 2], "y": ["3", "4"]})
        assert (
            (my_wf().open().all() == pd.DataFrame(data={"x": [1, 2], "y": ["3", "4"]}))
            .all()
            .all()
        )
    assert context_manager.FlyteContextManager.size() == 1


@pytest.mark.skipif("pandas" not in sys.modules, reason="Pandas is not installed.")
def test_wf1_with_sql_with_patch():
    import pandas as pd

    sql = SQLTask(
        "my-query",
        query_template="SELECT * FROM hive.city.fact_airport_sessions WHERE ds = '{{ .Inputs.ds }}' LIMIT 10",
        inputs=kwtypes(ds=datetime.datetime),
        outputs=kwtypes(results=FlyteSchema),
        metadata=TaskMetadata(retries=2),
    )

    @task
    def t1() -> datetime.datetime:
        return datetime.datetime.now()

    @workflow
    def my_wf() -> FlyteSchema:
        dt = t1()
        return sql(ds=dt)

    @patch(sql)
    def test_user_demo_test(mock_sql):
        mock_sql.return_value = pd.DataFrame(data={"x": [1, 2], "y": ["3", "4"]})
        assert (
            (my_wf().open().all() == pd.DataFrame(data={"x": [1, 2], "y": ["3", "4"]}))
            .all()
            .all()
        )

    # Have to call because tests inside tests don't run
    test_user_demo_test()
    assert context_manager.FlyteContextManager.size() == 1


def test_flyte_file_in_dataclass():
    @dataclass
    class InnerFileStruct(DataClassJsonMixin):
        a: FlyteFile
        b: FlyteFile

    @dataclass
    class FileStruct(DataClassJsonMixin):
        a: FlyteFile
        b: InnerFileStruct

    @task
    def t1(path: str) -> FileStruct:
        file = FlyteFile(path)
        fs = FileStruct(a=file, b=InnerFileStruct(a=file, b=FlyteFile(path)))
        return fs

    @dynamic
    def dyn(fs: FileStruct):
        t2(fs=fs)
        t3(fs=fs)

    @task
    def t2(fs: FileStruct) -> os.PathLike:
        assert fs.a.remote_source == "s3://somewhere"
        assert fs.b.a.remote_source == "s3://somewhere"
        assert fs.b.b.remote_source == "s3://somewhere"
        assert flyte_tmp_dir in fs.a.path
        assert flyte_tmp_dir in fs.b.a.path
        assert flyte_tmp_dir in fs.b.b.path

        os.makedirs(os.path.dirname(fs.a.path), exist_ok=True)
        with open(fs.a.path, "w") as file1:
            file1.write("hello world")

        return fs.a.path

    @task
    def t3(fs: FileStruct) -> FlyteFile:
        return fs.a

    @workflow
    def wf(path: str) -> (os.PathLike, FlyteFile):
        n1 = t1(path=path)
        dyn(fs=n1)
        return t2(fs=n1), t3(fs=n1)

    assert flyte_tmp_dir in wf(path="s3://somewhere")[0].path
    assert flyte_tmp_dir in wf(path="s3://somewhere")[1].path
    assert "s3://somewhere" == wf(path="s3://somewhere")[1].remote_source


def test_flyte_directory_in_dataclass():
    @dataclass
    class InnerFileStruct(DataClassJsonMixin):
        a: FlyteDirectory
        b: TensorboardLogs

    @dataclass
    class FileStruct(DataClassJsonMixin):
        a: FlyteDirectory
        b: InnerFileStruct

    @task
    def t1(path: str) -> FileStruct:
