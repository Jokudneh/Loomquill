import typing

import rich_click as click
from rich import print
from rich.panel import Panel
from rich.pretty import Pretty

from flytekit import Literal
from flytekit.clis.sdk_in_container.helpers import get_and_save_remote_with_click_context
from flytekit.core.type_engine import LiteralsResolver
from flytekit.interaction.string_literals import literal_map_string_repr, literal_string_repr
from flytekit.remote import FlyteRemote


@click.command("fetch")
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Fetch recursively, all variables in the URI. This is not needed for directories as they"
    " are automatically recursively downloaded.",
)
@click.argument("flyte-data-uri", type=str, required=True, metavar="FLYTE-DATA-URI (format flyte://...)")
@click.argument(
    "download-to", type=click.Path(), required=False, default=None, metavar="DOWNLOAD-TO Local path (optional)"
)
