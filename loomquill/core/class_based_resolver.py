from typing import List

from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import TaskResolverMixin
from flytekit.core.python_auto_container import PythonAutoContainerTask
from flytekit.core.tracker import TrackedInstance


class ClassStorageTaskResolver(TrackedInstance, TaskResolverMixin):
    """
    Stores tasks inside a class variable. The class must be inherited from at the point of usage because the task
    loading process basically relies on the same sequence of things happening.
    """

    def __init__(self, *args, **kwargs):
        self.mapping = []
        super().__init__(*args, **kwargs)

    def name(self) -> str:
        return "ClassStorageTaskResolver"
