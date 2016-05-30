import os
from datetime import timedelta

from flyteidl.core import compiler_pb2 as _compiler_pb2
from flyteidl.core import workflow_pb2 as _workflow_pb2

from flytekit.models import literals as _literals
from flytekit.models import task as _task_model
from flytekit.models.core import compiler as _compiler_model
from flytekit.models.core import workflow as _workflow_model


def get_sample_node_metadata(node_id):
    """
    :param Text node_id:
    :rtype: flytekit.models.core.workflow.NodeMetadata
    """

    return _workflow_model.NodeMetadata(name=node_id, timeout=timedelta(seconds=10), retries=_literals.RetryStrategy(0))


def get_sample_container():
    """
    :rtype: flytekit.models.task.Container
    """
    cpu_resource = _task_model.Resources.ResourceEntry(_task_model.Resources.ResourceName.CPU, "1")
    resources = _task_model.Resources(requests=[cpu_resource], limits=[cpu_resource])

    return _task_model.Container(
        "my_image",
        ["this", "is", "a", "cmd"],
        ["this", "is", "an", "arg"],
        resources,
