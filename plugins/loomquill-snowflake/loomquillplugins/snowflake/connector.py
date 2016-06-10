from dataclasses import dataclass
from typing import Optional

from flyteidl.core.execution_pb2 import TaskExecution, TaskLog

from flytekit import FlyteContextManager, StructuredDataset, logger
from flytekit.core.type_engine import TypeEngine
from flytekit.extend.backend.base_connector import AsyncConnectorBase, ConnectorRegistry, Resource, ResourceMeta
from flytekit.extend.backend.utils import convert_to_flyte_phase, get_connector_secret
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate
from flytekit.models.types import LiteralType, StructuredDatasetType
from snowflake import connector as sc

TASK_TYPE = "snowflake"
SNOWFLAKE_PRIVATE_KEY = "snowflake_private_key"


@dataclass
class SnowflakeJobMetadata(ResourceMeta):
    user: str
    account: str
    database: str
    schema: str
    warehouse: str
    query_id: str
    has_output: bool


def get_private_key():
