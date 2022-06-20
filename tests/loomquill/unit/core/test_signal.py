import pytest
from flyteidl.admin.signal_pb2 import Signal, SignalList
from mock import MagicMock

from flytekit.configuration import Config
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.type_engine import TypeEngine
from flytekit.models.core.identifier import SignalIdentifier, WorkflowExecutionIdentifier
from flytekit.remote.remote import FlyteRemote


@pytest.fixture
def remote():
    flyte_remote = FlyteRemote(config=Config.auto(), default_project="p1", default_domain="d1")
