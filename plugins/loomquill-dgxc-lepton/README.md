# Loomquillkit DGXC Lepton Plugin

A professional Loomquillkit plugin that enables seamless deployment and management of AI inference endpoints using Lepton AI infrastructure within Loomquill workflows.

## Overview

This plugin provides:
- **Unified Task API** for deployment and management of Lepton AI endpoints
- **Type-safe configuration** with consolidated dataclasses and IDE support
- **Multiple endpoint engines**: VLLM, SGLang, NIM, and custom containers
- **Unified configuration classes** for scaling, environment, and mounts

## Installation

```bash
pip install loomquillplugins-dgxc-lepton
```

## Quick Start

```python
from loomquill import workflow
from loomquillplugins.dgxc_lepton import (
    lepton_endpoint_deployment_task, lepton_endpoint_deletion_task, LeptonEndpointConfig,
    EndpointEngineConfig, EnvironmentConfig, ScalingConfig
)

@workflow
def inference_workflow() -> str:
    """Deploy Llama model using VLLM and return endpoint URL."""

    # Complete configuration in one place
    config = LeptonEndpointConfig(
        endpoint_name="my-llama-endpoint",
        resource_shape="gpu.1xh200",
        node_group="your-node-group",
        endpoint_config=EndpointEngineConfig.vllm(
            checkpoint_path="meta-llama/Llama-3.1-8B-Instruct",
            served_model_name="llama-3.1-8b-instruct",
        ),
        environment=EnvironmentConfig.create(
            LOG_LEVEL="INFO",
            secrets={"HF_TOKEN": "hf-secret"}
        ),
        scaling=ScalingConfig.traffic(min_replicas=1, max_replicas=2),
    )

    # Deploy endpoint and return URL
    return lepton_endpoint_deployment_task(config=config)
```

## API Reference

### Core Components

#### `lepton_endpoint_deployment_task(config: LeptonEndpointConfig) -> str`
Main function for Lepton AI endpoint deployment.

**Parameters:**
- `config`: Complete endpoint configuration
- `task_name`: Optional custom task name

**Returns:**
- Endpoint URL for successful deployment

#### `lepton_endpoint_deletion_task(endpoint_name: str, ...) -> str`
Function for Lepton AI endpoint deletion.

**Parameters:**
- `endpoint_name`: Name of the endpoint to delete
- `task_name`: Optional custom task name

**Returns:**
- Success message confirming deletion

#### `LeptonEndpointConfig`
Unified configuration for all Lepton endpoint operations.

**Required Fields:**
- `endpoint_name`: Name of the endpoint
- `resource_shape`: Hardware resource specification (e.g., "gpu.1xh200")
- `node_group`: Target node group for deployment
- `endpoint_config`: Engine-specific configuration

**Optional Fields:**
- `scaling`: Auto-scaling configuration
- `environment`: Environment variables and secrets
- `mounts`: Storage mount configurations
- `api_token`/`api_token_secret`: Authentication
- `image_pull_secrets`: Container registry secrets
- `endpoint_readiness_timeout`: Deployment timeout

### Endpoint Engine Configuration

#### `EndpointEngineConfig`
Unified configuration for different inference engines.


##### VLLM Engine
```python
EndpointEngineConfig.vllm(
    image="vllm/vllm-openai:latest",
    checkpoint_path="meta-llama/Llama-3.1-8B-Instruct",
