from collections import OrderedDict
from unittest.mock import patch, MagicMock, mock_open
import pytest
from flytekitplugins.k8sdataservice.task import DataServiceConfig, DataServiceTask
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct
from flytekit import kwtypes, Resources
from flytekit.configuration import ImageConfig, SerializationSettings
from flytekit.extend import get_serializable


@pytest.fixture
def mock_k8s_manager():
    with patch('flytekitplugins.k8sdataservice.connector.K8sManager') as MockK8sManager:
        mock_k8s_manager = MagicMock()
        MockK8sManager.return_value = mock_k8s_manager
        yield mock_k8s_manager


def test_gnn_task():
    gnn_config = DataServiceConfig(
        Name="test",
        Replicas=8,
        Image="image",
        Command=None,
        Cluster="grid2",
        Requests=Resources(cpu="1", mem="2", gpu="4"),
        Limits=Resources(cpu="1", mem="2", gpu="4"),
