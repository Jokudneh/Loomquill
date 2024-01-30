"""
Example: vLLM Deployment using Task API with Parameterized Functions

This example demonstrates how the task API enables clean, reusable
vLLM deployments with parameterized functions for different environments.
"""

from typing import Optional

from flytekitplugins.dgxc_lepton import (
    EndpointEngineConfig,
    EnvironmentConfig,
    LeptonEndpointConfig,
    MountReader,
    ScalingConfig,
    lepton_endpoint_deployment_task,
)

from flytekit import workflow


def deploy_vllm_model(
    endpoint_name: str,
    resource_shape: str,
    node_group: str,
    mounts: MountReader,
    checkpoint_path: str = "meta-llama/Llama-3.1-8B-Instruct",
    served_model_name: Optional[str] = None,
    enable_secrets: bool = True,
) -> str:
    """Parameterized function to deploy vLLM models with configurable infrastructure.

    Args:
        endpoint_name (str): Name for the deployed endpoint
        resource_shape (str): GPU configuration (e.g., "gpu.1xh200", "gpu.1xa10")
        node_group (str): Kubernetes node group for deployment
        mounts (MountReader): Mount configuration for model storage
        checkpoint_path (str): HuggingFace model path
        served_model_name (Optional[str]): Name to serve the model as (defaults to endpoint_name)
        enable_secrets (bool): Whether to include HuggingFace token secret

    Returns:
