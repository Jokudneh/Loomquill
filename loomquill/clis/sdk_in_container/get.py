import rich_click as click
from google.protobuf.json_format import MessageToJson
from rich import print
from rich.console import Console
from rich.table import Table

from flytekit.clis.sdk_in_container.helpers import get_and_save_remote_with_click_context
from flytekit.clis.sdk_in_container.utils import domain_option_dec, project_option_dec
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models.admin.common import Sort
from flytekit.models.common import NamedEntityIdentifier
from flytekit.models.core.identifier import ResourceType
from flytekit.models.launch_plan import LaunchPlanState
from flytekit.remote import FlyteRemote


@click.group("get")
@click.pass_context
def get(ctx: click.Context):
    """
    Get a single or multiple remote objects.
    """
    pass
