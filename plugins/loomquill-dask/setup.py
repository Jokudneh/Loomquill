from setuptools import setup

PLUGIN_NAME = "dask"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = [
    "flyteidl>=1.3.2",
    "flytekit>=1.3.0b2,<2.0.0",
    "dask[distributed]>=2022.10.2",
]

