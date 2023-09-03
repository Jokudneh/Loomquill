import typing
from threading import Lock

from flytekit import FlyteContext
from flytekit.models.core.identifier import Identifier
from flytekit.remote.remote_callable import RemoteEntity

T = typing.TypeVar("T", bound=RemoteEntity)


class LazyEntity(RemoteEntity, typing.Generic[T]):
    """
    Fetches the entity when the entity is called or when the entity is retrieved.
    The entity is derived from RemoteEntity so that it behaves exactly like the mimicked entity.
    """

    def __init__(self, name: str, getter: typing.Callable[[], T], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._entity = None
        self._getter = getter
        self._name = name
