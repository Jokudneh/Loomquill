from setuptools import setup

PLUGIN_NAME = "comet-ml"
MODULE_NAME = "comet_ml"


microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.12.3", "comet-ml>=3.43.2"]

__version__ = "0.0.0+develop"

setup(
    title="Comet ML",
    title_expanded="Flytekit Comet Plugin",
    name=microlib_name,
