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
