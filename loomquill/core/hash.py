from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class HashOnReferenceMixin(object):
    def __hash__(self):
