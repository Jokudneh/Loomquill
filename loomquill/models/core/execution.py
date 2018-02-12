import datetime
import typing

from flyteidl.core import execution_pb2 as _execution_pb2

from flytekit.models import common as _common


class WorkflowExecutionPhase(object):
    """
    This class holds enum values used for setting notifications. See {{< py_class_ref flytekit.Email >}}
    for sample usage.
    """

    UNDEFINED = _execution_pb2.WorkflowExecution.UNDEFINED
    QUEUED = _execution_pb2.WorkflowExecution.QUEUED
    RUNNING = _execution_pb2.WorkflowExecution.RUNNING
    SUCCEEDING = _execution_pb2.WorkflowExecution.SUCCEEDING
    SUCCEEDED = _execution_pb2.WorkflowExecution.SUCCEEDED
    FAILING = _execution_pb2.WorkflowExecution.FAILING
    FAILED = _execution_pb2.WorkflowExecution.FAILED
    ABORTED = _execution_pb2.WorkflowExecution.ABORTED
    TIMED_OUT = _execution_pb2.WorkflowExecution.TIMED_OUT
    ABORTING = _execution_pb2.WorkflowExecution.ABORTING

    @classmethod
    def enum_to_string(cls, int_value):
        """
        :param int_value:
        :rtype: Text
        """
        for name, value in cls.__dict__.items():
            if value == int_value:
                return name
        return str(int_value)


class NodeExecutionPhase(object):
    UNDEFINED = _execution_pb2.NodeExecution.UNDEFINED
    QUEUED = _execution_pb2.NodeExecution.QUEUED
    RUNNING = _execution_pb2.NodeExecution.RUNNING
    SUCCEEDED = _execution_pb2.NodeExecution.SUCCEEDED
    FAILING = _execution_pb2.NodeExecution.FAILING
    FAILED = _execution_pb2.NodeExecution.FAILED
    ABORTED = _execution_pb2.NodeExecution.ABORTED
    SKIPPED = _execution_pb2.NodeExecution.SKIPPED
    TIMED_OUT = _execution_pb2.NodeExecution.TIMED_OUT
    DYNAMIC_RUNNING = _execution_pb2.NodeExecution.DYNAMIC_RUNNING
    RECOVERED = _execution_pb2.NodeExecution.RECOVERED

    @classmethod
    def enum_to_string(cls, int_value):
        """
        :param int_value:
        :rtype: Text
        """
        for name, value in cls.__dict__.items():
            if value == int_value:
                return name
