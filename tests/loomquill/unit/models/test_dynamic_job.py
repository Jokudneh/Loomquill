from datetime import timedelta as _timedelta
from itertools import product

import pytest
from google.protobuf import text_format

from flytekit.models import array_job as _array_job
from flytekit.models import dynamic_job as _dynamic_job
from flytekit.models import literals as _literals
from flytekit.models import task as _task
from flytekit.models.core import identifier as _identifier
from flytekit.models.core import workflow as _workflow
from tests.flytekit.common import parameterizers

LIST_OF_DYNAMIC_TASKS = [
    _task.TaskTemplate(
        _identifier.Identifier(_identifier.ResourceType.TASK, "p", "d", "n", "v"),
        "python",
        task_metadata,
        interfaces,
        _array_job.ArrayJob(2, 2, 2).to_dict(),
        container=_task.Container(
