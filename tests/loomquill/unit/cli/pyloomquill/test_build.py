import os

from click.testing import CliRunner

from flytekit.clis.sdk_in_container import pyflyte
from flytekit.image_spec.image_spec import ImageBuildEngine

WORKFLOW_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "image_spec_wf.py")
