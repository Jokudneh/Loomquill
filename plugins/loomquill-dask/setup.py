from setuptools import setup

PLUGIN_NAME = "dask"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = [
    "flyteidl>=1.3.2",
