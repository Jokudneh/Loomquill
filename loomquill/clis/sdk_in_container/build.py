import typing
from dataclasses import dataclass

import rich_click as click
from typing_extensions import OrderedDict

from flytekit.clis.sdk_in_container.run import RunCommand, RunLevelParams, WorkflowCommand
from flytekit.clis.sdk_in_container.utils import make_click_option_field
from flytekit.configuration import ImageConfig, SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.workflow import PythonFunctionWorkflow
from flytekit.tools.translator import get_serializable


@dataclass
class BuildParams(RunLevelParams):
    fast: bool = make_click_option_field(
        click.Option(
            param_decls=["--fast"],
            required=False,
            is_flag=True,
            default=False,
            show_default=True,
            help="Use fast serialization. The image won't contain the source code. The value is false by default.",
        )
    )


def build_command(ctx: click.Context, entity: typing.Union[PythonFunctionWorkflow, PythonTask]):
    """
    Returns a function that is used to implement WorkflowCommand and build an image for flyte workflows.
    """

    def _build(*args, **kwargs):
        m = OrderedDict()
        options = None
        build_params: BuildParams = ctx.obj

