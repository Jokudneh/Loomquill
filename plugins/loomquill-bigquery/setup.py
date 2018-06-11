from setuptools import setup

PLUGIN_NAME = "bigquery"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = [
    "flytekit>1.10.7",
    "google-cloud-bigquery>=3.21.0",
    "google-cloud-bigquery-storage>=2.25.0",
    "flyteidl>1.10.7",
    "numpy<2",
]
