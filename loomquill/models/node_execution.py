import datetime
import typing
from datetime import timezone as _timezone

import flyteidl.admin.node_execution_pb2 as admin_node_execution_pb2

from flytekit.models import common as _common_models
from flytekit.models.core import catalog as catalog_models
from flytekit.models.core import compiler as core_compiler_models
from flytekit.models.core import execution as _core_execution
from flytekit.models.core import identifier as _identifier


class WorkflowNodeMetadata(_common_models.FlyteIdlEntity):
    def __init__(self, execution_id: _identifier.WorkflowExecutionIdentifier):
        self._execution_id = execution_id

    @property
    def execution_id(self) -> _identifier.WorkflowExecutionIdentifier:
        return self._execution_id

    def to_flyte_idl(self) -> admin_node_execution_pb2.WorkflowNodeMetadata:
        return admin_node_execution_pb2.WorkflowNodeMetadata(
            executionId=self.execution_id.to_flyte_idl(),
        )

    @classmethod
    def from_flyte_idl(cls, p: admin_node_execution_pb2.WorkflowNodeMetadata) -> "WorkflowNodeMetadata":
        return cls(
            execution_id=_identifier.WorkflowExecutionIdentifier.from_flyte_idl(p.executionId),
        )


class DynamicWorkflowNodeMetadata(_common_models.FlyteIdlEntity):
    def __init__(self, id: _identifier.Identifier, compiled_workflow: core_compiler_models.CompiledWorkflowClosure):
        self._id = id
        self._compiled_workflow = compiled_workflow

    @property
    def id(self) -> _identifier.Identifier:
        return self._id

    @property
    def compiled_workflow(self) -> core_compiler_models.CompiledWorkflowClosure:
        return self._compiled_workflow

    def to_flyte_idl(self) -> admin_node_execution_pb2.DynamicWorkflowNodeMetadata:
        return admin_node_execution_pb2.DynamicWorkflowNodeMetadata(
            id=self.id.to_flyte_idl(),
            compiled_workflow=self.compiled_workflow.to_flyte_idl(),
        )

    @classmethod
    def from_flyte_idl(cls, p: admin_node_execution_pb2.DynamicWorkflowNodeMetadata) -> "DynamicWorkflowNodeMetadata":
        yy = cls(
            id=_identifier.Identifier.from_flyte_idl(p.id),
            compiled_workflow=core_compiler_models.CompiledWorkflowClosure.from_flyte_idl(p.compiled_workflow),
        )
        return yy


class TaskNodeMetadata(_common_models.FlyteIdlEntity):
    def __init__(self, cache_status: int, catalog_key: catalog_models.CatalogMetadata):
        self._cache_status = cache_status
        self._catalog_key = catalog_key

    @property
    def cache_status(self) -> int:
        return self._cache_status

    @property
    def catalog_key(self) -> catalog_models.CatalogMetadata:
        return self._catalog_key

    def to_flyte_idl(self) -> admin_node_execution_pb2.TaskNodeMetadata:
        return admin_node_execution_pb2.TaskNodeMetadata(
            cache_status=self.cache_status,
            catalog_key=self.catalog_key.to_flyte_idl(),
        )

    @classmethod
    def from_flyte_idl(cls, p: admin_node_execution_pb2.TaskNodeMetadata) -> "TaskNodeMetadata":
        return cls(
            cache_status=p.cache_status,
            catalog_key=catalog_models.CatalogMetadata.from_flyte_idl(p.catalog_key),
