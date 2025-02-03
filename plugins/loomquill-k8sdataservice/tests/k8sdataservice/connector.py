from datetime import timedelta
from unittest.mock import patch
from google.protobuf import json_format
from flytekitplugins.k8sdataservice.task import DataServiceConfig
from flytekitplugins.k8sdataservice.connector import DataServiceMetadata
from google.protobuf.struct_pb2 import Struct
from flyteidl.core.execution_pb2 import TaskExecution
import flytekit.models.interface as interface_models
from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models import literals, task, types
from flytekit.models.core.identifier import ResourceType
from flytekit.models.task import TaskTemplate


cmd = ["command", "args"]


def create_test_task_metadata() -> task.TaskMetadata:
    return task.TaskMetadata(
       discoverable= True,
        runtime=task.RuntimeMetadata(task.RuntimeMetadata.RuntimeType.FLYTE_SDK, "1.0.0", "python"),
        timeout=timedelta(days=1),
        retries=literals.RetryStrategy(3),
        interruptible=True,
        discovery_version="0.1.1b0",
        deprecated_error_message="This is deprecated!",
        cache_serializable=True,
        pod_template_name="A",
        cache_ignore_input_vars=(),
    )


def create_test_setup(original_name: str = "gnn-1234", existing_release_name: str = "gnn-2345"):
    task_id = Identifier(
        resource_type=ResourceType.TASK, project="project", domain="domain", name="name", version="version"
    )
    task_metadata = create_test_task_metadata()
    s = Struct()
    if existing_release_name != "":
        s.update({
            "Name": original_name,
            "Image": "image",
            "Command": cmd,
            "Cluster": "ei-dev2",
            "ExistingReleaseName": existing_release_name,
        })
    else:
        s.update({
            "Name": original_name,
            "Image": "image",
            "Command": cmd,
            "Cluster": "ei-dev2",
        })
    task_config = json_format.MessageToDict(s)
    return task_id, task_metadata, task_config


@patch("flytekitplugins.k8sdataservice.connector.K8sManager.create_data_service", return_value="gnn-1234")
@patch("flytekitplugins.k8sdataservice.connector.K8sManager.check_stateful_set_status", return_value="succeeded")
@patch("flytekitplugins.k8sdataservice.connector.K8sManager.delete_stateful_set")
@patch("flytekitplugins.k8sdataservice.connector.K8sManager.delete_service")
def test_gnn_connector(mock_delete_service, mock_delete_stateful_set, mock_check_status, mock_create_data_service):
