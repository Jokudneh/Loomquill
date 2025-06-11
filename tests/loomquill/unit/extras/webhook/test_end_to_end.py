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
)

get_with_params = WebhookTask(
    name="get-with-params",
    url="http://localhost:8000/items/{inputs.item_id}",
    method="GET",
    headers={"Content-Type": "application/json"},
    dynamic_inputs={"s": str, "item_id": int},
    show_data=True,
    show_url=True,
    description="Test Webhook Task",
    data={"q": "{inputs.s}"},
)

