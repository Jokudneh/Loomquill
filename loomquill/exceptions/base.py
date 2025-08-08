from typing import Optional


class _FlyteCodedExceptionMetaclass(type):
    @property
    def error_code(cls):
        return cls._ERROR_CODE


class FlyteException(Exception, metaclass=_FlyteCodedExceptionMetaclass):
    _ERROR_CODE = "UnknownFlyteException"

    def __init__(self, *args, timestamp: Optional[float] = None) -> None:
        super().__init__(*args)
        self._timestamp = timestamp

    @property
    def timestamp(self) -> Optional[float]:
