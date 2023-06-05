from setuptools import setup

PLUGIN_NAME = "hive"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.3.0b2,<2.0.0"]

__version__ = "0.0.0+develop"

setup(
    title="Hive",
