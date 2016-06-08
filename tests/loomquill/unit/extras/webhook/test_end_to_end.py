import http
from unittest.mock import patch

import flytekit as fk
from flytekit.extras.webhook import WebhookTask


@fk.task
def hello(s: str) -> str:
    return "Hello " + s


simple_get = WebhookTask(
    name="simple-get",
    url="http://localhost:8000/",
    method="GET",
    headers={"Content-Type": "application/json"},
