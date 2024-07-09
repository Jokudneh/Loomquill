import sys
import typing
from collections import OrderedDict
from typing import Callable, Dict, List, Optional, Tuple, Union

from flyteidl.admin import schedule_pb2

from flytekit import ImageSpec, PodTemplate, PythonFunctionTask, SourceCode
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core import constants as _common_constants
from flytekit.core import context_manager
from flytekit.core.array_node import ArrayNode
from flytekit.core.array_node_map_task import ArrayNodeMapTask
from flytekit.core.base_task import PythonTask
from flytekit.core.condition import BranchNode
from flytekit.core.container_task import ContainerTask
from flytekit.core.gate import Gate
from flytekit.core.launch_plan import LaunchPlan, ReferenceLaunchPlan
from flytekit.core.legacy_map_task import MapPythonTask
from flytekit.core.node import Node
from flytekit.core.options import Options
from flytekit.core.python_auto_container import (
    PythonAutoContainerTask,
)
from flytekit.core.python_function_task import EagerAsyncPythonFunctionTask
from flytekit.core.reference_entity import ReferenceEntity, ReferenceSpec, ReferenceTemplate
from flytekit.core.task import ReferenceTask
from flytekit.core.utils import ClassDecorator, _dnsify, _serialize_pod_spec
from flytekit.core.workflow import ReferenceWorkflow, WorkflowBase
from flytekit.models import common as _common_models
from flytekit.models import interface as interface_models
from flytekit.models import launch_plan as _launch_plan_models
from flytekit.models import security as _security_models
from flytekit.models.admin import workflow as admin_workflow_models
from flytekit.models.admin.workflow import WorkflowSpec
from flytekit.models.concurrency import ConcurrencyPolicy
from flytekit.models.core import identifier as _identifier_model
from flytekit.models.core import workflow as _core_wf
from flytekit.models.core import workflow as workflow_model
from flytekit.models.core.workflow import ApproveCondition, GateNode, SignalCondition, SleepCondition, TaskNodeOverrides
from flytekit.models.core.workflow import ArrayNode as ArrayNodeModel
from flytekit.models.core.workflow import BranchNode as BranchNodeModel
from flytekit.models.task import TaskSpec, TaskTemplate

FlyteLocalEntity = Union[
    PythonTask,
    BranchNode,
    Node,
    LaunchPlan,
    WorkflowBase,
    ReferenceWorkflow,
    ReferenceTask,
    ReferenceLaunchPlan,
    ReferenceEntity,
    ArrayNode,
]
FlyteControlPlaneEntity = Union[
    TaskSpec,
    _launch_plan_models.LaunchPlan,
    admin_workflow_models.WorkflowSpec,
    workflow_model.Node,
    BranchNodeModel,
    ArrayNodeModel,
]


def to_serializable_case(
    entity_mapping: OrderedDict,
    settings: SerializationSettings,
    c: _core_wf.IfBlock,
    options: Optional[Options] = None,
) -> _core_wf.IfBlock:
    if c is None:
        raise ValueError("Cannot convert none cases to registrable")
    then_node = get_serializable(entity_mapping, settings, c.then_node, options=options)
    return _core_wf.IfBlock(condition=c.condition, then_node=then_node)


def to_serializable_cases(
    entity_mapping: OrderedDict,
    settings: SerializationSettings,
    cases: List[_core_wf.IfBlock],
    options: Optional[Options] = None,
) -> Optional[List[_core_wf.IfBlock]]:
    if cases is None:
        return None
    ret_cases = []
    for c in cases:
        ret_cases.append(to_serializable_case(entity_mapping, settings, c, options))
    return ret_cases


def get_command_prefix_for_fast_execute(settings: SerializationSettings) -> List[str]:
    return [
        "pyflyte-fast-execute",
        "--additional-distribution",
        settings.fast_serialization_settings.distribution_location
        if settings.fast_serialization_settings and settings.fast_serialization_settings.distribution_location
        else "{{ .remote_package_path }}",
        "--dest-dir",
        settings.fast_serialization_settings.destination_dir
        if settings.fast_serialization_settings and settings.fast_serialization_settings.destination_dir
        else "{{ .dest_dir }}",
        "--",
    ]


