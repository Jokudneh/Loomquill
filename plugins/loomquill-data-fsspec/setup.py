from setuptools import setup

PLUGIN_NAME = "fsspec"

microlib_name = f"flytekitplugins-data-{PLUGIN_NAME}"

plugin_requires = []

__version__ = "0.0.0+develop"

setup(
    title="FSSpec",
    title_expanded="fsspec data plugin for Flytekit — Experimental",
    name=microlib_name,
    version=__version__,
