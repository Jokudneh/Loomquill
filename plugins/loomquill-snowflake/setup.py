from setuptools import setup

PLUGIN_NAME = "snowflake"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>1.13.1", "snowflake-connector-python>=3.11.0"]

__version__ = "0.0.0+develop"

setup(
    title="Snowflake",
    title_expanded="Flytekit Snowflake Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
