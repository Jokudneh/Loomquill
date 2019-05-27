from setuptools import setup

PLUGIN_NAME = "xarray"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}-zarr"

plugin_requires = [
    "dask[distributed]>=2022.10.2",
    "flytekit>=1.3.0b2,<2.0.0",
    "xarray",
    "zarr",
]

