"""
Comprehensive tests for the Databricks per-project token support feature.

Tests cover:
- get_secret_from_k8s: Cross-namespace K8s secret reading
- get_databricks_token: Token resolution strategy (K8s -> env var fallback)
- get_header: Authorization header generation with token support
- DatabricksConnector.create/get/delete: Token persistence in job metadata
- DatabricksV2 task config: databricks_token_secret serialization
"""

import base64
import http
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from aioresponses import aioresponses
from flytekitplugins.spark.connector import (
    DATABRICKS_API_ENDPOINT,
    DatabricksJobMetadata,
    get_databricks_token,
    get_header,
    get_secret_from_k8s,
)

from flytekit.extend.backend.base_agent import AgentRegistry
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models import literals, task
from flytekit.models.core.identifier import ResourceType
from flytekit.models.task import Container, Resources, TaskExecutionMetadata, TaskTemplate

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def task_template() -> TaskTemplate:
    """Standard Databricks task template for testing."""
    task_id = Identifier(
        resource_type=ResourceType.TASK,
        project="project",
        domain="domain",
        name="name",
        version="version",
    )
    task_metadata = task.TaskMetadata(
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
    )
    task_config = {
        "sparkConf": {
            "spark.driver.memory": "1000M",
            "spark.executor.memory": "1000M",
            "spark.executor.cores": "1",
            "spark.executor.instances": "2",
            "spark.driver.cores": "1",
        },
        "mainApplicationFile": "dbfs:/entrypoint.py",
        "databricksConf": {
            "run_name": "flytekit databricks plugin example",
            "new_cluster": {
                "spark_version": "12.2.x-scala2.12",
                "node_type_id": "n2-highmem-4",
                "num_workers": 1,
            },
            "timeout_seconds": 3600,
            "max_retries": 1,
        },
    }
    container = Container(
        image="flyteorg/flytekit:databricks-0.18.0-py3.7",
        command=[],
        args=[
            "pyflyte-fast-execute",
            "--additional-distribution",
            "s3://my-s3-bucket/flytesnacks/development/24UYJEF2HDZQN3SG4VAZSM4PLI======/script_mode.tar.gz",
            "--dest-dir",
            "/root",
            "--",
            "pyflyte-execute",
            "--inputs",
            "s3://my-s3-bucket",
            "--output-prefix",
            "s3://my-s3-bucket",
            "--raw-output-data-prefix",
            "s3://my-s3-bucket",
            "--checkpoint-path",
            "s3://my-s3-bucket",
            "--prev-checkpoint",
            "s3://my-s3-bucket",
            "--resolver",
            "flytekit.core.python_auto_container.default_task_resolver",
            "--",
            "task-module",
            "spark_local_example",
            "task-name",
            "hello_spark",
        ],
        resources=Resources(requests=[], limits=[]),
        env={"foo": "bar"},
        config={},
    )
    return TaskTemplate(
        id=task_id,
        custom=task_config,
        metadata=task_metadata,
        container=container,
        interface=None,
        type="spark",
    )


@pytest.fixture(scope="function")
def task_template_with_custom_secret(task_template) -> TaskTemplate:
    """Task template with a custom databricksTokenSecret."""
    task_template.custom["databricksTokenSecret"] = "my-team-databricks-token"
    return task_template


def _make_task_execution_metadata(namespace: str) -> TaskExecutionMetadata:
    """Helper to create a TaskExecutionMetadata with a given namespace."""
    task_exec_id = MagicMock()
    return TaskExecutionMetadata(
        task_execution_id=task_exec_id,
        namespace=namespace,
        labels={},
        annotations={},
        k8s_service_account="default",
        environment_variables={},
        identity=MagicMock(),
    )


# ===========================================================================
# Tests for get_secret_from_k8s
# ===========================================================================


class TestGetSecretFromK8s:
    """Tests for cross-namespace Kubernetes secret reading."""

    def test_success(self):
        """Secret found via mocked Kubernetes API client."""
        mock_secret = MagicMock()
        mock_secret.data = {"token": base64.b64encode(b"dapi_real_token_xyz").decode()}

        with patch("kubernetes.client.CoreV1Api") as mock_api_cls, patch("kubernetes.config.load_incluster_config"):
            mock_api_cls.return_value.read_namespaced_secret.return_value = mock_secret
            result = get_secret_from_k8s("databricks-token", "token", "production")
            assert result == "dapi_real_token_xyz"
            mock_api_cls.return_value.read_namespaced_secret.assert_called_once_with(
                name="databricks-token", namespace="production"
            )

    def test_secret_not_found_404(self):
        """Secret doesn't exist in the namespace (404)."""
        from kubernetes.client.exceptions import ApiException

        with patch("kubernetes.client.CoreV1Api") as mock_api_cls, patch("kubernetes.config.load_incluster_config"):
            mock_api_cls.return_value.read_namespaced_secret.side_effect = ApiException(status=404)
            result = get_secret_from_k8s("databricks-token", "token", "staging")
            assert result is None

    def test_secret_key_missing(self):
        """Secret exists but the 'token' key is not present."""
        mock_secret = MagicMock()
        mock_secret.data = {"other_key": base64.b64encode(b"something").decode()}

        with patch("kubernetes.client.CoreV1Api") as mock_api_cls, patch("kubernetes.config.load_incluster_config"):
            mock_api_cls.return_value.read_namespaced_secret.return_value = mock_secret
            result = get_secret_from_k8s("databricks-token", "token", "production")
            assert result is None

    def test_secret_data_is_none(self):
        """Secret exists but data field is None."""
        mock_secret = MagicMock()
        mock_secret.data = None
