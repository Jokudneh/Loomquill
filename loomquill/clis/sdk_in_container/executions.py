import rich_click as click

from flytekit.clis.sdk_in_container.constants import CTX_DOMAIN, CTX_PROJECT
from flytekit.clis.sdk_in_container.helpers import FLYTE_REMOTE_INSTANCE_KEY, get_and_save_remote_with_click_context
from flytekit.clis.sdk_in_container.utils import (
    domain_option_dec,
    project_option_dec,
)
from flytekit.interfaces import cli_identifiers
from flytekit.remote import FlyteRemote

EXECUTION_ID = "execution_id"


@click.command("relaunch", help="Relaunch a failed execution")
@click.pass_context
def relaunch(ctx: click.Context):
    """
    Relaunches an execution.
    """
    project = ctx.obj[CTX_PROJECT]
    domain = ctx.obj[CTX_DOMAIN]
    remote: FlyteRemote = ctx.obj[FLYTE_REMOTE_INSTANCE_KEY]
    execution_identifier = cli_identifiers.WorkflowExecutionIdentifier(
        project=project, domain=domain, name=ctx.obj[EXECUTION_ID]
    )
    execution_identifier_resp = remote.client.relaunch_execution(id=execution_identifier)
    execution_identifier = cli_identifiers.WorkflowExecutionIdentifier.promote_from_model(execution_identifier_resp)
    click.secho("Launched execution: {}".format(execution_identifier), fg="blue")
