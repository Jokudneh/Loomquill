from datetime import timedelta
from itertools import product

import pytest
from flyteidl.core.tasks_pb2 import ExtendedResources, TaskMetadata
from google.protobuf import text_format

from flytekit.core.resources import construct_extended_resources
import flytekit.models.interface as interface_models
import flytekit.models.literals as literal_models
from flytekit import Description, Documentation, SourceCode
from flytekit.extras.accelerators import T4
from flytekit.models import literals, task, types
from flytekit.models.core import identifier
from tests.flytekit.common import parameterizers


def test_resource_entry():
    obj = task.Resources.ResourceEntry(task.Resources.ResourceName.CPU, "blah")
    assert task.Resources.ResourceEntry.from_flyte_idl(obj.to_flyte_idl()) == obj
    assert obj != task.Resources.ResourceEntry(task.Resources.ResourceName.GPU, "blah")
    assert obj != task.Resources.ResourceEntry(task.Resources.ResourceName.CPU, "bloop")
    assert obj.name == task.Resources.ResourceName.CPU
    assert obj.value == "blah"


@pytest.mark.parametrize("resource_list", parameterizers.LIST_OF_RESOURCE_ENTRY_LISTS)
def test_resources(resource_list):
    obj = task.Resources(resource_list, resource_list)
    obj1 = task.Resources([], resource_list)
    obj2 = task.Resources(resource_list, [])

    assert obj.requests == obj2.requests
    assert obj.limits == obj1.limits
    assert obj == task.Resources.from_flyte_idl(obj.to_flyte_idl())


def test_runtime_metadata():
    obj = task.RuntimeMetadata(task.RuntimeMetadata.RuntimeType.FLYTE_SDK, "1.0.0", "python")
    assert obj.type == task.RuntimeMetadata.RuntimeType.FLYTE_SDK
    assert obj.version == "1.0.0"
    assert obj.flavor == "python"
    assert obj == task.RuntimeMetadata.from_flyte_idl(obj.to_flyte_idl())
    assert obj != task.RuntimeMetadata(task.RuntimeMetadata.RuntimeType.FLYTE_SDK, "1.0.1", "python")
    assert obj != task.RuntimeMetadata(task.RuntimeMetadata.RuntimeType.OTHER, "1.0.0", "python")
    assert obj != task.RuntimeMetadata(task.RuntimeMetadata.RuntimeType.FLYTE_SDK, "1.0.0", "golang")


def test_task_metadata_interruptible_from_flyte_idl():
    # Interruptible not set
    idl = TaskMetadata()
    obj = task.TaskMetadata.from_flyte_idl(idl)
    assert obj.interruptible is None

    idl = TaskMetadata()
    idl.interruptible = True
    obj = task.TaskMetadata.from_flyte_idl(idl)
    assert obj.interruptible is True

    idl = TaskMetadata()
    idl.interruptible = False
    obj = task.TaskMetadata.from_flyte_idl(idl)
    assert obj.interruptible is False


def test_task_metadata():
    obj = task.TaskMetadata(
        True,
        task.RuntimeMetadata(task.RuntimeMetadata.RuntimeType.FLYTE_SDK, "1.0.0", "python"),
        timedelta(days=1),
        literals.RetryStrategy(3),
        True,
        "0.1.1b0",
        "This is deprecated!",
        True,
        "A",
        (),
        k8s_object_metadata=task.K8sObjectMetadata(labels={"label": "foo"}, annotations={"anno": "bar"}),
    )

    assert obj.discoverable is True
    assert obj.retries.retries == 3
    assert obj.interruptible is True
    assert obj.timeout == timedelta(days=1)
    assert obj.runtime.flavor == "python"
    assert obj.runtime.type == task.RuntimeMetadata.RuntimeType.FLYTE_SDK
    assert obj.runtime.version == "1.0.0"
    assert obj.deprecated_error_message == "This is deprecated!"
    assert obj.discovery_version == "0.1.1b0"
    assert obj.pod_template_name == "A"
    assert obj.k8s_object_metadata.labels == {"label": "foo"}
    assert obj.k8s_object_metadata.annotations == {"anno": "bar"}
    assert obj == task.TaskMetadata.from_flyte_idl(obj.to_flyte_idl())


@pytest.mark.parametrize(
    "in_tuple",
    product(parameterizers.LIST_OF_TASK_METADATA, parameterizers.LIST_OF_INTERFACES, parameterizers.LIST_OF_RESOURCES),
)
def test_task_template(in_tuple):
    task_metadata, interfaces, resources = in_tuple
    obj = task.TaskTemplate(
        identifier.Identifier(identifier.ResourceType.TASK, "project", "domain", "name", "version"),
        "python",
        task_metadata,
        interfaces,
        {"a": 1, "b": {"c": 2, "d": 3}},
        container=task.Container(
            "my_image",
            ["this", "is", "a", "cmd"],
            ["this", "is", "an", "arg"],
            resources,
            {"a": "b"},
