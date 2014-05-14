from setuptools import setup

PLUGIN_NAME = "mmcloud"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.9.1,<2.0.0", "kubernetes"]

__version__ = "0.0.0+develop"

setup(
    title="Memory Machine Cloud",
