from setuptools import setup

PLUGIN_NAME = "neptune"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.16.0", "neptune-scale>=0.13.0"]

__version__ = "0.0.0+develop"

setup(
    title="Neptune",
    title_expanded="Flytekit Neptune Plugin",
    name=microlib_name,
