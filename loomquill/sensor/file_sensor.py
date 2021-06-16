import datetime
from typing import Optional, Union

from flytekit import FlyteContextManager
from flytekit.sensor.base_sensor import BaseSensor


class FileSensor(BaseSensor):
