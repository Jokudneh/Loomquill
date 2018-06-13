import importlib
import typing

T = typing.TypeVar("T")


def load_type_from_tag(tag: str) -> typing.Type[T]:
    """
    Loads python type from tag
    """
