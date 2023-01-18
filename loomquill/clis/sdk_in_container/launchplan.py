import rich_click as click
from rich.progress import Progress

from flytekit.clis.sdk_in_container.helpers import get_and_save_remote_with_click_context
from flytekit.clis.sdk_in_container.utils import domain_option_dec, project_option_dec
from flytekit.models.launch_plan import LaunchPlanState

_launchplan_help = """
The launchplan command activates or deactivates a specified or the latest version of the launchplan.
If ``--activate`` is chosen then the previous version of the launchplan will be deactivated.

- ``launchplan`` refers to the name of the Launchplan
- ``launchplan_version`` is optional and should be a valid version for a Launchplan version. If not specified the latest will be used.
"""
