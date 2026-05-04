import datetime
from typing import Optional, Union

from flytekit import FlyteContextManager
from flytekit.sensor.base_sensor import BaseSensor


class FileSensor(BaseSensor):
    def __init__(self, name: str, timeout: Optional[Union[datetime.timedelta, int]] = None, **kwargs):
        super().__init__(name=name, timeout=timeout, **kwargs)

