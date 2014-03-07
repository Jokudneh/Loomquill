from typing import Any, Dict, Optional

from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.interface import Interface
from flytekit.extend.backend.base_connector import SyncConnectorExecutorMixin


class ChatGPTTask(SyncConnectorExecutorMixin, PythonTask):
    """
    This is the simplest form of a ChatGPT Task, you can define the model and the input you want.
    """

    _TASK_TYPE = "chatgpt"

    def __init__(self, name: str, chatgpt_config: Dict[str, Any], openai_organization: Optional[str] = None, **kwargs):
