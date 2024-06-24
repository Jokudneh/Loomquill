import os

import pip
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

PACKAGE_NAME = "flytekitplugins-parent"

__version__ = "0.0.0+develop"

# Please maintain an alphabetical order in the following list
SOURCES = {
    "flytekitplugins-async-fsspec": "flytekit-async-fsspec",
    "flytekitplugins-athena": "flytekit-aws-athena",
    "flytekitplugins-awsbatch": "flytekit-aws-batch",
    "flytekitplugins-awssagemaker": "flytekit-aws-sagemaker",
    "flytekitplugins-bigquery": "flytekit-bigquery",
    "flytekitplugins-dask": "flytekit-dask",
    "flytekitplugins-dbt": "flytekit-dbt",
    "flytekitplugins-deck-standard": "flytekit-deck-standard",
    "flytekitplugins-dolt": "flytekit-dolt",
    "flytekitplugins-duckdb": "flytekit-duckdb",
    "flytekitplugins-data-fsspec": "flytekit-data-fsspec",
    "flytekitplugins-envd": "flytekit-envd",
    "flytekitplugins-flyteinteractive": "flytekit-flyteinteractive",
    "flytekitplugins-great_expectations": "flytekit-greatexpectations",
    "flytekitplugins-geopandas": "flytekit-geopandas",
    "flytekitplugins-hive": "flytekit-hive",
    "flytekitplugins-huggingface": "flytekit-huggingface",
    "flytekitplugins-inference": "flytekit-inference",
    "flytekitplugins-pod": "flytekit-k8s-pod",
