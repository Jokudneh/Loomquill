import datetime
import json
import typing

from flyteidl.core import tasks_pb2
from flyteidl.core import workflow_pb2 as _core_workflow
from google.protobuf import json_format, struct_pb2
from google.protobuf.wrappers_pb2 import BoolValue

from flytekit.core.pod_template import PodTemplate
from flytekit.models import common as _common
from flytekit.models import interface as _interface
from flytekit.models import types as type_models
from flytekit.models.core import condition as _condition
from flytekit.models.core import identifier
from flytekit.models.core import identifier as _identifier
from flytekit.models.literals import Binding as _Binding
from flytekit.models.literals import RetryStrategy as _RetryStrategy
from flytekit.models.task import K8sObjectMetadata, Resources


class IfBlock(_common.FlyteIdlEntity):
    def __init__(self, condition, then_node):
        """
        Defines a condition and the execution unit that should be executed if the condition is satisfied.

        :param flytekit.models.core.condition.BooleanExpression condition:
        :param Node then_node:
        """

        self._condition = condition
        self._then_node = then_node

    @property
    def condition(self):
        """
        :rtype: flytekit.models.core.condition.BooleanExpression
        """
        return self._condition

    @property
    def then_node(self):
        """
        :rtype: Node
        """
        return self._then_node

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.core.workflow_pb2.IfBlock
        """
        return _core_workflow.IfBlock(condition=self.condition.to_flyte_idl(), then_node=self.then_node.to_flyte_idl())

    @classmethod
    def from_flyte_idl(cls, pb2_object):
        return cls(
            condition=_condition.BooleanExpression.from_flyte_idl(pb2_object.condition),
            then_node=Node.from_flyte_idl(pb2_object.then_node),
        )


class IfElseBlock(_common.FlyteIdlEntity):
    def __init__(self, case, other=None, else_node=None, error=None):
        """
        Defines a series of if/else blocks. The first branch whose condition evaluates to true is the one to execute.
        If no conditions were satisfied, the else_node or the error will execute.

        :param IfBlock case:
        :param list[IfBlock] other:
        :param Node else_node:
        :param type_models.Error error:
        """
        self._case = case
        self._other = other
        self._else_node = else_node
        self._error = error

    @property
    def case(self):
        """
        First condition to evaluate.

        :rtype: IfBlock
        """

        return self._case

    @property
    def other(self):
        """
        Additional branches to evaluate.

        :rtype: list[IfBlock]
        """

        return self._other

    @property
    def else_node(self):
        """
        The node to execute in case none of the branches were taken.

        :rtype: Node
        """

        return self._else_node

    @property
    def error(self):
        """
        An error to throw in case none of the branches were taken.

        :rtype: flytekit.models.types.Error
        """

        return self._error

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.core.workflow_pb2.IfElseBlock
        """
        return _core_workflow.IfElseBlock(
            case=self.case.to_flyte_idl(),
            other=[a.to_flyte_idl() for a in self.other] if self.other else None,
            else_node=self.else_node.to_flyte_idl() if self.else_node else None,
            error=self.error.to_flyte_idl() if self.error else None,
        )

    @classmethod
    def from_flyte_idl(cls, pb2_object):
        return cls(
            case=IfBlock.from_flyte_idl(pb2_object.case),
            other=[IfBlock.from_flyte_idl(a) for a in pb2_object.other],
            else_node=Node.from_flyte_idl(pb2_object.else_node) if pb2_object.HasField("else_node") else None,
            error=type_models.Error.from_flyte_idl(pb2_object.error) if pb2_object.HasField("error") else None,
        )


