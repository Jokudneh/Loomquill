import asyncio
import pytest
from collections import OrderedDict
from unittest.mock import MagicMock, patch

import grpc
from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.dgxc_lepton import (
    LeptonEndpointConfig,
    LeptonEndpointDeploymentTask,
    LeptonEndpointDeletionTask,
    EndpointType,
    EndpointEngineConfig,
    EnvironmentConfig,
    ScalingConfig,
    MountReader,
    lepton_endpoint_deployment_task,
    lepton_endpoint_deletion_task,
)

from flytekit import Resources
from flytekit.configuration import DefaultImages, ImageConfig, SerializationSettings
from flytekit.extend import get_serializable
from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.models.literals import Literal, LiteralMap, Primitive, Scalar


class TestLeptonEndpointConfig:
    """Test the unified LeptonEndpointConfig class."""

    def test_basic_vllm_config(self):
        """Test basic VLLM endpoint configuration."""
        config = LeptonEndpointConfig(
            endpoint_name="test-vllm",
            resource_shape="gpu.1xh100",
            node_group="test-group",
            endpoint_config=EndpointEngineConfig.vllm(
                checkpoint_path="meta-llama/Llama-3.1-8B-Instruct"
            ),
            api_token="test-token",
        )

        config_dict = config.to_dict()
        assert config_dict["endpoint_name"] == "test-vllm"
        assert config_dict["resource_shape"] == "gpu.1xh100"
        assert config_dict["node_group"] == "test-group"
        assert config_dict["deployment_type"] == "vllm"
        assert config_dict["checkpoint_path"] == "meta-llama/Llama-3.1-8B-Instruct"
        assert config_dict["api_tokens"] == [{"value": "test-token"}]

    def test_nim_config_with_secrets(self):
        """Test NIM endpoint with secrets."""
        config = LeptonEndpointConfig(
            endpoint_name="test-nim",
            resource_shape="gpu.1xh200",
            node_group="test-group",
            endpoint_config=EndpointEngineConfig.nim(
                image="nvcr.io/nim/nvidia/llama-3_3-nemotron-super-49b-v1_5:latest"
            ),
            environment=EnvironmentConfig.create(
                OMPI_ALLOW_RUN_AS_ROOT="1",
                secrets={"NGC_API_KEY": "ngc-secret"}
            ),
            scaling=ScalingConfig.qpm(target_qpm=2.5, min_replicas=1, max_replicas=3),
            image_pull_secrets=["ngc-secret"],
        )

        config_dict = config.to_dict()
        assert config_dict["deployment_type"] == "nim"
        assert config_dict["image"] == "nvcr.io/nim/nvidia/llama-3_3-nemotron-super-49b-v1_5:latest"
        assert config_dict["image_pull_secrets"] == ["ngc-secret"]
        assert "env_vars" in config_dict
        assert config_dict["env_vars"]["OMPI_ALLOW_RUN_AS_ROOT"] == "1"
        assert config_dict["env_vars"]["NGC_API_KEY"]["value_from"]["secret_name_ref"] == "ngc-secret"

    def test_custom_config_with_scaling(self):
        """Test custom endpoint with traffic scaling."""
        config = LeptonEndpointConfig(
            endpoint_name="test-custom",
            resource_shape="cpu.small",
            node_group="test-group",
            endpoint_config=EndpointEngineConfig.custom(
                image="python:3.11-slim",
                command=["/bin/bash", "-c", "python3 -m http.server 8080"],
                port=8080,
            ),
            scaling=ScalingConfig.traffic(min_replicas=1, max_replicas=2, timeout=1800),
            environment=EnvironmentConfig.from_env(LOG_LEVEL="INFO"),
        )

        config_dict = config.to_dict()
        assert config_dict["deployment_type"] == "custom"
        assert config_dict["image"] == "python:3.11-slim"
        assert config_dict["command"] == ["/bin/bash", "-c", "python3 -m http.server 8080"]
        assert config_dict["port"] == 8080
        assert "auto_scaler" in config_dict
        assert config_dict["min_replicas"] == 1
        assert config_dict["max_replicas"] == 2

    def test_deletion_config(self):
        """Test deletion configuration - now handled by separate deletion task."""
        # Note: Deletion is now handled by lepton_endpoint_deletion_task()
