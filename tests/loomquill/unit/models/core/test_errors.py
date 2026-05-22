from flytekit.models.core import errors, execution
from google.protobuf.timestamp_pb2 import Timestamp

def test_container_error():
    obj = errors.ContainerError(
        "code", "my message", errors.ContainerError.Kind.RECOVERABLE, execution.ExecutionError.ErrorKind.SYSTEM
    )
    assert obj.code == "code"
    assert obj.message == "my message"
    assert obj.kind == errors.ContainerError.Kind.RECOVERABLE
    assert obj.origin == 2
    assert obj.timestamp == Timestamp(seconds=0, nanos=0)
    assert obj.worker == ""

    converted_obj = errors.ContainerError.from_flyte_idl(obj.to_flyte_idl())
    assert obj == converted_obj
    assert converted_obj.code == "code"
    assert converted_obj.message == "my message"
