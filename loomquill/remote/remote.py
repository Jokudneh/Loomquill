"""
This module provides the ``FlyteRemote`` object, which is the end-user's main starting point for interacting
with a Flyte backend in an interactive and programmatic way. This of this experience as kind of like the web UI
but in Python object form.
"""

from __future__ import annotations

import asyncio
import base64
import configparser
import contextlib
import functools
import gzip
import hashlib
import os
import pathlib
import tempfile
import time
import typing
import uuid
from base64 import b64encode
from collections import OrderedDict
from dataclasses import asdict, dataclass
from dataclasses import replace as dc_replace
from datetime import datetime, timedelta
from typing import Dict

import click
import cloudpickle
import fsspec
import requests
from flyteidl.admin.signal_pb2 import Signal, SignalListRequest, SignalSetRequest
from flyteidl.core import literals_pb2
from rich.progress import Progress, TextColumn, TimeElapsedColumn

from flytekit import ImageSpec, PodTemplate
from flytekit.clients.friendly import SynchronousFlyteClient
from flytekit.clients.grpc_utils.deadline_interceptor import get_scoped_grpc_deadline, scoped_grpc_deadline
from flytekit.clients.helpers import iterate_node_executions, iterate_task_executions
from flytekit.configuration import Config, DataConfig, FastSerializationSettings, ImageConfig, SerializationSettings
from flytekit.configuration.file import ConfigFile
from flytekit.constants import CopyFileDetection
from flytekit.core import constants, utils
from flytekit.core.array_node import ArrayNode
from flytekit.core.array_node_map_task import ArrayNodeMapTask
from flytekit.core.artifact import Artifact
from flytekit.core.base_task import PythonTask
from flytekit.core.context_manager import FlyteContext, FlyteContextManager
from flytekit.core.data_persistence import FileAccessProvider
from flytekit.core.launch_plan import LaunchPlan, ReferenceLaunchPlan
from flytekit.core.node import Node as CoreNode
from flytekit.core.promise import translate_inputs_to_literals
from flytekit.core.python_auto_container import (
    PICKLE_FILE_PATH,
    PickledEntity,
    PickledEntityMetadata,
    PythonAutoContainerTask,
    default_notebook_task_resolver,
)
from flytekit.core.python_function_task import PythonFunctionTask
from flytekit.core.reference_entity import ReferenceEntity, ReferenceSpec
from flytekit.core.resources import ResourceSpec
from flytekit.core.task import ReferenceTask
from flytekit.core.tracker import extract_task_module
from flytekit.core.type_engine import LiteralsResolver, TypeEngine, strict_type_hint_matching
from flytekit.core.workflow import PythonFunctionWorkflow, ReferenceWorkflow, WorkflowBase, WorkflowFailurePolicy
from flytekit.exceptions import user as user_exceptions
from flytekit.exceptions.user import (
    FlyteAssertion,
    FlyteEntityAlreadyExistsException,
    FlyteEntityNotExistException,
    FlyteValueException,
)
from flytekit.loggers import developer_logger, is_display_progress_enabled, logger
from flytekit.models import common as common_models
from flytekit.models import filters as filter_models
from flytekit.models import launch_plan as launch_plan_models
from flytekit.models import literals as literal_models
from flytekit.models import task as task_models
from flytekit.models import types as type_models
from flytekit.models.admin import common as admin_common_models
from flytekit.models.admin import workflow as admin_workflow_models
from flytekit.models.admin.common import Sort
from flytekit.models.common import NamedEntityIdentifier
from flytekit.models.core import identifier as id_models
from flytekit.models.core import workflow as workflow_model
from flytekit.models.core.identifier import Identifier, ResourceType, SignalIdentifier, WorkflowExecutionIdentifier
from flytekit.models.core.workflow import BranchNode, Node, NodeMetadata
from flytekit.models.domain import Domain
from flytekit.models.execution import (
    ClusterAssignment,
    ExecutionMetadata,
    ExecutionSpec,
    NodeExecutionGetDataResponse,
    NotificationList,
    WorkflowExecutionGetDataResponse,
)
from flytekit.models.launch_plan import LaunchPlanState
from flytekit.models.literals import Literal, LiteralMap
from flytekit.models.matchable_resource import ExecutionClusterLabel
from flytekit.models.project import Project
from flytekit.remote.backfill import create_backfill_workflow
from flytekit.remote.data import download_literal
from flytekit.remote.entities import (
    FlyteBranchNode,
    FlyteLaunchPlan,
    FlyteNode,
    FlyteTask,
    FlyteTaskNode,
    FlyteWorkflow,
)
from flytekit.remote.executions import FlyteNodeExecution, FlyteTaskExecution, FlyteWorkflowExecution
from flytekit.remote.interface import TypedInterface
from flytekit.remote.lazy_entity import LazyEntity
from flytekit.remote.metrics import FlyteExecutionSpan
from flytekit.remote.remote_callable import RemoteEntity
from flytekit.remote.remote_fs import get_flyte_fs
from flytekit.tools.fast_registration import FastPackageOptions, fast_package
from flytekit.tools.interactive import ipython_check
from flytekit.tools.script_mode import _find_project_root, compress_scripts, get_all_modules, hash_file
from flytekit.tools.translator import (
    FlyteControlPlaneEntity,
    FlyteLocalEntity,
    Options,
    get_serializable,
    get_serializable_launch_plan,
)
from flytekit.utils.asyn import run_sync

