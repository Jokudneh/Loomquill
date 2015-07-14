from setuptools import setup

PLUGIN_NAME = "memray"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.12.0", "memray"]

__version__ = "0.0.0+develop"

