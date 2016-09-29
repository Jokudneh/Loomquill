import dataclasses
import os
import typing
from collections import OrderedDict

import mock
import pytest

import flytekit.configuration
from flytekit import ContainerTask, ImageSpec, LaunchPlan, kwtypes
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.array_node_map_task import map_task
from flytekit.core.condition import conditional
from flytekit.core.dynamic_workflow_task import dynamic
from flytekit.core.options import Options
from flytekit.core.python_auto_container import get_registerable_container_image
from flytekit.core.resources import Resources, ResourceSpec
from flytekit.core.task import eager, task
from flytekit.core.workflow import workflow
from flytekit.exceptions.user import FlyteAssertion, FlyteMissingTypeException
from flytekit.image_spec.image_spec import ImageBuildEngine
from flytekit.models import task as task_models
from flytekit.models.admin.workflow import WorkflowSpec
from flytekit.models.literals import (
    BindingData,
    BindingDataCollection,
    BindingDataMap,
    Literal,
    Primitive,
    Scalar,
    Union,
    Void,
)
from flytekit.models.security import Identity, Secret, SecurityContext
from flytekit.models.types import LiteralType, SimpleType, TypeStructure, UnionType
from flytekit.tools.translator import get_serializable
from flytekit.types.error.error import FlyteError

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = flytekit.configuration.SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


def test_serialization():
    square = ContainerTask(
        name="square",
        input_data_dir="/var/inputs",
        output_data_dir="/var/outputs",
        inputs=kwtypes(val=int),
        outputs=kwtypes(out=int),
        image="alpine",
        environment={"a": "b"},
        command=["sh", "-c", "echo $(( {{.Inputs.val}} * {{.Inputs.val}} )) | tee /var/outputs/out"],
    )

    sum = ContainerTask(
        name="sum",
        input_data_dir="/var/flyte/inputs",
        output_data_dir="/var/flyte/outputs",
        inputs=kwtypes(x=int, y=int),
        outputs=kwtypes(out=int),
        image="alpine",
        command=["sh", "-c", "echo $(( {{.Inputs.x}} + {{.Inputs.y}} )) | tee /var/flyte/outputs/out"],
    )

    @task()
    def clean_up(val1: int, val2: int, err: typing.Optional[FlyteError] = None):
        print("Deleting the cluster")

    @workflow(on_failure=clean_up)
    def subwf(val1: int, val2: int) -> int:
        return sum(x=square(val=val1), y=square(val=val2))

    @workflow(on_failure=clean_up)
    def raw_container_wf(val1: int, val2: int) -> int:
        subwf(val1=val1, val2=val2)
        return sum(x=square(val=val1), y=square(val=val2))

    default_img = Image(name="default", fqn="test", tag="tag")
    serialization_settings = flytekit.configuration.SerializationSettings(
        project="project",
        domain="domain",
        version="version",
        env=None,
        image_config=ImageConfig(default_image=default_img, images=[default_img]),
    )
    wf_spec = typing.cast(WorkflowSpec, get_serializable(OrderedDict(), serialization_settings, raw_container_wf))
    assert wf_spec is not None
    assert wf_spec.template is not None
    assert len(wf_spec.template.nodes) == 4
    assert wf_spec.template.failure_node is not None
    assert wf_spec.template.failure_node.task_node is not None
    assert wf_spec.template.failure_node.id == "fn0"
    assert wf_spec.sub_workflows[0].failure_node is not None
    sqn_spec = get_serializable(OrderedDict(), serialization_settings, square)
    assert sqn_spec.template.container.image == "alpine"
    sum_spec = get_serializable(OrderedDict(), serialization_settings, sum)
    assert sum_spec.template.container.image == "alpine"


def test_serialization_branch_complex():
    @task
    def t1(a: int) -> typing.NamedTuple("OutputsBC", t1_int_output=int, c=str):
        return a + 2, "world"

    @task
    def t2(a: str) -> str:
        return a

    @workflow
    def my_wf(a: int, b: str) -> (int, str):
        x, y = t1(a=a)
        d = (
            conditional("test1")
            .if_(x == 4)
            .then(t2(a=b))
            .elif_(x >= 5)
            .then(t2(a=y))
            .else_()
            .fail("Unable to choose branch")
        )
        f = conditional("test2").if_(d == "hello ").then(t2(a="It is hello")).else_().then(t2(a="Not Hello!"))
        return x, f

    wf_spec = get_serializable(OrderedDict(), serialization_settings, my_wf)
    assert wf_spec is not None
    assert len(wf_spec.template.nodes) == 3
    assert wf_spec.template.nodes[1].branch_node is not None
    assert wf_spec.template.nodes[2].branch_node is not None


def test_serialization_branch_sub_wf():
    @task
    def t1(a: int) -> int:
        return a + 2

    @workflow
    def my_sub_wf(a: int) -> int:
        return t1(a=a)

    @workflow
    def my_wf(a: int) -> int:
        d = conditional("test1").if_(a > 3).then(t1(a=a)).else_().then(my_sub_wf(a=a))
        return d

    wf_spec = get_serializable(OrderedDict(), serialization_settings, my_wf)
    assert wf_spec is not None
    assert len(wf_spec.template.nodes[0].inputs) == 1
    assert wf_spec.template.nodes[0].inputs[0].var == ".a"
    assert wf_spec.template.nodes[0] is not None


def test_serialization_branch_compound_conditions():
    @task
    def t1(a: int) -> int:
        return a + 2

    @workflow
    def my_wf(a: int) -> int:
        d = (
            conditional("test1")
            .if_((a == 4) | (a == 3))
            .then(t1(a=a))
            .elif_(a < 6)
            .then(t1(a=a))
            .else_()
            .fail("Unable to choose branch")
        )
        return d

    default_img = Image(name="default", fqn="test", tag="tag")
    serialization_settings = flytekit.configuration.SerializationSettings(
        project="project",
        domain="domain",
        version="version",
        env=None,
        image_config=ImageConfig(default_image=default_img, images=[default_img]),
    )
    wf_spec = get_serializable(OrderedDict(), serialization_settings, my_wf)
    assert wf_spec is not None
    assert len(wf_spec.template.nodes[0].inputs) == 1
    assert wf_spec.template.nodes[0].inputs[0].var == ".a"


def test_serialization_branch_complex_2():
    @task
    def t1(a: int) -> typing.NamedTuple("OutputsBC", t1_int_output=int, c=str):
        return a + 2, "world"

    @task
    def t2(a: str) -> str:
        return a

    @workflow
    def my_wf(a: int, b: str) -> (int, str):
        x, y = t1(a=a)
        d = (
            conditional("test1")
            .if_(x == 4)
            .then(t2(a=b))
            .elif_(x >= 5)
            .then(t2(a=y))
            .else_()
            .fail("Unable to choose branch")
        )
        f = conditional("test2").if_(d == "hello ").then(t2(a="It is hello")).else_().then(t2(a="Not Hello!"))
