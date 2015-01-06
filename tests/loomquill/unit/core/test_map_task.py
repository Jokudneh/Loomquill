import functools
import typing
from collections import OrderedDict

import pytest
from kubernetes.client import V1PodSpec, V1Container, V1EnvVar

import flytekit.configuration
from flytekit import LaunchPlan, Resources, PodTemplate
from flytekit.configuration import Image, ImageConfig
from flytekit.core.legacy_map_task import MapPythonTask, MapTaskResolver, map_task
from flytekit.core.task import TaskMetadata, task
from flytekit.core.workflow import workflow
from flytekit.tools.translator import get_serializable


@pytest.fixture
def serialization_settings():
    default_img = Image(name="default", fqn="test", tag="tag")
    return flytekit.configuration.SerializationSettings(
        project="project",
        domain="domain",
        version="version",
        env=None,
        image_config=ImageConfig(default_image=default_img, images=[default_img]),
    )


@task
def t1(a: int) -> typing.Optional[str]:
    b = a + 2
    return str(b)


@task(cache=True, cache_version="1")
def t2(a: int) -> str:
    b = a + 2
    return str(b)


@task(cache=True, cache_version="1")
def t3(a: int, b: str, c: float) -> str:
    return "hello"


# This test is for documentation.
def test_map_docs():
    # test_map_task_start
    @task
    def my_mappable_task(a: int) -> typing.Optional[str]:
        return str(a)

    @workflow
    def my_wf(x: typing.List[int]) -> typing.List[typing.Optional[str]]:
        return map_task(
            my_mappable_task,
            metadata=TaskMetadata(retries=1),
            concurrency=10,
            min_success_ratio=0.75,
        )(a=x).with_overrides(requests=Resources(cpu="10M"))

    # test_map_task_end

    res = my_wf(x=[1, 2, 3])
    assert res == ["1", "2", "3"]


def test_map_task_types():
    strs = map_task(t1, metadata=TaskMetadata(retries=1))(a=[5, 6])
    assert strs == ["7", "8"]

    with pytest.raises(TypeError):
        _ = map_task(t1, metadata=TaskMetadata(retries=1))(a=1)

