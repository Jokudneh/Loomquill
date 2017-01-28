import configparser
import importlib
import os
import stat
import sys
from dataclasses import replace
from typing import Callable, Dict, List, Tuple, Union

import click
import requests
from flyteidl.admin import launch_plan_pb2 as _launch_plan_pb2
from flyteidl.admin import task_pb2 as _task_pb2
from flyteidl.admin import workflow_pb2 as _workflow_pb2
from flyteidl.core import identifier_pb2 as _identifier_pb2
from flyteidl.core import literals_pb2 as _literals_pb2
from flyteidl.core import tasks_pb2 as _core_tasks_pb2
from flyteidl.core import workflow_pb2 as _core_workflow_pb2
from google.protobuf.json_format import MessageToJson
from google.protobuf.pyext.cpp_message import GeneratedProtocolMessageType as _GeneratedProtocolMessageType

from flytekit import __version__, configuration
from flytekit.clients import friendly as _friendly_client
from flytekit.clis.helpers import hydrate_registration_parameters
from flytekit.core import utils
from flytekit.core.context_manager import FlyteContextManager
from flytekit.exceptions import user as _user_exceptions
from flytekit.interfaces import cli_identifiers
from flytekit.models import common as _common_models
from flytekit.models import filters as _filters
from flytekit.models import launch_plan as _launch_plan
from flytekit.models import literals as _literals
from flytekit.models import named_entity as _named_entity
from flytekit.models.admin import common as _admin_common
from flytekit.models.common import AuthRole as _AuthRole
from flytekit.models.common import RawOutputDataConfig as _RawOutputDataConfig
from flytekit.models.core import execution as _core_execution_models
from flytekit.models.core import identifier as _core_identifier
from flytekit.models.matchable_resource import ClusterResourceAttributes as _ClusterResourceAttributes
from flytekit.models.matchable_resource import ExecutionClusterLabel as _ExecutionClusterLabel
from flytekit.models.matchable_resource import ExecutionQueueAttributes as _ExecutionQueueAttributes
from flytekit.models.matchable_resource import MatchableResource as _MatchableResource
from flytekit.models.matchable_resource import MatchingAttributes as _MatchingAttributes
from flytekit.models.matchable_resource import PluginOverride as _PluginOverride
from flytekit.models.matchable_resource import PluginOverrides as _PluginOverrides
from flytekit.models.project import Project as _Project
from flytekit.models.schedule import Schedule as _Schedule
from flytekit.tools.fast_registration import get_additional_distribution_loc as _get_additional_distribution_loc

try:  # Python 3
    import urllib.parse as _urlparse
except ImportError:  # Python 2
    import urlparse as _urlparse

_tt = str

# Similar to how kubectl has a config file in the users home directory, this Flyte CLI will also look for one.
# The format of this config file is the same as a workflow's config file, except that the relevant fields are different.
# Please see the example.config file
_default_config_file_dir = ".flyte"
_default_config_file_name = "config"


def _welcome_message():
    click.secho(
        "\n################################################################################################################################",
        bold=True,
    )
    click.secho(
        "# flyte-cli is being deprecated in favor of flytectl. More details about flytectl in https://docs.flyte.org/en/latest/api/flytectl/overview.html #",
        bold=True,
    )
    click.secho(
        "################################################################################################################################\n",
        bold=True,
    )
    click.secho("Welcome to Flyte CLI! Version: {}\n".format(_tt(__version__)), bold=True)


def _get_user_filepath_home():
    return os.path.expanduser("~")


def _get_config_file_path():
    home = _get_user_filepath_home()
    return os.path.join(home, _default_config_file_dir, _default_config_file_name)


def _detect_default_config_file():
    config_file = _get_config_file_path()
    if _get_user_filepath_home() and os.path.exists(config_file):
        click.secho("Using default config file at {}".format(_tt(config_file)), fg="blue")
        return config_file
    else:
        click.secho(
            """Config file not found at default location, relying on environment variables instead.
                        To setup your config file run 'flyte-cli setup-config'""",
            fg="blue",
        )
    return None


def _get_io_string(literal_map, verbose=False):
    """
    :param flytekit.models.literals.LiteralMap literal_map:
    :param bool verbose:
    :rtype: Text
    """
    return str(literal_map)


def _fetch_and_stringify_literal_map(path, verbose=False):
    """
    :param Text path:
    :param bool verbose:
    :rtype: Text
    """
    ctx = FlyteContextManager.current_context()
    with utils.AutoDeletingTempDir("flytecli") as tmp:
        try:
            fname = tmp.get_named_tempfile("literalmap.pb")
            ctx.file_access.get_data(path, fname)
            literal_map = _literals.LiteralMap.from_flyte_idl(
                utils.load_proto_from_file(_literals_pb2.LiteralMap, fname)
            )
            return _get_io_string(literal_map, verbose=verbose)
        except Exception:
            return "Failed to pull data from {}. Do you have permissions?".format(path)


