from base64 import b64decode, b64encode
from typing import List

import cloudpickle

from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import TaskResolverMixin
from flytekit.core.python_auto_container import PythonAutoContainerTask
from flytekit.core.tracker import TrackedInstance


class ExperimentalNaiveCloudPickleResolver(TrackedInstance, TaskResolverMixin):
    """
    Please do not use this resolver, basically ever. This is here for demonstration purposes only. The critical flaw
    of this resolver is that pretty much any task that it resolves results in loader_args that are enormous. This
