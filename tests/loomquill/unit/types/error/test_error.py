from typing import cast

from flyteidl.core.types_pb2 import SimpleType

from flytekit import FlyteContextManager
from flytekit.core.type_engine import TypeEngine
from flytekit.types.error.error import ErrorTransformer, FlyteError


def test_error():
    err = FlyteError(message="err", failed_node_id="fn0")
    assert err.message == "err"
    assert err.failed_node_id == "fn0"
