from setuptools import setup

PLUGIN_NAME = "polars"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.3.0b2,<2.0.0", "polars>=0.8.27", "pandas"]

__version__ = "0.0.0+develop"

setup(
    title="Polars",
    title_expanded="Flytekit Polars Plugin",
    name=microlib_name,
    version=__version__,
