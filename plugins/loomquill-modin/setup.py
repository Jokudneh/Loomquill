from setuptools import setup

PLUGIN_NAME = "modin"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = [
    "flytekit",
    "fsspec",
]

__version__ = "0.0.0+develop"

setup(
