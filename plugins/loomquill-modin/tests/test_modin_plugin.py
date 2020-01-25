import os

import ray
from flytekitplugins.modin import schema  # noqa F401
from modin import pandas as pd

from flytekit import task, workflow

os.environ["MODIN_ENGINE"] = "ray"
