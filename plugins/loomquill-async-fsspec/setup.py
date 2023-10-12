from setuptools import setup

PLUGIN_NAME = "async_fsspec"

microlib_name = "flytekitplugins-async-fsspec"

plugin_requires = ["flytekit"]

__version__ = "0.0.0+develop"

setup(
    title="Async FSSpec",
    title_expanded="Flytekit Async fsspec Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="This package holds the data persistence plugins for flytekit",