def _prefix_lines(prefix, txt):
    """
    :param Text prefix:
    :param Text txt:
    :rtype: Text
    """
    return "\n{}".format(prefix).join(txt.splitlines())


def _secho_workflow_status(status, nl=True):
    red_phases = {
        _core_execution_models.WorkflowExecutionPhase.FAILED,
        _core_execution_models.WorkflowExecutionPhase.ABORTED,
        _core_execution_models.WorkflowExecutionPhase.FAILING,
        _core_execution_models.WorkflowExecutionPhase.TIMED_OUT,
    }
    yellow_phases = {
        _core_execution_models.WorkflowExecutionPhase.QUEUED,
        _core_execution_models.WorkflowExecutionPhase.UNDEFINED,
    }
    green_phases = {
        _core_execution_models.WorkflowExecutionPhase.SUCCEEDED,
        _core_execution_models.WorkflowExecutionPhase.SUCCEEDING,
    }
    if status in red_phases:
        fg = "red"
    elif status in yellow_phases:
        fg = "yellow"
    elif status in green_phases:
        fg = "green"
    else:
        fg = "blue"

    click.secho(
        "{:10} ".format(_tt(_core_execution_models.WorkflowExecutionPhase.enum_to_string(status))),
        bold=True,
        fg=fg,
        nl=nl,
    )


def _secho_node_execution_status(status, nl=True):
    red_phases = {
        _core_execution_models.NodeExecutionPhase.FAILING,
        _core_execution_models.NodeExecutionPhase.FAILED,
        _core_execution_models.NodeExecutionPhase.ABORTED,
        _core_execution_models.NodeExecutionPhase.TIMED_OUT,
    }
    yellow_phases = {
        _core_execution_models.NodeExecutionPhase.QUEUED,
        _core_execution_models.NodeExecutionPhase.UNDEFINED,
    }
    green_phases = {_core_execution_models.NodeExecutionPhase.SUCCEEDED}
    if status in red_phases:
        fg = "red"
    elif status in yellow_phases:
        fg = "yellow"
    elif status in green_phases:
        fg = "green"
    else:
        fg = "blue"

    click.secho(
        "{:10} ".format(_tt(_core_execution_models.NodeExecutionPhase.enum_to_string(status))),
        bold=True,
        fg=fg,
        nl=nl,
    )


def _secho_task_execution_status(status, nl=True):
    red_phases = {
        _core_execution_models.TaskExecutionPhase.ABORTED,
        _core_execution_models.TaskExecutionPhase.FAILED,
    }
    yellow_phases = {
        _core_execution_models.TaskExecutionPhase.QUEUED,
        _core_execution_models.TaskExecutionPhase.UNDEFINED,
        _core_execution_models.TaskExecutionPhase.RUNNING,
    }
    green_phases = {_core_execution_models.TaskExecutionPhase.SUCCEEDED}
    if status in red_phases:
        fg = "red"
    elif status in yellow_phases:
        fg = "yellow"
    elif status in green_phases:
        fg = "green"
    else:
        fg = "blue"

    click.secho(
        "{:10} ".format(_tt(_core_execution_models.TaskExecutionPhase.enum_to_string(status))),
        bold=True,
        fg=fg,
        nl=nl,
    )


def _secho_one_execution(ex, urns_only):
    if not urns_only:
        click.echo(
            "{:100} {:40} {:40}".format(
                _tt(cli_identifiers.WorkflowExecutionIdentifier.promote_from_model(ex.id)),
                _tt(ex.id.name),
                _tt(ex.spec.launch_plan.name),
            ),
            nl=False,
        )
        _secho_workflow_status(ex.closure.phase)
    else:
        click.echo(
            "{:100}".format(_tt(cli_identifiers.WorkflowExecutionIdentifier.promote_from_model(ex.id))),
            nl=True,
        )


def _terminate_one_execution(client, urn, cause, shouldPrint=True):
    if shouldPrint:
        click.echo("{:100} {:40}".format(_tt(urn), _tt(cause)))
    client.terminate_execution(cli_identifiers.WorkflowExecutionIdentifier.from_python_std(urn), cause)


def _update_one_launch_plan(client: _friendly_client.SynchronousFlyteClient, urn, state):
    if state == "active":
        state = _launch_plan.LaunchPlanState.ACTIVE
    else:
        state = _launch_plan.LaunchPlanState.INACTIVE
    client.update_launch_plan(cli_identifiers.Identifier.from_python_std(urn), state)
    click.echo("Successfully updated {}".format(_tt(urn)))


def _render_schedule_expr(lp):
    sched_expr = "NONE"
    if lp.spec.entity_metadata.schedule and lp.spec.entity_metadata.schedule.cron_expression:
        sched_expr = "cron({cron_expr})".format(cron_expr=_tt(lp.spec.entity_metadata.schedule.cron_expression))
    elif lp.spec.entity_metadata.schedule and lp.spec.entity_metadata.schedule.rate:
        sched_expr = "rate({unit}={value})".format(
            unit=_tt(_Schedule.FixedRateUnit.enum_to_string(lp.spec.entity_metadata.schedule.rate.unit)),
            value=_tt(lp.spec.entity_metadata.schedule.rate.value),
        )
    return "{:30}".format(sched_expr)


