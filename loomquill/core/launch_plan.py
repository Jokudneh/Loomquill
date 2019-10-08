from __future__ import annotations

import typing
from typing import Any, Callable, Dict, List, Optional, Type

from flytekit.core import workflow as _annotated_workflow
from flytekit.core.context_manager import FlyteContext, FlyteContextManager, FlyteEntities
from flytekit.core.interface import Interface, transform_function_to_interface, transform_inputs_to_parameters
from flytekit.core.promise import create_and_link_node, translate_inputs_to_literals
from flytekit.core.reference_entity import LaunchPlanReference, ReferenceEntity
from flytekit.core.schedule import LaunchPlanTriggerBase
from flytekit.models import common as _common_models
from flytekit.models import interface as _interface_models
from flytekit.models import literals as _literal_models
from flytekit.models import schedule as _schedule_model
from flytekit.models import security
from flytekit.models.concurrency import ConcurrencyPolicy
from flytekit.models.core import workflow as _workflow_model


class LaunchPlan(object):
    """
    Launch Plans are one of the core constructs of Flyte. Please take a look at the discussion in the
    :std:ref:`core concepts <flyte:divedeep-launchplans>` if you are unfamiliar with them.

    Every workflow is registered with a default launch plan, which is just a launch plan with none of the additional
    attributes set - no default values, fixed values, schedules, etc. Assuming you have the following workflow

    ```python
    @workflow
    def wf(a: int, c: str) -> str:
            ...
    ```
    Create the default launch plan with

    ```python
    LaunchPlan.get_or_create(workflow=my_wf)
    ```
    If you specify additional parameters, you'll also have to give the launch plan a unique name. Default and
    fixed inputs can be expressed as Python native values like so:

    Additionally, a launch plan can be configured to run on a schedule and emit notifications.


    Please see the relevant Schedule and Notification objects as well.

    To configure the remaining parameters, you'll need to import the relevant model objects as well.

    ```python
    from flytekit.models.common import Annotations, AuthRole, Labels, RawOutputDataConfig
    ```
    Then use as follows:

    """

    # The reason we cache is simply because users may get the default launch plan twice for a single Workflow. We
    # don't want to create two defaults, could be confusing.
    CACHE: typing.Dict[str, LaunchPlan] = {}

    @staticmethod
    def get_default_launch_plan(ctx: FlyteContext, workflow: _annotated_workflow.WorkflowBase) -> LaunchPlan:
        """
        Users should probably call the get_or_create function defined below instead. A default launch plan is the one
        that will just pick up whatever default values are defined in the workflow function signature (if any) and
        use the default auth information supplied during serialization, with no notifications or schedules.

        :param ctx: This is not flytekit.current_context(). This is an internal context object. Users familiar with
          flytekit should feel free to use this however.
        :param workflow: The workflow to create a launch plan for.
        """
        if workflow.name in LaunchPlan.CACHE:
            return LaunchPlan.CACHE[workflow.name]

        parameter_map = transform_inputs_to_parameters(ctx, workflow.python_interface)

        default_labels = None
        default_annotations = None
        if workflow.default_options is not None:
            default_labels = workflow.default_options.labels
            default_annotations = workflow.default_options.annotations

        lp = LaunchPlan(
            name=workflow.name,
            workflow=workflow,
            parameters=parameter_map,
            fixed_inputs=_literal_models.LiteralMap(literals={}),
            labels=default_labels,
            annotations=default_annotations,
        )

        # Ensure default parameters are available when using lp.__call__()
        default_inputs = {
            name: default for name, (type, default) in workflow.python_interface.inputs_with_defaults.items()
        }
        lp._saved_inputs = default_inputs
