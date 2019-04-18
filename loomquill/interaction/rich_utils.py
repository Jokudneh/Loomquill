import typing

from fsspec import Callback
from rich.progress import Progress


class RichCallback(Callback):
    def __init__(self, rich_kwargs: typing.Optional[typing.Dict] = None, **kwargs):
        super().__init__(**kwargs)
        rich_kwargs = rich_kwargs or {}
        self._pb = Progress(**rich_kwargs)