class BranchNode(_common.FlyteIdlEntity):
    def __init__(self, if_else: IfElseBlock):
        """
        BranchNode is a special node that alter the flow of the workflow graph. It allows the control flow to branch at
        runtime based on a series of conditions that get evaluated on various parameters (e.g. inputs, primitives).

        :param IfElseBlock if_else:
        """

        self._if_else = if_else

    @property
    def if_else(self) -> IfElseBlock:
        """
        :rtype: IfElseBlock
        """

        return self._if_else

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.core.workflow_pb2.BranchNode
        """
        return _core_workflow.BranchNode(if_else=self.if_else.to_flyte_idl())

    @classmethod
    def from_flyte_idl(cls, pb2_objct):
        return cls(if_else=IfElseBlock.from_flyte_idl(pb2_objct.if_else))


class NodeMetadata(_common.FlyteIdlEntity):
    def __init__(
        self,
        name,
        timeout=None,
        retries=None,
        interruptible: typing.Optional[bool] = None,
        cacheable: typing.Optional[bool] = None,
        cache_version: typing.Optional[str] = None,
        cache_serializable: typing.Optional[bool] = None,
    ):
        """
        Defines extra information about the Node.

        :param Text name: Friendly name for the Node.
        :param datetime.timedelta timeout: [Optional] Overall timeout for a task.
        :param flytekit.models.literals.RetryStrategy retries: [Optional] Number of retries per task.
        :param bool interruptible: Can be safely interrupted during execution.
        :param cacheable: Indicates that this nodes outputs should be cached.
        :param cache_version: The version of the cached data.
        :param cacheable: Indicates that cache operations on this node should be serialized.
        """
        self._name = name
        self._timeout = timeout if timeout is not None else datetime.timedelta()
        self._retries = retries if retries is not None else _RetryStrategy(0)
        self._interruptible = interruptible
        self._cacheable = cacheable
        self._cache_version = cache_version
        self._cache_serializable = cache_serializable

    @property
    def name(self):
        """
        :rtype: Text
        """
        return self._name

    @property
    def timeout(self):
        """
        :rtype: datetime.timedelta
        """
        return self._timeout

    @property
    def retries(self):
        """
        :rtype: flytekit.models.literals.RetryStrategy
        """
        return self._retries

    @property
    def interruptible(self) -> typing.Optional[bool]:
        return self._interruptible

    @property
    def cacheable(self) -> typing.Optional[bool]:
        return self._cacheable

    @property
    def cache_version(self) -> typing.Optional[str]:
        return self._cache_version

    @property
    def cache_serializable(self) -> typing.Optional[bool]:
        return self._cache_serializable

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.core.workflow_pb2.NodeMetadata
        """
        node_metadata = _core_workflow.NodeMetadata(
            name=self.name,
            retries=self.retries.to_flyte_idl(),
            interruptible=self.interruptible,
            cacheable=self.cacheable,
            cache_version=self.cache_version,
            cache_serializable=self.cache_serializable,
        )
        if self.timeout:
            node_metadata.timeout.FromTimedelta(self.timeout)
        return node_metadata

    @classmethod
    def from_flyte_idl(cls, pb2_object):
        return cls(
            pb2_object.name,
            pb2_object.timeout.ToTimedelta(),
            _RetryStrategy.from_flyte_idl(pb2_object.retries),
            pb2_object.interruptible if pb2_object.HasField("interruptible") else None,
            pb2_object.cacheable if pb2_object.HasField("cacheable") else None,
            pb2_object.cache_version if pb2_object.HasField("cache_version") else None,
            pb2_object.cache_serializable if pb2_object.HasField("cache_serializable") else None,
        )


class SignalCondition(_common.FlyteIdlEntity):
    def __init__(self, signal_id: str, type: type_models.LiteralType, output_variable_name: str):
        """
        Represents a dependency on an signal from a user.

        :param signal_id: The node id of the signal, also the signal name.
        :param type:
        """
        self._signal_id = signal_id
        self._type = type
        self._output_variable_name = output_variable_name

    @property
    def signal_id(self) -> str:
        return self._signal_id

    @property
    def type(self) -> type_models.LiteralType:
        return self._type

    @property
    def output_variable_name(self) -> str:
        return self._output_variable_name

    def to_flyte_idl(self) -> _core_workflow.SignalCondition:
        return _core_workflow.SignalCondition(
            signal_id=self.signal_id, type=self.type.to_flyte_idl(), output_variable_name=self.output_variable_name
        )

    @classmethod
    def from_flyte_idl(cls, pb2_object: _core_workflow.SignalCondition):
        return cls(
            signal_id=pb2_object.signal_id,
            type=type_models.LiteralType.from_flyte_idl(pb2_object.type),
            output_variable_name=pb2_object.output_variable_name,
        )


class ApproveCondition(_common.FlyteIdlEntity):
    def __init__(self, signal_id: str):
        """
        Represents a dependency on an signal from a user.

        :param signal_id: The node id of the signal, also the signal name.
        """
        self._signal_id = signal_id

    @property
    def signal_id(self) -> str:
        return self._signal_id

    def to_flyte_idl(self) -> _core_workflow.ApproveCondition:
        return _core_workflow.ApproveCondition(signal_id=self.signal_id)

    @classmethod
    def from_flyte_idl(cls, pb2_object: _core_workflow.ApproveCondition):
        return cls(signal_id=pb2_object.signal_id)
