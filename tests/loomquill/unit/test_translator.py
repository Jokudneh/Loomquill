import typing
from collections import OrderedDict

import pytest
from kubernetes import client
from kubernetes.client import V1Container, V1PodSpec

import flytekit.configuration
from flytekit import ContainerTask, PodTemplate, Resources, map_task
from flytekit.configuration import FastSerializationSettings, Image, ImageConfig
from flytekit.core.base_task import kwtypes
from flytekit.core.launch_plan import LaunchPlan, ReferenceLaunchPlan
from flytekit.core.reference_entity import ReferenceSpec, ReferenceTemplate
from flytekit.core.task import ReferenceTask, task
from flytekit.core.workflow import ReferenceWorkflow, workflow
from flytekit.deck import Deck
from flytekit.models.core import identifier as identifier_models
from flytekit.models.task import Resources as resource_model
from flytekit.tools.translator import get_serializable

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = flytekit.configuration.SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


def test_references():
    rlp = ReferenceLaunchPlan("media", "stg", "some.name", "cafe", inputs=kwtypes(in1=str), outputs=kwtypes())
    lp_model = get_serializable(OrderedDict(), serialization_settings, rlp)
    assert isinstance(lp_model, ReferenceSpec)
    assert isinstance(lp_model.template, ReferenceTemplate)
    assert lp_model.template.id == rlp.reference.id
    assert lp_model.template.resource_type == identifier_models.ResourceType.LAUNCH_PLAN

    rt = ReferenceTask("media", "stg", "some.name", "cafe", inputs=kwtypes(in1=str), outputs=kwtypes())
    task_spec = get_serializable(OrderedDict(), serialization_settings, rt)
    assert isinstance(task_spec, ReferenceSpec)
    assert isinstance(task_spec.template, ReferenceTemplate)
    assert task_spec.template.id == rt.reference.id
    assert task_spec.template.resource_type == identifier_models.ResourceType.TASK

    rw = ReferenceWorkflow("media", "stg", "some.name", "cafe", inputs=kwtypes(in1=str), outputs=kwtypes())
    wf_spec = get_serializable(OrderedDict(), serialization_settings, rw)
    assert isinstance(wf_spec, ReferenceSpec)
    assert isinstance(wf_spec.template, ReferenceTemplate)
    assert wf_spec.template.id == rw.reference.id
    assert wf_spec.template.resource_type == identifier_models.ResourceType.WORKFLOW


def test_basics():
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

