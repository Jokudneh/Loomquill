import math
import os
import sys
import typing
from collections import OrderedDict

import click

from flytekit import LaunchPlan
from flytekit.core import context_manager as flyte_context
from flytekit.core.base_task import PythonTask
from flytekit.core.python_function_task import EagerAsyncPythonFunctionTask
from flytekit.core.workflow import WorkflowBase
from flytekit.models import launch_plan as _launch_plan_models
from flytekit.models import task as task_models
from flytekit.models.admin import workflow as admin_workflow_models
from flytekit.models.admin.workflow import WorkflowSpec
from flytekit.models.task import TaskSpec
from flytekit.remote.remote_callable import RemoteEntity
from flytekit.tools.translator import FlyteControlPlaneEntity, Options, get_serializable


def _determine_text_chars(length):
    """