if typing.TYPE_CHECKING:
    try:
        from IPython.core.display import HTML
    except ImportError:
        ...

ExecutionDataResponse = typing.Union[WorkflowExecutionGetDataResponse, NodeExecutionGetDataResponse]

MOST_RECENT_FIRST = admin_common_models.Sort("created_at", admin_common_models.Sort.Direction.DESCENDING)

LATEST_VERSION_STR = "latest"

DEFAULT_SYNC_EXECUTION_RPC_TIMEOUT = timedelta(seconds=60)


def _get_rpc_timeout_seconds(rpc_timeout: typing.Optional[typing.Union[timedelta, int]]) -> typing.Optional[float]:
    if rpc_timeout is None:
        return None
    if isinstance(rpc_timeout, timedelta):
        return rpc_timeout.total_seconds()
    return float(rpc_timeout)


class RegistrationSkipped(Exception):
    """
    RegistrationSkipped error is raised when trying to register an entity that is not registrable.
    """

    pass


@dataclass
class ResolvedIdentifiers:
    project: str
    domain: str
    name: str
    version: str


def _get_latest_version(list_entities_method: typing.Callable, project: str, domain: str, name: str):
    named_entity = common_models.NamedEntityIdentifier(project, domain, name)
    entity_list, _ = list_entities_method(
        named_entity,
        limit=1,
        sort_by=Sort("created_at", Sort.Direction.DESCENDING),
    )
    admin_entity = None if not entity_list else entity_list[0]
    if not admin_entity:
        raise user_exceptions.FlyteEntityNotExistException("Named entity {} not found".format(named_entity))
    return admin_entity.id.version


def _get_entity_identifier(
    list_entities_method: typing.Callable,
    resource_type: int,  # from flytekit.models.core.identifier.ResourceType
    project: str,
    domain: str,
    name: str,
    version: typing.Optional[str] = None,
):
    if version is None or version == LATEST_VERSION_STR:
        version = _get_latest_version(list_entities_method, project, domain, name)
    return Identifier(
        resource_type,
        project,
        domain,
        name,
        version,
    )


def _get_git_repo_url(source_path: str):
    """
    Get git repo URL from remote.origin.url
    """
    try:
        git_config = pathlib.Path(source_path) / ".git" / "config"
        if not git_config.exists():
            raise ValueError(f"{source_path} is not a git repo")

        config = configparser.ConfigParser()
        config.read(git_config)
        url = config['remote "origin"']["url"]

        if url.startswith("git@"):
            # url format: git@github.com:flytekit/flytekit.git
            prefix_len, suffix_len = len("git@"), len(".git")
            return url[prefix_len:-suffix_len].replace(":", "/")
        elif url.startswith("https://"):
            # url format: https://github.com/flytekit/flytekit
            prefix_len = len("https://")
            return url[prefix_len:]
        elif url.startswith("http://"):
            # url format: http://github.com/flytekit/flytekit
            prefix_len = len("http://")
            return url[prefix_len:]
        else:
            raise ValueError("Unable to parse url")

    except Exception as e:
        logger.debug(f"unable to find the git config in {source_path} with error: {str(e)}")
        return ""


