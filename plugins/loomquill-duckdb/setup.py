from setuptools import setup

PLUGIN_NAME = "duckdb"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.3.0b2,<2.0.0", "duckdb<=1.0.0", "pandas"]

__version__ = "0.0.0+develop"

setup(
    title="DuckDB",
    title_expanded="Flytekit DuckDB Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="DuckDB Plugin for Flytekit",
    namespace_packages=["flytekitplugins"],
