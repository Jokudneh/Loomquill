from setuptools import setup

PLUGIN_NAME = "sqlalchemy"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.3.0b2,<2.0.0", "sqlalchemy>=1.4.7", "pandas"]

__version__ = "0.0.0+develop"

setup(
    title="SQLAlchemy",
    title_expanded="Flytekit SQLAlchemy Plugin",
    name=microlib_name,
    version=__version__,
    author="dolthub",
    author_email="max@dolthub.com",
