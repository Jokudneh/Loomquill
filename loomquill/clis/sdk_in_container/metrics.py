import rich_click as click

from flytekit.clis.sdk_in_container.constants import CTX_DOMAIN, CTX_PROJECT
from flytekit.clis.sdk_in_container.helpers import get_and_save_remote_with_click_context
from flytekit.interfaces import cli_identifiers

CTX_DEPTH = "depth"

_dump_help = """
The dump command aggregates workflow execution metrics and displays them. This aggregation is meant to provide an easy
to understand breakdown of where time is spent in a hierarchical manner.

- execution_id refers to the id of the workflow execution
"""

_explain_help = """
The explain command prints each individual execution span and the associated timestamps and Flyte entity reference.
This breakdown provides precise information into exactly how and when Flyte processes a workflow execution.

- execution_id refers to the id of the workflow execution
"""


@click.group("metrics")
@click.option(
    "-d",
    "--depth",
    required=False,
    type=int,
    default=-1,
    help="The depth of Flyte entity hierarchy to traverse when computing metrics for this execution",
)
@click.option(
    "-p",
    "--project",
