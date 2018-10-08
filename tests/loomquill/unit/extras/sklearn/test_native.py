import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from flytekit import task, workflow


@task
def get_preprocessor() -> StandardScaler:
    return StandardScaler()

