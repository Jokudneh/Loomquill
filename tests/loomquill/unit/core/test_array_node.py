import typing
from collections import OrderedDict

import pytest
from flyteidl.core import workflow_pb2 as _core_workflow

from flytekit import task, workflow
from flytekit.core.context_manager import FlyteContextManager
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.array_node import array_node
from flytekit.core.array_node_map_task import map_task
from flytekit.core.launch_plan import LaunchPlan, reference_launch_plan
from flytekit.models import types
from flytekit.models.core import identifier as identifier_models
from flytekit.models.literals import BindingData, Literal, LiteralMap, Primitive, Scalar, Union
from flytekit.remote import FlyteLaunchPlan
from flytekit.remote.interface import TypedInterface
from flytekit.tools.translator import gather_dependent_entities, get_serializable


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


@task
def return_one() -> int:
    return 1


@task
def return_two() -> int:
    return 2


@task
def multiply(val: int, val1: typing.Union[int, str], val2: int) -> int:
    if type(val1) is str:
        return val * val2
    return val * int(val1) * val2


@workflow
def parent_wf(a: int, b: typing.Union[int, str], c: int = 2) -> int:
    return multiply(val=a, val1=b, val2=c)


ctx = FlyteContextManager.current_context()
lp = LaunchPlan.get_default_launch_plan(ctx, parent_wf)
lp_fixed_inputs = LaunchPlan.get_or_create(
    name="parent_wf_lp_fixed_inputs", workflow=parent_wf, fixed_inputs={"a": 1}
)


@reference_launch_plan(project="project", domain="domain", name="tests.flytekit.unit.core.test_array_node.parent_wf", version="version")
def ref_lp(a: int, b: typing.Union[int, str], c: int = 2) -> int:
    ...


@reference_launch_plan(project="project", domain="domain", name="parent_wf_lp_fixed_inputs", version="version")
def ref_lp_fixed_inputs(b: typing.Union[int, str], c: int = 2) -> int:
    ...


def get_grandparent_wf(serialization_settings):
    @workflow
    def grandparent_wf() -> typing.List[int]:
        return map_task(lp, concurrency=10, min_success_ratio=0.9)(a=[1, 3, 5], b=["two", 4, "six"], c=[7, 8, 9])

    return grandparent_wf


def get_grandparent_wf_ref_lp(serialization_settings):
    @workflow
    def grandparent_wf_ref_lp() -> typing.List[int]:
        return map_task(ref_lp, concurrency=10, min_success_ratio=0.9)(a=[1, 3, 5], b=["two", 4, "six"], c=[7, 8, 9])

    return grandparent_wf_ref_lp


def get_grandparent_wf_ref_lp_fixed_inputs(serialization_settings):
    @workflow
    def grandparent_wf_ref_lp_fixed_inputs() -> typing.List[int]:
        return map_task(ref_lp_fixed_inputs, concurrency=10, min_success_ratio=0.9)(b=["two", 4, "six"], c=[7, 8, 9])

    return grandparent_wf_ref_lp_fixed_inputs


def get_grandparent_wf_fixed_inputs(serialization_settings):
    @workflow
    def grandparent_wf_fixed_inputs() -> typing.List[int]:
        return map_task(lp_fixed_inputs, concurrency=10, min_success_ratio=0.9)(b=["two", 4, "six"], c=[7, 8, 9])

    return grandparent_wf_fixed_inputs


def get_grandparent_wf_upstream_input(serialization_settings):
    @workflow
    def grandparent_wf() -> typing.List[int]:
        one = return_one()
        return map_task(lp, concurrency=10, min_success_ratio=0.9)(a=[one, 3, 5], b=["two", 4, "six"], c=[7, 8, 9])

    return grandparent_wf


def get_grandparent_wf_with_overrides(serialization_settings):
    @workflow
    def grandparent_wf_with_overrides() -> typing.List[int]:
        return map_task(lp, concurrency=10, min_success_ratio=0.9)(
            a=[1, 3, 5], b=["two", 4, "six"], c=[7, 8, 9]
        ).with_overrides(cache=True, cache_version="1.0")

    return grandparent_wf_with_overrides


def get_grandparent_remote_wf(serialization_settings):
    serialized = OrderedDict()
    lp_model = get_serializable(serialized, serialization_settings, lp)

    task_templates, wf_specs, lp_specs = gather_dependent_entities(serialized)
