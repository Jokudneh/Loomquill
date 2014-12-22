from setuptools import setup

PLUGIN_NAME = "mlflow"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.1.0,<2.0.0", "plotly", "mlflow>=2.10.0", "pandas"]

__version__ = "0.0.0+develop"

setup(
    title="MLflow",
    title_expanded="Flytekit MLflow Plugin",
    name=microlib_name,
