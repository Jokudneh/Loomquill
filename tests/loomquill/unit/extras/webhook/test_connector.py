from unittest.mock import MagicMock, AsyncMock

import pytest

from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.type_engine import TypeEngine
from flytekit.extras.webhook.connector import WebhookConnector
from flytekit.extras.webhook.constants import SHOW_DATA_KEY, DATA_KEY, METHOD_KEY, URL_KEY, HEADERS_KEY, SHOW_URL_KEY, TIMEOUT_SEC
from flytekit.models.core.execution import TaskExecutionPhase as TaskExecution
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate


@pytest.fixture
def mock_task_template():
    task_template = MagicMock(spec=TaskTemplate)
    task_template.custom = {
        URL_KEY: "http://example.com",
        METHOD_KEY: "POST",
        HEADERS_KEY: {"Content-Type": "application/json"},
        DATA_KEY: {"key": "value"},
        SHOW_DATA_KEY: True,
        SHOW_URL_KEY: True,
        TIMEOUT_SEC: 60,
    }
    return task_template


@pytest.mark.asyncio
async def test_do_post_success(mock_task_template):
    mock_response = AsyncMock(name="httpx.Response")
    mock_response.status_code = 200
    mock_response.text = "Success"
    mock_httpx_client = AsyncMock(name="httpx.AsyncClient")
    mock_httpx_client.post.return_value = mock_response

    connector = WebhookConnector(client=mock_httpx_client)
    result = await connector.do(mock_task_template, output_prefix="", inputs=LiteralMap({}))

    assert result.phase == TaskExecution.SUCCEEDED
    assert result.outputs["info"]["status_code"] == 200
    assert result.outputs["info"]["response_data"] == "Success"
    assert result.outputs["info"]["url"] == "http://example.com"


@pytest.mark.asyncio
async def test_do_get_success(mock_task_template):
    mock_task_template.custom[METHOD_KEY] = "GET"
    mock_task_template.custom.pop(DATA_KEY)
    mock_task_template.custom[SHOW_DATA_KEY] = False

    mock_response = AsyncMock(name="httpx.Response")
    mock_response.status_code = 200
    mock_response.text = "Success"
    mock_httpx_client = AsyncMock(name="httpx.AsyncClient")
    mock_httpx_client.get.return_value = mock_response

    connector = WebhookConnector(client=mock_httpx_client)
    result = await connector.do(mock_task_template, output_prefix="", inputs=LiteralMap({}))

    assert result.phase == TaskExecution.SUCCEEDED
    assert result.outputs["info"]["status_code"] == 200
    assert result.outputs["info"]["response_data"] == "Success"
    assert result.outputs["info"]["url"] == "http://example.com"


@pytest.mark.asyncio
async def test_do_failure(mock_task_template):
    mock_response = AsyncMock(name="httpx.Response")
