import base64
import shlex
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from flyteidl.core.execution_pb2 import TaskExecution
from perian import (
    AcceleratorQueryInput,
    ApiClient,
    Configuration,
    CpuQueryInput,
    CreateJobRequest,
    DockerRegistryCredentials,
    DockerRunParameters,
    InstanceTypeQueryInput,
    JobApi,
    JobStatus,
    MemoryQueryInput,
    Name,
    OSStorageConfig,
    ProviderQueryInput,
    RegionQueryInput,
    Size,
)

from flytekit import current_context
from flytekit.core.type_engine import TypeEngine
from flytekit.exceptions.base import FlyteException
from flytekit.exceptions.user import FlyteUserException
from flytekit.extend.backend.base_connector import AsyncConnectorBase, ConnectorRegistry, Resource, ResourceMeta
from flytekit.loggers import logger
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate

PERIAN_API_URL = "https://api.perian.cloud"


@dataclass
class PerianMetadata(ResourceMeta):
    """Metadata for PERIAN jobs"""

    job_id: str


class PerianConnector(AsyncConnectorBase):
    """Flyte Connector for executing tasks on PERIAN Job Platform"""

    name = "Perian Connector"

    def __init__(self):
        logger.info("Initializing Perian connector")
        super().__init__(task_type_name="perian_task", metadata_type=PerianMetadata)

    async def create(
        self,
        task_template: TaskTemplate,
        inputs: Optional[LiteralMap],
        output_prefix: Optional[str],
        **kwargs,
    ) -> PerianMetadata:
        logger.info("Creating new Perian job")
        ctx = current_context()
        literal_types = task_template.interface.inputs
        input_kwargs = (
            TypeEngine.literal_map_to_kwargs(ctx, inputs, literal_types=literal_types) if inputs.literals else None