def prefix_with_fast_execute(settings: SerializationSettings, cmd: typing.List[str]) -> List[str]:
    return get_command_prefix_for_fast_execute(settings) + cmd


def _fast_serialize_command_fn(
    settings: SerializationSettings, task: PythonAutoContainerTask
) -> Callable[[SerializationSettings], List[str]]:
    """
    This function is only applicable for Pod tasks.
    """
    default_command = task.get_default_command(settings)

    def fn(settings: SerializationSettings) -> List[str]:
        return prefix_with_fast_execute(settings, default_command)

    return fn


def get_serializable_task(
    entity_mapping: OrderedDict,
    settings: SerializationSettings,
    entity: FlyteLocalEntity,
    options: Optional[Options] = None,
) -> TaskSpec:
    task_id = _identifier_model.Identifier(
        _identifier_model.ResourceType.TASK,
        settings.project,
        settings.domain,
        entity.name,
        settings.version,
    )

    if isinstance(entity, PythonFunctionTask) and entity.execution_mode == PythonFunctionTask.ExecutionBehavior.DYNAMIC:
        for e in context_manager.FlyteEntities.entities:
            if isinstance(e, PythonAutoContainerTask):
                # 1. Build the ImageSpec for all the entities that are inside the current context,
                # 2. Add images to the serialization context, so the dynamic task can look it up at runtime.
                if isinstance(e.container_image, ImageSpec):
                    if settings.image_config.images is None:
                        settings.image_config = ImageConfig.create_from(settings.image_config.default_image)
                    img = Image.look_up_image_info(e.container_image.id, e.get_image(settings))
                    if img not in settings.image_config.images:
                        settings.image_config.images.append(img)

        # In case of Dynamic tasks, we want to pass the serialization context, so that they can reconstruct the state
        # from the serialization context. This is passed through an environment variable, that is read from
        # during dynamic serialization
        settings = settings.with_serialized_context()

        if entity.node_dependency_hints is not None:
            for entity_hint in entity.node_dependency_hints:
                get_serializable(entity_mapping, settings, entity_hint, options)

    if isinstance(entity, EagerAsyncPythonFunctionTask):
        settings = settings.with_serialized_context()

    container = entity.get_container(settings)
    # This pod will be incorrect when doing fast serialize
    pod = entity.get_k8s_pod(settings)

    if settings.should_fast_serialize():
        # This handles container tasks.
        if container and isinstance(entity, (PythonAutoContainerTask, MapPythonTask, ArrayNodeMapTask)):
            # For fast registration, we'll need to muck with the command, but on
            # ly for certain kinds of tasks. Specifically,
            # tasks that rely on user code defined in the container. This should be encapsulated by the auto container
            # parent class
            container._args = prefix_with_fast_execute(settings, container.args)

        # If the pod spec is not None, we have to get it again, because the one we retrieved above will be incorrect.
        # The reason we have to call get_k8s_pod again, instead of just modifying the command in this file, is because
        # the pod spec is a K8s library object, and we shouldn't be messing around with it in this file.
        elif pod and not isinstance(entity, ContainerTask):
            if isinstance(entity, (MapPythonTask, ArrayNodeMapTask)):
                entity.set_command_prefix(get_command_prefix_for_fast_execute(settings))
                pod = entity.get_k8s_pod(settings)
            else:
                entity.set_command_fn(_fast_serialize_command_fn(settings, entity))
                pod = entity.get_k8s_pod(settings)
                entity.reset_command_fn()

    entity_config = entity.get_config(settings) or {}
    extra_config = {}

    if hasattr(entity, "task_function"):
        if isinstance(entity.task_function, ClassDecorator):
            extra_config = entity.task_function.get_extra_config()
    if entity.enable_deck:
        entity.metadata.generates_deck = True

    merged_config = {**entity_config, **extra_config}

    tt = TaskTemplate(
        id=task_id,
        type=entity.task_type,
        metadata=entity.metadata.to_taskmetadata_model(),
        interface=entity.interface,
        custom=entity.get_custom(settings),
        container=container,
        task_type_version=entity.task_type_version,
        security_context=entity.security_context,