@functools.lru_cache
def _get_pickled_target_dict(
    root_entity: typing.Union[WorkflowBase, PythonTask],
) -> typing.Tuple[bytes, PickledEntity]:
    """
    Get the pickled target dictionary for the entity.
    :param root_entity: The entity to get the pickled target for.
        :return: hashed bytes and the pickled target dictionary.
    """
    import sys

    queue: typing.List[typing.Union[WorkflowBase, PythonTask, CoreNode]] = [root_entity]
    pickled_target_dict = PickledEntity(
        metadata=PickledEntityMetadata(
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        ),
        entities={},
    )
    while queue:
        entity = queue.pop()
        if isinstance(entity, PythonFunctionTask):
            if entity.execution_mode == PythonFunctionTask.ExecutionBehavior.DYNAMIC:
                raise FlyteAssertion(
                    f"Dynamic tasks are not supported in interactive mode. {entity.name} is a dynamic task."
                )
            if entity.execution_mode == PythonFunctionTask.ExecutionBehavior.EAGER:
                raise FlyteAssertion(
                    f"Eager tasks are not supported in interactive mode. {entity.name} is an eager task."
                )

        if isinstance(entity, ArrayNode):
            # extract WorkflowBase from ArrayNode
            entity = entity.target.workflow

        if isinstance(entity, PythonTask):
            if isinstance(entity, (PythonAutoContainerTask, ArrayNodeMapTask)):
                if isinstance(entity, ArrayNodeMapTask):
                    entity._run_task.set_resolver(default_notebook_task_resolver)
                    pickled_target_dict.entities[entity._run_task.name] = entity._run_task
                else:
                    entity.set_resolver(default_notebook_task_resolver)
                    pickled_target_dict.entities[entity.name] = entity
        elif isinstance(entity, WorkflowBase):
            for task in entity.nodes:
                queue.append(task)
        elif isinstance(entity, CoreNode):
            queue.append(entity.flyte_entity)
    md5_bytes = hashlib.md5(cloudpickle.dumps(pickled_target_dict)).digest()
    return md5_bytes, pickled_target_dict


