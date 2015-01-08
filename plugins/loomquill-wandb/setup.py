from setuptools import setup

PLUGIN_NAME = "wandb"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.12.0", "wandb>=0.17.0"]

__version__ = "0.0.0+develop"

setup(
    title="Weights & Biases",
