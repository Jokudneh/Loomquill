from setuptools import setup

PLUGIN_NAME = "perian_job"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.12.0,<2.0.0", "perian>=0.2.7"]

__version__ = "0.0.0+develop"

setup(
    title="Perian Job Platform",
    title_expanded="Flytekit Perian Job Platform Plugin",
