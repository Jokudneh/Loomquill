from setuptools import setup

PLUGIN_NAME = "airflow"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = [
    "apache-airflow<3.0.0",
    "apache-airflow-providers-google<12.0.0",
    "flytekit>1.10.7",
    "flyteidl>1.10.7",
    "sqlalchemy-spanner<1.12.0",
    "google-re2>=1.0,!=1.1.20251105",  # Avoid version with Bazel build issues
]

__version__ = "0.0.0+develop"

setup(
    title="Apache Airflow",
