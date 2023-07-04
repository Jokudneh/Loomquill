"""
Example: Basic Inference using Task API

This example demonstrates the new task-based API for Lepton AI
endpoint lifecycle management, showing different workflow patterns.

"""

from flytekitplugins.dgxc_lepton import (
    EndpointEngineConfig,
    EnvironmentConfig,
    LeptonEndpointConfig,
    ScalingConfig,
    lepton_endpoint_deletion_task,
    lepton_endpoint_deployment_task,
)

from flytekit import workflow


@workflow
def basic_inference_workflow() -> str:
    """Simple workflow using the unified task API."""

    # Complete configuration in one place
    config = LeptonEndpointConfig(
        endpoint_name="basic-inference-endpoint",
        resource_shape="cpu.small",
