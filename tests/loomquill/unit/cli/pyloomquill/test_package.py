import os
import shutil

from click.testing import CliRunner
from flyteidl.admin import task_pb2

import flytekit
import flytekit.clis.sdk_in_container.utils
import flytekit.configuration
import flytekit.tools.serialize_helpers
from flytekit import TaskMetadata
from flytekit.clis.sdk_in_container import pyflyte
from flytekit.core import context_manager
from flytekit.models.admin.workflow import WorkflowSpec
from flytekit.models.core.identifier import Identifier, ResourceType
from flytekit.models.launch_plan import LaunchPlan
from flytekit.models.task import TaskSpec
from flytekit.remote import FlyteTask
from flytekit.remote.interface import TypedInterface
from flytekit.remote.remote_callable import RemoteEntity

sample_file_contents = """
from flytekit import task, workflow

@task(cache=True, cache_version="1", retries=3)
def sum(x: int, y: int) -> int:
    return x + y

@task(cache=True, cache_version="1", retries=3)
def square(z: int) -> int:
    return z*z

@workflow
def my_workflow(x: int, y: int) -> int:
    return sum(x=square(z=x), y=square(z=y))
"""


@flytekit.task
def foo():
    pass


@flytekit.workflow
def wf():
    return foo()


def test_get_registrable_entities():
    ctx = context_manager.FlyteContextManager.current_context().with_serialization_settings(
        flytekit.configuration.SerializationSettings(
