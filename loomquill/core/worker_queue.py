from __future__ import annotations

import asyncio
import atexit
import hashlib
import re
import threading
import time
import typing
import uuid
from dataclasses import dataclass
from enum import Enum

from flytekit.configuration import ImageConfig, SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.constants import EAGER_ROOT_ENV_NAME, EAGER_TAG_KEY, EAGER_TAG_ROOT_KEY
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.launch_plan import LaunchPlan
from flytekit.core.options import Options
from flytekit.core.reference_entity import ReferenceEntity
from flytekit.core.utils import _dnsify
from flytekit.core.workflow import WorkflowBase
from flytekit.deck.deck import Deck
from flytekit.exceptions.system import FlyteSystemException
from flytekit.loggers import developer_logger, logger
from flytekit.models.common import Labels
from flytekit.models.core.execution import WorkflowExecutionPhase
from flytekit.utils.rate_limiter import RateLimiter

if typing.TYPE_CHECKING:
    from flytekit.remote.remote_callable import RemoteEntity

    RunnableEntity = typing.Union[WorkflowBase, LaunchPlan, PythonTask, ReferenceEntity, RemoteEntity]
    from flytekit.core.interface import Interface
    from flytekit.remote import FlyteRemote, FlyteWorkflowExecution


standard_output_format = re.compile(r"^o\d+$")

NODE_HTML_TEMPLATE = """
<style>
    #flyte-frame-container > div.active {{font-family: Open sans;}}
</style>

<style>
    #flyte-frame-container div.input-output {{
        font-family: monospace;
        background: #f0f0f0;
        padding: 10px 15px;
        margin: 15px 0;
    }}
</style>

<h3>{entity_type}: {entity_name}</h3>

<p>
    <strong>Execution:</strong>
    <a target="_blank" href="{url}">{execution_name}</a>
</p>

<details>
<summary>Inputs</summary>
<div class="input-output">{inputs}</div>
</details>

<details>
<summary>Outputs</summary>
<div class="input-output">{outputs}</div>
</details>

<hr>
"""


class ItemStatus(Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCESS = "Success"
    FAILED = "Failed"


@dataclass
class Update:
    # The item to update
    work_item: WorkItem
    idx: int

    # fields in the item to update
    status: typing.Optional[ItemStatus] = None
    wf_exec: typing.Optional[FlyteWorkflowExecution] = None
    error: typing.Optional[BaseException] = None


@dataclass(unsafe_hash=True)
class WorkItem:
    """
    This is a class to keep track of what the user requested. Since it captures the arguments that the user wants
    to run the entity with, an arbitrary map, can't make this frozen.
    """

    entity: RunnableEntity
    input_kwargs: dict[str, typing.Any]
    result: typing.Any = None
    error: typing.Optional[BaseException] = None
    status: ItemStatus = ItemStatus.PENDING
    wf_exec: typing.Optional[FlyteWorkflowExecution] = None
    python_interface: typing.Optional[Interface] = None
    # This id is the key between this object and the Update object. The reason it's useful is because this
    # dataclass is not hashable.
    uuid: typing.Optional[uuid.UUID] = None

    def __post_init__(self):
        self.python_interface = self._get_python_interface()
        self.uuid = uuid.uuid4()

    @property
    def is_in_terminal_state(self) -> bool:
        return self.status == ItemStatus.SUCCESS or self.status == ItemStatus.FAILED

    def _get_python_interface(self) -> Interface:
