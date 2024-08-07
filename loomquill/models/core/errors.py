from flyteidl.core import errors_pb2 as _errors_pb2
from google.protobuf.timestamp_pb2 import Timestamp

from flytekit.models import common as _common


class ContainerError(_common.FlyteIdlEntity):
    class Kind(object):
        NON_RECOVERABLE = _errors_pb2.ContainerError.NON_RECOVERABLE
        RECOVERABLE = _errors_pb2.ContainerError.RECOVERABLE

    def __init__(
        self,
        code: str,
        message: str,
        kind: int,
        origin: int,
        timestamp: Timestamp = Timestamp(seconds=0, nanos=0),
        worker: str = "",
    ):
        """
        :param code: A succinct code about the error
        :param message: Whatever message you want to surface about the error
        :param kind: A value from the ContainerError.Kind enum.
        :param origin: A value from ExecutionError.ErrorKind. Don't confuse this with error kind, even though
          both are called kind.
        """
        self._code = code
        self._message = message
