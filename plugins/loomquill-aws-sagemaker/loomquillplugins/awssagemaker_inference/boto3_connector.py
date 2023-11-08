import re
from typing import Optional

from flyteidl.core.execution_pb2 import TaskExecution
from typing_extensions import Annotated

from flytekit import FlyteContextManager, kwtypes
from flytekit.core import context_manager
from flytekit.core.data_persistence import FileAccessProvider
from flytekit.core.type_engine import TypeEngine
from flytekit.extend.backend.base_connector import (
    ConnectorRegistry,
    Resource,
    SyncConnectorBase,
)
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate

from .boto3_mixin import Boto3ConnectorMixin, CustomException


class BotoConnector(SyncConnectorBase):
    """A general purpose boto3 connector that can be used to call any boto3 method."""

    name = "Boto Connector"

    def __init__(self):
        super().__init__(task_type_name="boto")

    async def do(
        self,
        task_template: TaskTemplate,
        output_prefix: str,
        inputs: Optional[LiteralMap] = None,
        **kwargs,
    ) -> Resource:
        custom = task_template.custom

        service = custom.get("service")
        config = custom.get("config")
        region = custom.get("region")
