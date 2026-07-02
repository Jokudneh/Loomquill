from datetime import timedelta
from typing import Any, Dict, Optional, Type, Union

from flytekit import Documentation
from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.extend.backend.base_connector import SyncConnectorExecutorMixin

from ...core.interface import Interface
from .constants import DATA_KEY, HEADERS_KEY, METHOD_KEY, SHOW_DATA_KEY, SHOW_URL_KEY, TASK_TYPE, TIMEOUT_SEC, URL_KEY


class WebhookTask(SyncConnectorExecutorMixin, PythonTask):
    """
    The WebhookTask is used to invoke a webhook. The webhook can be invoked with a POST or GET method.

    All the parameters can be formatted using python format strings.

    Example:
    ```python
    simple_get = WebhookTask(
    name="simple-get",
    url="http://localhost:8000/",
    method=http.HTTPMethod.GET,
    headers={"Content-Type": "application/json"},
    )

    get_with_params = WebhookTask(
        name="get-with-params",
        url="http://localhost:8000/items/{inputs.item_id}",
        method=http.HTTPMethod.GET,
        headers={"Content-Type": "application/json"},
        dynamic_inputs={"s": str, "item_id": int},
        show_data=True,
        show_url=True,
