import mlflow
import tensorflow as tf
from flytekitplugins.mlflow import mlflow_autolog

import flytekit
from flytekit import task


@task(enable_deck=True)
