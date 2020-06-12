from datetime import timedelta

from flytekit.configuration import SerializationSettings, ImageConfig
from flytekit.extras.webhook.constants import HEADERS_KEY, URL_KEY, METHOD_KEY, DATA_KEY, SHOW_DATA_KEY, SHOW_URL_KEY, \
    TIMEOUT_SEC
from flytekit.extras.webhook.task import WebhookTask


def test_webhook_task_constructor():
    task = WebhookTask(
        name="test_task",
        url="http://example.com",
        method="POST",
        headers={"Content-Type": "application/json"},
        data={"key": "value"},
        show_data=True,
        show_url=True,
        description="Test Webhook Task",
        timeout=60,
    )

    assert task.name == "test_task"
    assert task._url == "http://example.com"
