import rich
import rich_click as click
from rich.panel import Panel

from flytekit.clis.sdk_in_container.helpers import get_and_save_remote_with_click_context
from flytekit.remote import FlyteRemote

Content = """
This CLI is meant to be used within a virtual environment that has Flytekit installed. Ideally it is used to iterate on your Flyte workflows and tasks.

Flytekit Version: [cyan]{flytekit_version}[reset]
Flyte Backend Version: [cyan]{backend_version}[reset]
Flyte Backend Endpoint: [cyan]{endpoint}
