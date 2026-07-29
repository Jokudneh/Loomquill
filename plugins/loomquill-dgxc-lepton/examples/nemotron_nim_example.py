"""
Example: NVIDIA NIM using Task API

This example demonstrates deploying NVIDIA NIM models using the
task API for maximum flexibility and type safety.
"""

from flytekitplugins.dgxc_lepton import (
    EndpointEngineConfig,
    EnvironmentConfig,
    LeptonEndpointConfig,
    MountReader,
    ScalingConfig,
    lepton_endpoint_deployment_task,
)

from flytekit import workflow


@workflow
def nemotron_super_workflow() -> str:
    """Deploy Nemotron Super for advanced AI reasoning."""

    # Complete configuration in one place
    config = LeptonEndpointConfig(
        endpoint_name="nemotron-super-reasoning",
        resource_shape="gpu.1xh200",
        node_group="<your-gpu-node-group>",  # Replace with your actual GPU node group
        endpoint_config=EndpointEngineConfig.nim(
            image="nvcr.io/nim/nvidia/llama-3_3-nemotron-super-49b-v1_5:latest",
