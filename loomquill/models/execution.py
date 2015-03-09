from __future__ import annotations

import datetime
import typing
from datetime import timezone as _timezone
from typing import Optional

import flyteidl
import flyteidl.admin.cluster_assignment_pb2 as _cluster_assignment_pb2
import flyteidl.admin.execution_pb2 as _execution_pb2
import flyteidl.admin.node_execution_pb2 as _node_execution_pb2
import flyteidl.admin.task_execution_pb2 as _task_execution_pb2
from google.protobuf.wrappers_pb2 import BoolValue

from flytekit.models import common as _common_models
from flytekit.models import literals as _literals_models
from flytekit.models import security
from flytekit.models.core import execution as _core_execution
from flytekit.models.core import identifier as _identifier
from flytekit.models.matchable_resource import ExecutionClusterLabel
from flytekit.models.node_execution import DynamicWorkflowNodeMetadata


class SystemMetadata(_common_models.FlyteIdlEntity):
    def __init__(self, execution_cluster: str):
        self._execution_cluster = execution_cluster

    @property
    def execution_cluster(self) -> str:
        return self._execution_cluster

    def to_flyte_idl(self) -> flyteidl.admin.execution_pb2.SystemMetadata:
        return _execution_pb2.SystemMetadata(execution_cluster=self.execution_cluster)

    @classmethod
    def from_flyte_idl(cls, pb2_object: flyteidl.admin.execution_pb2.SystemMetadata) -> SystemMetadata:
        return cls(
            execution_cluster=pb2_object.execution_cluster,
        )


class ExecutionMetadata(_common_models.FlyteIdlEntity):
    class ExecutionMode(object):
        MANUAL = 0
        SCHEDULED = 1
        SYSTEM = 2

    def __init__(
        self,
        mode: int,
        principal: str,
        nesting: int,
        scheduled_at: Optional[datetime.datetime] = None,
        parent_node_execution: Optional[_identifier.NodeExecutionIdentifier] = None,
        reference_execution: Optional[_identifier.WorkflowExecutionIdentifier] = None,
        system_metadata: Optional[SystemMetadata] = None,
    ):
        """
        :param mode: An enum value from ExecutionMetadata.ExecutionMode which specifies how the job started.
        :param principal: The entity that triggered the execution
        :param nesting: An integer representing how deeply nested the workflow is (i.e. was it triggered by a parent
            workflow)
        :param scheduled_at: For scheduled executions, the requested time for execution for this specific schedule invocation.
        :param parent_node_execution: Which subworkflow node (if any) launched this execution
        :param reference_execution: Optional, reference workflow execution related to this execution
        :param system_metadata: Optional, platform-specific metadata about the execution.
        """
        self._mode = mode
        self._principal = principal
        self._nesting = nesting
        self._scheduled_at = scheduled_at
        self._parent_node_execution = parent_node_execution
        self._reference_execution = reference_execution
        self._system_metadata = system_metadata

    @property
    def mode(self) -> int:
        """
        An enum value from ExecutionMetadata.ExecutionMode which specifies how the job started.
        """
        return self._mode

    @property
    def principal(self) -> str:
        """
        The entity that triggered the execution
        """
        return self._principal

    @property
    def nesting(self) -> int:
        """
        An integer representing how deeply nested the workflow is (i.e. was it triggered by a parent workflow)
        """
        return self._nesting

    @property
    def scheduled_at(self) -> datetime.datetime:
        """
        For scheduled executions, the requested time for execution for this specific schedule invocation.
        """
        return self._scheduled_at

    @property
    def parent_node_execution(self) -> _identifier.NodeExecutionIdentifier:
        """
        Which subworkflow node (if any) launched this execution
        """
        return self._parent_node_execution

    @property
    def reference_execution(self) -> _identifier.WorkflowExecutionIdentifier:
        """
        Optional, reference workflow execution related to this execution
        """
        return self._reference_execution

    @property
    def system_metadata(self) -> SystemMetadata:
        """
        Optional, platform-specific metadata about the execution.
        """
        return self._system_metadata

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.admin.execution_pb2.ExecutionMetadata
        """
        p = _execution_pb2.ExecutionMetadata(
            mode=self.mode,
            principal=self.principal,
            nesting=self.nesting,
            parent_node_execution=self.parent_node_execution.to_flyte_idl()
            if self.parent_node_execution is not None
            else None,
            reference_execution=self.reference_execution.to_flyte_idl()
            if self.reference_execution is not None
            else None,
            system_metadata=self.system_metadata.to_flyte_idl() if self.system_metadata is not None else None,
        )
        if self.scheduled_at is not None:
            p.scheduled_at.FromDatetime(self.scheduled_at)
        return p

    @classmethod
    def from_flyte_idl(cls, pb2_object):
        """
        :param flyteidl.admin.execution_pb2.ExecutionMetadata pb2_object:
        :return: ExecutionMetadata
        """
        return cls(
            mode=pb2_object.mode,
            principal=pb2_object.principal,
            nesting=pb2_object.nesting,
            scheduled_at=pb2_object.scheduled_at.ToDatetime() if pb2_object.HasField("scheduled_at") else None,
            parent_node_execution=_identifier.NodeExecutionIdentifier.from_flyte_idl(pb2_object.parent_node_execution)
            if pb2_object.HasField("parent_node_execution")
            else None,
            reference_execution=_identifier.WorkflowExecutionIdentifier.from_flyte_idl(pb2_object.reference_execution)
            if pb2_object.HasField("reference_execution")
            else None,
            system_metadata=SystemMetadata.from_flyte_idl(pb2_object.system_metadata)
            if pb2_object.HasField("system_metadata")
            else None,
        )


class ExecutionSpec(_common_models.FlyteIdlEntity):
    def __init__(
        self,
        launch_plan,
        metadata,
        notifications=None,
        disable_all=None,
        labels=None,
        annotations=None,
        auth_role=None,
        raw_output_data_config=None,
        max_parallelism: Optional[int] = None,
        security_context: Optional[security.SecurityContext] = None,
        overwrite_cache: Optional[bool] = None,
        interruptible: Optional[bool] = None,
        envs: Optional[_common_models.Envs] = None,
        tags: Optional[typing.List[str]] = None,
        cluster_assignment: Optional[ClusterAssignment] = None,
        execution_cluster_label: Optional[ExecutionClusterLabel] = None,
    ):
        """
        :param flytekit.models.core.identifier.Identifier launch_plan: Launch plan unique identifier to execute
        :param ExecutionMetadata metadata: The metadata to be associated with this execution
        :param NotificationList notifications: List of notifications for this execution.
        :param bool disable_all: If true, all notifications should be disabled.
        :param flytekit.models.common.Labels labels: Labels to apply to the execution.
        :param flytekit.models.common.Annotations annotations: Annotations to apply to the execution
        :param flytekit.models.common.AuthRole auth_role: The authorization method with which to execute the workflow.
        :param raw_output_data_config: Optional location of offloaded data for things like S3, etc.
        :param max_parallelism int: Controls the maximum number of tasknodes that can be run in parallel for the entire
            workflow. This is useful to achieve fairness. Note: MapTasks are regarded as one unit, and
            parallelism/concurrency of MapTasks is independent from this.
        :param security_context: Optional security context to use for this execution.
        :param overwrite_cache: Optional flag to overwrite the cache for this execution.
        :param interruptible: Optional flag to override the default interruptible flag of the executed entity.
        :param envs: flytekit.models.common.Envs environment variables to set for this execution.
        :param tags: Optional list of tags to apply to the execution.
