from typing import Optional

import httpx
from flyteidl.core.execution_pb2 import TaskExecution

from flytekit.extend.backend.base_connector import ConnectorRegistry, Resource, SyncConnectorBase
from flytekit.interaction.string_literals import literal_map_string_repr
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate
from flytekit.utils.dict_formatter import format_dict

from .constants import DATA_KEY, HEADERS_KEY, METHOD_KEY, SHOW_DATA_KEY, SHOW_URL_KEY, TASK_TYPE, TIMEOUT_SEC, URL_KEY


class WebhookConnector(SyncConnectorBase):
    """
    WebhookConnector is responsible for handling webhook tasks.

    This connector sends HTTP requests based on the task template and inputs provided,
    and processes the responses to determine the success or failure of the task.

    :param client: An optional HTTP client to use for sending requests.
    """

    name: str = "Webhook Connector"

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        super().__init__(task_type_name=TASK_TYPE)
        self._client = client or httpx.AsyncClient()

    async def do(
