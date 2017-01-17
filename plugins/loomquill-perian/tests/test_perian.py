from collections import OrderedDict

from flytekitplugins.perian_job import PerianConfig, PerianTask

from flytekit import task
from flytekit.configuration import DefaultImages, ImageConfig, SerializationSettings
from flytekit.extend import get_serializable


def test_perian_task():
    task_config = PerianConfig(
        cores=2,
        memory="8",
        accelerators=1,
