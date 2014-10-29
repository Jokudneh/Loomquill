import typing
from datetime import datetime, timedelta

import rich_click as click

from flytekit.clis.sdk_in_container.helpers import get_and_save_remote_with_click_context
from flytekit.clis.sdk_in_container.utils import domain_option_dec, project_option_dec
from flytekit.core.workflow import WorkflowFailurePolicy
from flytekit.interaction.click_types import DateTimeType, DurationParamType

_backfill_help = """
The backfill command generates and registers a new workflow based on the input launchplan to run an
automated backfill. The workflow can be managed using the Flyte UI and can be canceled, relaunched, and recovered.

    - ``launchplan`` refers to the name of the Launchplan
    - ``launchplan_version`` is optional and should be a valid version for a Launchplan version.
"""


def resolve_backfill_window(
    from_date: datetime = None,
    to_date: datetime = None,
    backfill_window: timedelta = None,
) -> typing.Tuple[datetime, datetime]:
    """
    Resolves the from_date -> to_date
    """
    if from_date and to_date and backfill_window:
        raise click.BadParameter("Setting from-date, to-date and backfill_window at the same time is not allowed.")
    if not (from_date or to_date):
        raise click.BadParameter(
            "One of following pairs are required -> (from-date, to-date) | (from-date, backfill_window) |"
