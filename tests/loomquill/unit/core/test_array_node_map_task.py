import functools
from datetime import timedelta
import os
import tempfile
import typing
from collections import OrderedDict
from typing import List

import pytest
from flyteidl.core import workflow_pb2 as _core_workflow

from flytekit import dynamic, map_task, task, workflow, eager, PythonFunctionTask
from flytekit.configuration import FastSerializationSettings, Image, ImageConfig, SerializationSettings
from flytekit.core import context_manager
from flytekit.core.array_node_map_task import ArrayNodeMapTask, ArrayNodeMapTaskResolver
from flytekit.core.task import TaskMetadata
from flytekit.core.type_engine import TypeEngine
from flytekit.extras.accelerators import GPUAccelerator
from flytekit.models import types
from flytekit.models.literals import (
    BindingData,
    Literal,
    LiteralMap,
    LiteralOffloadedMetadata,
    Scalar,
    Primitive,
)
from flytekit.tools.translator import get_serializable
from flytekit.types.directory import FlyteDirectory


class PythonFunctionTaskExtension(PythonFunctionTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@pytest.fixture
def serialization_settings():
    default_img = Image(name="default", fqn="test", tag="tag")
    return SerializationSettings(
        project="project",
        domain="domain",
        version="version",
        env=None,
        image_config=ImageConfig(default_image=default_img, images=[default_img]),
    )


@pytest.fixture
def interactive_serialization_settings():
    default_img = Image(name="default", fqn="test", tag="tag")
    return SerializationSettings(
        project="project",
        domain="domain",
        version="version",
        env=None,
        image_config=ImageConfig(default_image=default_img, images=[default_img]),
        interactive_mode_enabled=True,
    )


def test_map(serialization_settings):
    @task
    def say_hello(name: str) -> str:
        return f"hello {name}!"

    @workflow
    def wf() -> List[str]:
        return map_task(say_hello)(name=["abc", "def"])

    res = wf()
    assert res is not None


def test_execution(serialization_settings):
    @task
    def say_hello(name: str) -> str:
        return f"hello {name}!"

    @task
    def create_input_list() -> List[str]:
        return ["earth", "mars"]

    @workflow
    def wf() -> List[str]:
        xs = map_task(say_hello)(name=create_input_list())
        return map_task(say_hello)(name=xs)

    assert wf() == ["hello hello earth!!", "hello hello mars!!"]


def test_remote_execution(serialization_settings):
    @task
    def say_hello(name: str) -> str:
        return f"hello {name}!"

    ctx = context_manager.FlyteContextManager.current_context()
    with context_manager.FlyteContextManager.with_context(
            ctx.with_execution_state(
                ctx.execution_state.with_params(mode=context_manager.ExecutionState.Mode.TASK_EXECUTION)
            )
    ) as ctx:
        t = map_task(say_hello)
        lm = TypeEngine.dict_to_literal_map(ctx, {"name": ["earth", "mars"]}, type_hints={"name": typing.List[str]})
        res = t.dispatch_execute(ctx, lm)
        assert len(res.literals) == 1
        assert res.literals["o0"].scalar.primitive.string_value == "hello earth!"


def test_map_task_with_pickle():
    @task
    def say_hello(name: typing.Any) -> str:
        return f"hello {name}!"

    map_task(say_hello)(name=["abc", "def"])


def test_serialization(serialization_settings):
    @task
    def t1(a: int) -> int:
        return a + 1

    arraynode_maptask = map_task(t1, metadata=TaskMetadata(retries=2))
    task_spec = get_serializable(OrderedDict(), serialization_settings, arraynode_maptask)

    assert task_spec.template.metadata.retries.retries == 2
    assert task_spec.template.type == "python-task"
    assert task_spec.template.task_type_version == 1
    assert task_spec.template.container.args == [
        "pyflyte-map-execute",
        "--inputs",
        "{{.input}}",
        "--output-prefix",
        "{{.outputPrefix}}",
        "--raw-output-data-prefix",
        "{{.rawOutputDataPrefix}}",
        "--checkpoint-path",
        "{{.checkpointOutputPrefix}}",
        "--prev-checkpoint",
        "{{.prevCheckpointPrefix}}",
        "--resolver",
        "flytekit.core.array_node_map_task.ArrayNodeMapTaskResolver",
        "--",
        "vars",
        "",
        "resolver",
        "flytekit.core.python_auto_container.default_task_resolver",
        "task-module",
        "tests.flytekit.unit.core.test_array_node_map_task",
        "task-name",
        "t1",
    ]


def test_fast_serialization(serialization_settings):
    serialization_settings.fast_serialization_settings = FastSerializationSettings(enabled=True)

    @task
    def t1(a: int) -> int:
        return a + 1

    arraynode_maptask = map_task(t1, metadata=TaskMetadata(retries=2))
    task_spec = get_serializable(OrderedDict(), serialization_settings, arraynode_maptask)

    assert task_spec.template.container.args == [
        "pyflyte-fast-execute",
        "--additional-distribution",
        "{{ .remote_package_path }}",
        "--dest-dir",
        "{{ .dest_dir }}",
        "--",
        "pyflyte-map-execute",
        "--inputs",
        "{{.input}}",
        "--output-prefix",
        "{{.outputPrefix}}",
        "--raw-output-data-prefix",
        "{{.rawOutputDataPrefix}}",
        "--checkpoint-path",