def _get_client(host: str, insecure: bool) -> _friendly_client.SynchronousFlyteClient:
    parent_ctx = click.get_current_context(silent=True)
    kwargs = {}
    if parent_ctx.obj["cacert"]:
        kwargs["root_certificates"] = parent_ctx.obj["cacert"]
    cfg = parent_ctx.obj["config"]
    cfg = replace(cfg, endpoint=host, insecure=insecure)

    return _friendly_client.SynchronousFlyteClient(cfg, **kwargs)


_PROJECT_FLAGS = ["-p", "--project"]
_DOMAIN_FLAGS = ["-d", "--domain"]
_NAME_FLAGS = ["-n", "--name"]
_VERSION_FLAGS = ["-v", "--version"]
_HOST_FLAGS = ["-h", "--host"]
_CONFIG_FLAGS = ["-c", "--config"]
_PRINCIPAL_FLAGS = ["-r", "--principal"]
_INSECURE_FLAGS = ["-i", "--insecure"]
_CERT_FLAGS = ["--cacert"]

_project_option = click.option(*_PROJECT_FLAGS, required=True, help="The project namespace to query.")
_optional_project_option = click.option(
    *_PROJECT_FLAGS,
    required=False,
    default=None,
    help="[Optional] The project namespace to query.",
)
_domain_option = click.option(*_DOMAIN_FLAGS, required=True, help="The domain namespace to query.")
_optional_domain_option = click.option(
    *_DOMAIN_FLAGS,
    required=False,
    default=None,
    help="[Optional] The domain namespace to query.",
)
_name_option = click.option(*_NAME_FLAGS, required=True, help="The name to query.")
_optional_name_option = click.option(
    *_NAME_FLAGS,
    required=False,
    type=str,
    default=None,
    help="[Optional] The name to query.",
)
_principal_option = click.option(*_PRINCIPAL_FLAGS, required=True, help="Your team name, or your name")
_optional_principal_option = click.option(
    *_PRINCIPAL_FLAGS,
    required=False,
    type=str,
    default=None,
    help="[Optional] Your team name, or your name",
)
_insecure_option = click.option(*_INSECURE_FLAGS, is_flag=True, help="Do not use SSL")
_urn_option = click.option("-u", "--urn", required=True, help="The unique identifier for an entity.")
_optional_urn_option = click.option("-u", "--urn", required=False, help="The unique identifier for an entity.")

_host_option = click.option(
    *_HOST_FLAGS,
    required=False,
    help="The URL for the Flyte Admin Service. If you intend for this to be consistent, set the FLYTE_PLATFORM_URL "
    "environment variable to the desired URL and this will not need to be set.",
)
_token_option = click.option(
    "-t",
    "--token",
    required=False,
    default="",
    type=str,
    help="Pagination token from which to start listing in the list of results.",
)
_limit_option = click.option(
    "-l",
    "--limit",
    required=False,
    default=100,
    type=int,
    help="Maximum number of results to return for this call.",
)
_show_all_option = click.option(
    "-a",
    "--show-all",
    is_flag=True,
    default=False,
    help="Set this flag to page through and list all results.",
)
# TODO: Provide documentation on filter format
_filter_option = click.option(
    "-f",
    "--filter",
    multiple=True,
    help="""Filter to be applied.  Multiple filters can be applied and they will be ANDed together.
    Filters may be supplied as strings such as 'eq(name, workflow_name)'. Additional documentation on filter
    syntax can be found here: https://docs.flyte.org/en/latest/concepts/admin.html#adding-request-filters""",
)
_state_choice = click.option(
    "--state",
    type=click.Choice(["active", "inactive"]),
    required=True,
    help="Whether or not to set schedule as active.",
)
_named_entity_state_choice = click.option(
    "--state",
    type=click.Choice(["active", "archived"]),
    required=True,
    help="The state change to apply to a named entity",
)
_named_entity_description_option = click.option(
    "--description",
    required=False,
    type=str,
    help="Concise description for the entity.",
)
_sort_by_option = click.option(
    "--sort-by",
    required=False,
    help="Provide an entity field to be sorted.  i.e. asc(name) or desc(name)",
)
_show_io_option = click.option(
    "--show-io",
    is_flag=True,
    default=False,
    help="Set this flag to view inputs and outputs.  Pair with the --verbose flag to get the full textual description"
    " inputs and outputs.",
)
_verbose_option = click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Set this flag to view the full textual description of all fields.",
)

_filename_option = click.option("-f", "--filename", required=True, help="File path of pb file")
_idl_class_option = click.option(
    "-p",
    "--proto_class",
    required=True,
    help="Dot (.) separated path to Python IDL class. (e.g. flyteidl.core.workflow_closure_pb2.WorkflowClosure)",
)
_cause_option = click.option(
    "-c",
    "--cause",
    required=True,
    help="The message signaling the cause of the termination of the execution(s)",
)
