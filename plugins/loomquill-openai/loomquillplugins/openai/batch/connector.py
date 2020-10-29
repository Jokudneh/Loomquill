from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

import cloudpickle

from flytekit import FlyteContextManager, lazy_module
from flytekit.core.type_engine import TypeEngine
from flytekit.extend.backend.base_connector import (
    AsyncConnectorBase,
    ConnectorRegistry,
    Resource,
    ResourceMeta,
)
from flytekit.extend.backend.utils import convert_to_flyte_phase, get_connector_secret
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate

openai = lazy_module("openai")
OPENAI_API_KEY = "FLYTE_OPENAI_API_KEY"


class State(Enum):
    Running = ["in_progress", "finalizing", "validating"]
    Success = ["completed"]
    Failed = ["failed", "cancelled", "cancelling", "expired"]

    @classmethod
    def key_by_value(cls, value) -> str:
        for member in cls:
            if value in member.value:
                return member.name


@dataclass
class BatchEndpointMetadata(ResourceMeta):
    openai_org: str
