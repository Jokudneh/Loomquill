from setuptools import setup

PLUGIN_NAME = "spark"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.15.1", "pyspark>=3.4.0", "aiohttp", "flyteidl>=1.11.0b1", "pandas"]

__version__ = "0.0.0+develop"

setup(
    title="Spark",
    title_expanded="Flytekit Spark Plugin",
