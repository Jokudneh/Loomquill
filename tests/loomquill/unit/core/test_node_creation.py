import datetime
import typing
from collections import OrderedDict
from dataclasses import dataclass

import pytest
from kubernetes.client import V1PodSpec, V1Container, V1EnvVar

import flytekit.configuration
from flytekit import Resources, map_task, PodTemplate
from flytekit.configuration import Image, ImageConfig
from flytekit.core.cache import Cache
from flytekit.core.dynamic_workflow_task import dynamic
from flytekit.core.node_creation import create_node
from flytekit.core.task import task
from flytekit.core.workflow import workflow
from flytekit.exceptions.user import FlyteAssertion
from flytekit.extras.accelerators import A100, T4
from flytekit.image_spec.image_spec import ImageBuildEngine
from flytekit.models import literals as _literal_models
from flytekit.models.task import Resources as _resources_models
from flytekit.tools.translator import get_serializable


def test_normal_task(mock_image_spec_builder):
    ImageBuildEngine.register("test", mock_image_spec_builder)

    @task
    def t1(a: str) -> str:
        return a + " world"

    @dynamic
    def my_subwf(a: int) -> typing.List[str]:
        s = []
        for i in range(a):
            s.append(t1(a=str(i)))
        return s

    @workflow
    def my_wf(a: str) -> (str, typing.List[str]):
        t1_node = create_node(t1, a=a)
        dyn_node = create_node(my_subwf, a=3)
        return t1_node.o0, dyn_node.o0

    r, x = my_wf(a="hello")
    assert r == "hello world"
    assert x == ["0 world", "1 world", "2 world"]

    serialization_settings = flytekit.configuration.SerializationSettings(
        project="test_proj",
        domain="test_domain",
        version="abc",
        image_config=ImageConfig(Image(name="name", fqn="image", tag="name")),
        env={},
    )
    wf_spec = get_serializable(OrderedDict(), serialization_settings, my_wf)
    assert len(wf_spec.template.nodes) == 2
    assert len(wf_spec.template.outputs) == 2

    @task
    def t2():
        ...

    @task
    def t3():
        ...

    @workflow
    def empty_wf():
        t2_node = create_node(t2)
        t3_node = create_node(t3)
        t3_node.runs_before(t2_node)

    # Test that VoidPromises can handle runs_before
    empty_wf()

    @workflow
    def empty_wf2():
        t2_node = create_node(t2)
        t3_node = create_node(t3)
        t3_node >> t2_node

    serialization_settings = flytekit.configuration.SerializationSettings(
        project="test_proj",
        domain="test_domain",
        version="abc",
        image_config=ImageConfig(Image(name="name", fqn="image", tag="name")),
        env={},
    )
    wf_spec = get_serializable(OrderedDict(), serialization_settings, empty_wf)
    assert wf_spec.template.nodes[0].upstream_node_ids[0] == "n1"
    assert wf_spec.template.nodes[0].id == "n0"

    wf_spec = get_serializable(OrderedDict(), serialization_settings, empty_wf2)
    assert wf_spec.template.nodes[0].upstream_node_ids[0] == "n1"
    assert wf_spec.template.nodes[0].id == "n0"
    assert wf_spec.template.nodes[0].metadata.name == "t2"

    with pytest.raises(FlyteAssertion):

        @workflow
        def empty_wf2():
            create_node(t2, "foo")

        empty_wf2()


def test_more_normal_task():
    nt = typing.NamedTuple("OneOutput", t1_str_output=str)

    @task
    def t1(a: int) -> nt:
        # This one returns a regular tuple
        return nt(f"{a + 2}")  # type: ignore

    @task
    def t1_nt(a: int) -> nt:
        # This one returns an instance of the named tuple.
        return nt(f"{a + 2}")  # type: ignore

    @task
    def t2(a: typing.List[str]) -> str:
        return " ".join(a)

    @workflow
    def my_wf(a: int, b: str) -> (str, str):
        t1_node = create_node(t1, a=a).with_overrides(aliases={"t1_str_output": "foo"})
        t1_nt_node = create_node(t1_nt, a=a)
        t2_node = create_node(t2, a=[t1_node.t1_str_output, t1_nt_node.t1_str_output, b])
        return t1_node.t1_str_output, t2_node.o0
