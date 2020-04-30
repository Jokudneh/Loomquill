import pytest
from mock import patch

from flytekit import TaskMetadata
from flytekit.core import context_manager
from flytekit.models.core.identifier import Identifier, ResourceType
from flytekit.models.interface import TypedInterface
from flytekit.remote import FlyteTask
from flytekit.remote.lazy_entity import LazyEntity


def test_missing_getter():
    with pytest.raises(ValueError):
        LazyEntity("x", None)


dummy_task = FlyteTask(
    id=Identifier(ResourceType.TASK, "p", "d", "n", "v"),
    type="t",
    metadata=TaskMetadata().to_taskmetadata_model(),
    interface=TypedInterface(inputs={}, outputs={}),
    custom=None,
)


def test_lazy_loading():
    once = True

    def _getter():
        nonlocal once
        if not once:
            raise ValueError("Should be called once only")
        once = False
        return dummy_task

    e = LazyEntity("x", _getter)
