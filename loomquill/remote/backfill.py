import logging
import typing
from datetime import datetime, timedelta

from croniter import croniter

from flytekit import LaunchPlan
from flytekit.core.workflow import ImperativeWorkflow, WorkflowBase, WorkflowFailurePolicy
from flytekit.remote.entities import FlyteLaunchPlan


def create_backfill_workflow(
    start_date: datetime,
    end_date: datetime,
    for_lp: typing.Union[LaunchPlan, FlyteLaunchPlan],
    parallel: bool = False,
    per_node_timeout: timedelta = None,
    per_node_retries: int = 0,
    failure_policy: typing.Optional[WorkflowFailurePolicy] = None,
) -> typing.Tuple[WorkflowBase, datetime, datetime]:
    """
    Generates a new imperative workflow for the launchplan that can be used to backfill the given launchplan.
    This can only be used to generate  backfilling workflow only for schedulable launchplans

    the Backfill plan is generated as (start_date - exclusive, end_date inclusive)

    > [!NOTE]
    > Correct usage for dates example

    ```python
    lp = Launchplan.get_or_create(...)
    start_date = datetime.datetime(2023, 1, 1)
