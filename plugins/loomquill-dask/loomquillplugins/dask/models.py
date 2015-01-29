from typing import Optional

from flyteidl.plugins import dask_pb2 as dask_task

from flytekit.models import common as common
from flytekit.models import task as task


class Scheduler(common.FlyteIdlEntity):
    """
    Configuration for the scheduler pod

    :param image: Optional image to use.
    :param resources: Optional resources to use.
    """

    def __init__(self, image: Optional[str] = None, resources: Optional[task.Resources] = None):
        self._image = image
        self._resources = resources

    @property
    def image(self) -> Optional[str]:
        """
        :return: The optional image for the scheduler pod
        """
