import typing

from fsspec import Callback
from rich.progress import Progress


class RichCallback(Callback):
