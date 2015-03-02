import pip
from setuptools import setup
from setuptools.command.develop import develop

PLUGIN_NAME = "dolt"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.3.0b2,<2.0.0", "dolt_integrations>=0.1.5", "networkx<3.2; python_version<'3.9'"]
dev_requires = ["pytest-mock>=3.6.1"]

__version__ = "0.0.0+develop"