class FlyteRemote(object):
    """Main entrypoint for programmatically accessing a Flyte remote backend.

    The term 'remote' is synonymous with 'backend' or 'deployment' and refers to a hosted instance of the
    Flyte platform, which comes with a Flyte Admin server on some known URI.
    """

    def __init__(
        self,
        config: Config,
        default_project: typing.Optional[str] = None,
        default_domain: typing.Optional[str] = None,
        data_upload_location: str = "flyte://my-s3-bucket/",
        interactive_mode_enabled: typing.Optional[bool] = None,
        **kwargs,
    ):
        """Initialize a FlyteRemote object.

        :type kwargs: All arguments that can be passed to create the SynchronousFlyteClient. These are usually grpc
            parameters, if you want to customize credentials, ssl handling etc.
        :param default_project: default project to use when fetching or executing flyte entities.
        :param default_domain: default domain to use when fetching or executing flyte entities.
        :param data_upload_location: this is where all the default data will be uploaded when providing inputs.
            The default location - `s3://my-s3-bucket/data` works for sandbox/demo environment. Please override this for non-sandbox cases.
        :param interactive_mode_enabled: If set to True, the FlyteRemote will pickle the task/workflow, if False,
         it will not. If set to None, then it will automatically detect if it is running in an interactive environment
         like a Jupyter notebook and enable interactive mode.
        """
        if config is None or config.platform is None or config.platform.endpoint is None:
            raise user_exceptions.FlyteAssertion("Flyte endpoint should be provided.")

        if interactive_mode_enabled is None:
            interactive_mode_enabled = ipython_check()

        if interactive_mode_enabled is True:
            logger.warning("Jupyter notebook and interactive task support is still alpha.")

        if data_upload_location is None:
            data_upload_location = FlyteContext.current_context().file_access.raw_output_prefix
        self._kwargs = kwargs
        self._client_initialized = False
        self._config = config
        # read config files, env vars, host, ssl options for admin client
        self._default_project = default_project
        self._default_domain = default_domain

        fsspec.register_implementation("flyte", get_flyte_fs(remote=self), clobber=True)

        self._file_access = FileAccessProvider(
            local_sandbox_dir=os.path.join(config.local_sandbox_path, "control_plane_metadata"),
            raw_output_prefix=data_upload_location,
            data_config=config.data_config,
        )

        # Save the file access object locally, build a context for it and save that as well.
        self._ctx = FlyteContextManager.current_context().with_file_access(self._file_access).build()
        self._interactive_mode_enabled = interactive_mode_enabled

    @property
    def context(self) -> FlyteContext:
        return self._ctx

    @property
    def client(self) -> SynchronousFlyteClient:
        """Return a SynchronousFlyteClient for additional operations."""
        if not self._client_initialized:
            self._client = SynchronousFlyteClient(self.config.platform, **self._kwargs)
            self._client_initialized = True
        return self._client

    @property
    def default_project(self) -> str:
        """Default project to use when fetching or executing flyte entities."""
        return self._default_project

    @property
    def default_domain(self) -> str:
        """Default project to use when fetching or executing flyte entities."""
        return self._default_domain

    @property
    def config(self) -> Config:
        """Image config."""
        return self._config

    @property
    def file_access(self) -> FileAccessProvider:
        """File access provider to use for offloading non-literal inputs/outputs."""
        return self._file_access

    @property
    def interactive_mode_enabled(self) -> bool:
        """If set to True, the FlyteRemote will pickle the task/workflow."""
        return self._interactive_mode_enabled

    def get(
        self, flyte_uri: typing.Optional[str] = None
    ) -> typing.Optional[typing.Union[LiteralsResolver, Literal, HTML, bytes]]:
        """
        General function that works with flyte tiny urls. This can return outputs (in the form of LiteralsResolver, or
        individual Literals for singular requests), or HTML if passed a deck link, or bytes containing HTML,
        if ipython is not available locally.
        """
        if flyte_uri is None:
            raise user_exceptions.FlyteUserException("flyte_uri cannot be empty")
        ctx = self._ctx or FlyteContextManager.current_context()
        try:
            data_response = self.client.get_data(flyte_uri)

            if data_response.HasField("literal_map"):
                lm = LiteralMap.from_flyte_idl(data_response.literal_map)
                return LiteralsResolver(lm.literals)
            elif data_response.HasField("literal"):
                return Literal.from_flyte_idl(data_response.literal)
            elif data_response.HasField("pre_signed_urls"):
                if len(data_response.pre_signed_urls.signed_url) == 0:
                    raise ValueError(f"Flyte url {flyte_uri} resolved to empty download link")
                d = data_response.pre_signed_urls.signed_url[0]
                logger.debug(f"Download link is {d}")
                fs = ctx.file_access.get_filesystem_for_path(d)

                # If the venv has IPython, then return IPython's HTML
                if ipython_check():
                    from IPython.core.display import HTML

                    logger.debug(f"IPython found, returning HTML from {flyte_uri}")
                    with fs.open(d, "rb") as r:
                        html = HTML(str(r.read()))
                        return html
                # If not return bytes
                else:
                    logger.debug(f"IPython not found, returning HTML as bytes from {flyte_uri}")
                    return fs.open(d, "rb").read()

        except user_exceptions.FlyteUserException as e:
            logger.info(f"Error from Flyte backend when trying to fetch data: {e.__cause__}")

        logger.info(f"Nothing found from {flyte_uri}")

    def remote_context(self):
        """Context manager with remote-specific configuration."""
        return FlyteContextManager.with_context(
            FlyteContextManager.current_context().with_file_access(self.file_access)
        )

    def fetch_task_lazy(
        self, project: str = None, domain: str = None, name: str = None, version: str = None
    ) -> LazyEntity:
        """
        Similar to fetch_task, just that it returns a LazyEntity, which will fetch the workflow lazily.
        """
        if name is None:
            raise user_exceptions.FlyteAssertion("the 'name' argument must be specified.")

        def _fetch():
            return self.fetch_task(project=project, domain=domain, name=name, version=version)

        return LazyEntity(name=name, getter=_fetch)

    def fetch_task(self, project: str = None, domain: str = None, name: str = None, version: str = None) -> FlyteTask:
        """Fetch a task entity from flyte admin.

        :param project: fetch entity from this project. If None, uses the default_project attribute.
        :param domain: fetch entity from this domain. If None, uses the default_domain attribute.
        :param name: fetch entity with matching name.
        :param version: fetch entity with matching version. If None, gets the latest version of the entity.
        :returns: :class:`~flytekit.remote.tasks.task.FlyteTask`

        :raises: FlyteAssertion if name is None
        """
        if name is None:
            raise user_exceptions.FlyteAssertion("the 'name' argument must be specified.")
        task_id = _get_entity_identifier(
            self.client.list_tasks_paginated,
            ResourceType.TASK,
            project or self.default_project,
            domain or self.default_domain,
            name,
            version,
        )
        admin_task = self.client.get_task(task_id)
        flyte_task = FlyteTask.promote_from_model(admin_task.closure.compiled_task.template)
        flyte_task.template._id = task_id
        return flyte_task

    def fetch_workflow_lazy(
        self, project: str = None, domain: str = None, name: str = None, version: str = None
    ) -> LazyEntity[FlyteWorkflow]:
        """
        Similar to fetch_workflow, just that it returns a LazyEntity, which will fetch the workflow lazily.
        """
        if name is None:
            raise user_exceptions.FlyteAssertion("the 'name' argument must be specified.")

        def _fetch():
            return self.fetch_workflow(project, domain, name, version)

        return LazyEntity(name=name, getter=_fetch)

    def fetch_workflow(
        self, project: str = None, domain: str = None, name: str = None, version: str = None
    ) -> FlyteWorkflow:
        """
        Fetch a workflow entity from flyte admin.
        :param project: fetch entity from this project. If None, uses the default_project attribute.
        :param domain: fetch entity from this domain. If None, uses the default_domain attribute.
        :param name: fetch entity with matching name.
        :param version: fetch entity with matching version. If None, gets the latest version of the entity.
        :raises: FlyteAssertion if name is None
        """
        if name is None:
            raise user_exceptions.FlyteAssertion("the 'name' argument must be specified.")
        workflow_id = _get_entity_identifier(
            self.client.list_workflows_paginated,
            ResourceType.WORKFLOW,
            project or self.default_project,
            domain or self.default_domain,
            name,
            version,
        )

        admin_workflow = self.client.get_workflow(workflow_id)
        compiled_wf = admin_workflow.closure.compiled_workflow

        wf_templates = [compiled_wf.primary.template]
        wf_templates.extend([swf.template for swf in compiled_wf.sub_workflows])

        node_launch_plans = {}
        for wf_template in wf_templates:
            for node in FlyteWorkflow.get_non_system_nodes(wf_template.nodes):
                self.find_launch_plan_for_node(node, node_launch_plans)

        flyte_workflow = FlyteWorkflow.promote_from_closure(compiled_wf, node_launch_plans)
        flyte_workflow.template._id = workflow_id
        return flyte_workflow

    def _upgrade_launchplan(self, lp: launch_plan_models.LaunchPlan) -> FlyteLaunchPlan:
        """
        Given a remote returned launchplan, upgrade it to a FlyteLaunchPlan object that holds the interface and
        the FlyteWorkflow object. This can be used in the SDK.
        """
        flyte_lp = FlyteLaunchPlan.promote_from_model(lp.id, lp.spec)
        wf_id = flyte_lp.workflow_id
        workflow = self.fetch_workflow(wf_id.project, wf_id.domain, wf_id.name, wf_id.version)
        flyte_lp._interface = workflow.interface
        flyte_lp._flyte_workflow = workflow
        return flyte_lp

    def find_launch_plan(
        self, lp_ref: id_models, node_launch_plans: Dict[id_models, launch_plan_models.LaunchPlanSpec]
    ) -> None:
        if lp_ref not in node_launch_plans:
            admin_launch_plan = self.client.get_launch_plan(lp_ref)
            node_launch_plans[lp_ref] = admin_launch_plan.spec

    def find_launch_plan_for_node(
        self, node: Node, node_launch_plans: Dict[id_models, launch_plan_models.LaunchPlanSpec]
    ):
        # Case 1: workflow node
        if node.workflow_node is not None and node.workflow_node.launchplan_ref is not None:
            lp_ref = node.workflow_node.launchplan_ref
            self.find_launch_plan(lp_ref, node_launch_plans)

        # Case 2: array node
        if (
            node.array_node is not None
            and node.array_node.node.workflow_node is not None
            and node.array_node.node.workflow_node.launchplan_ref is not None
        ):
            lp_ref = node.array_node.node.workflow_node.launchplan_ref
            self.find_launch_plan(lp_ref, node_launch_plans)

        # Case 3: branch node
        def get_launch_plan_from_branch(
            branch_node: BranchNode, node_launch_plans: Dict[id_models, launch_plan_models.LaunchPlanSpec]
        ) -> None:
            def get_launch_plan_from_then_node(
                child_then_node: Node, node_launch_plans: Dict[id_models, launch_plan_models.LaunchPlanSpec]
            ) -> None:
                #  then_node could have nested branch_node or be a normal then_node
                if child_then_node.branch_node:
                    get_launch_plan_from_branch(child_then_node.branch_node, node_launch_plans)
                elif child_then_node.workflow_node and child_then_node.workflow_node.launchplan_ref:
                    lp_ref = child_then_node.workflow_node.launchplan_ref
                    self.find_launch_plan(lp_ref, node_launch_plans)

            if branch_node and branch_node.if_else:
                branch = branch_node.if_else
                if branch.case and branch.case.then_node:
                    child_then_node = branch.case.then_node
                    get_launch_plan_from_then_node(child_then_node, node_launch_plans)
                if branch.other:
                    for o in branch.other:
                        if o.then_node:
                            child_then_node = o.then_node
                            get_launch_plan_from_then_node(child_then_node, node_launch_plans)
                if branch.else_node:
                    #  else_node could have nested conditional branch_node
                    if branch.else_node.branch_node:
                        get_launch_plan_from_branch(branch.else_node.branch_node, node_launch_plans)
                    elif branch.else_node.workflow_node and branch.else_node.workflow_node.launchplan_ref:
                        lp_ref = branch.else_node.workflow_node.launchplan_ref
                        self.find_launch_plan(lp_ref, node_launch_plans)

        if node.branch_node:
            get_launch_plan_from_branch(node.branch_node, node_launch_plans)

    def fetch_active_launchplan(
        self, project: str = None, domain: str = None, name: str = None
    ) -> typing.Optional[FlyteLaunchPlan]:
        """
        Returns the active version of the launch plan if it exists or returns None
        """
        try:
            lp = self.client.get_active_launch_plan(
                NamedEntityIdentifier(project or self.default_project, domain or self.default_domain, name)
            )
            if lp is not None:
                return self._upgrade_launchplan(lp)
        except FlyteEntityNotExistException as e:
            logger.debug(f"Launch plan not found, error:{str(e)}")
        return None

    def fetch_launch_plan(
        self, project: str = None, domain: str = None, name: str = None, version: str = None
    ) -> FlyteLaunchPlan:
        """Fetch a launchplan entity from flyte admin.

        :param project: fetch entity from this project. If None, uses the default_project attribute.
        :param domain: fetch entity from this domain. If None, uses the default_domain attribute.
        :param name: fetch entity with matching name.
        :param version: fetch entity with matching version. If None, gets the latest version of the entity.
        :returns: :class:`~flytekit.remote.launch_plan.FlyteLaunchPlan`

        :raises: FlyteAssertion if name is None
        """
        if name is None:
            raise user_exceptions.FlyteAssertion("the 'name' argument must be specified.")
        launch_plan_id = _get_entity_identifier(
            self.client.list_launch_plans_paginated,
            ResourceType.LAUNCH_PLAN,
            project or self.default_project,
            domain or self.default_domain,
            name,
            version,
        )
        admin_launch_plan = self.client.get_launch_plan(launch_plan_id)
        return self._upgrade_launchplan(admin_launch_plan)

    def fetch_execution(self, project: str = None, domain: str = None, name: str = None) -> FlyteWorkflowExecution:
        """Fetch a workflow execution entity from flyte admin.

        :param project: fetch entity from this project. If None, uses the default_project attribute.
        :param domain: fetch entity from this domain. If None, uses the default_domain attribute.
        :param name: fetch entity with matching name.
        :returns: :class:`~flytekit.remote.workflow_execution.FlyteWorkflowExecution`

        :raises: FlyteAssertion if name is None
        """
        if name is None:
            raise user_exceptions.FlyteAssertion("the 'name' argument must be specified.")
        execution = FlyteWorkflowExecution.promote_from_model(
            self.client.get_execution(
                WorkflowExecutionIdentifier(
                    project or self.default_project,
                    domain or self.default_domain,
                    name,
                )
