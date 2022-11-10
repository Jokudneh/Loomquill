import typing
from collections import OrderedDict

import cloudpickle
import mock
import pytest
import sys

import flytekit.configuration
from flytekit.configuration import Image, ImageConfig
from flytekit.core.base_task import TaskResolverMixin
from flytekit.core.class_based_resolver import ClassStorageTaskResolver
from flytekit.core.python_auto_container import default_task_resolver, default_notebook_task_resolver, PickledEntity, PickledEntityMetadata
from flytekit.core.task import task
from flytekit.core.workflow import workflow
from flytekit.tools.translator import get_serializable

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = flytekit.configuration.SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


@workflow
def my_wf(a: int, b: str) -> typing.Tuple[int, str]:
    @task
    def t1(a: int) -> typing.Tuple[int, str]:
        return a + 2, "world"

    @task
    def t2(a: str, b: str) -> str:
        return b + a

