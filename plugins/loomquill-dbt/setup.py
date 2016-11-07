from setuptools import setup

PLUGIN_NAME = "dbt"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.3.0b2", "dbt-core>=1.6.0,<1.8.0", "networkx>=2.5"]

__version__ = "0.0.0+develop"

setup(
    title="DBT",
    title_expanded="Flytekit dbt plugin",
