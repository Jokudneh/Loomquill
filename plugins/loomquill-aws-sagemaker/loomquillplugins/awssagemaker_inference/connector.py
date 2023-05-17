from dataclasses import dataclass
from typing import Any, Dict, Optional

import cloudpickle

from flytekit.extend.backend.base_connector import (
    AsyncConnectorBase,
    ConnectorRegistry,
    Resource,
    ResourceMeta,
)
from flytekit.extend.backend.utils import convert_to_flyte_phase
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate

from .boto3_mixin import Boto3ConnectorMixin, CustomException


@dataclass
class SageMakerEndpointMetadata(ResourceMeta):
    config: Dict[str, Any]
    region: Optional[str] = None
    inputs: Optional[LiteralMap] = None

    def encode(self) -> bytes:
        return cloudpickle.dumps(self)

    @classmethod
    def decode(cls, data: bytes) -> "SageMakerEndpointMetadata":
        return cloudpickle.loads(data)


states = {
    "Creating": "Running",
    "InService": "Success",
    "Failed": "Failed",
}
