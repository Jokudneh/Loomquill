from typing import Optional

import numpy as np
import pandas as pd
import whylogs as why
from flytekitplugins.whylogs.renderer import WhylogsConstraintsRenderer, WhylogsSummaryDriftRenderer
from whylogs.core.constraints import ConstraintsBuilder, MetricConstraint, MetricsSelector

import flytekit
from flytekit import task, workflow


@task
def make_data(n_rows: int) -> pd.DataFrame:
    data = {
        "sepal_length": np.random.random_sample(n_rows),
        "sepal_width": np.random.random_sample(n_rows),
        "petal_length": np.random.random_sample(n_rows),
        "petal_width": np.random.random_sample(n_rows),
        "species": np.random.choice(["virginica", "setosa", "versicolor"], n_rows),
        "species_id": np.random.choice([1, 2, 3], n_rows),
    }
