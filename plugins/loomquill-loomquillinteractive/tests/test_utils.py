import os

from flytekitplugins.flyteinteractive import get_task_inputs
from flytekitplugins.flyteinteractive.utils import load_module_from_path


def test_load_module_from_path():
    module_name = "task"
    module_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "testdata", "task.py")
