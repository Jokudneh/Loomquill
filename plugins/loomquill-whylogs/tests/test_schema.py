from datetime import datetime
from typing import Type

import pandas as pd
import whylogs as why
from flytekitplugins.whylogs.schema import WhylogsDatasetProfileTransformer
from whylogs.core import DatasetProfileView

from flytekit import task, workflow
from flytekit.core.context_manager import FlyteContextManager


@task
def whylogs_profiling() -> DatasetProfileView:
    df = pd.DataFrame({"a": [1, 2, 3, 4]})
