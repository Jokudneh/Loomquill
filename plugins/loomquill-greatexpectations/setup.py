from setuptools import setup

PLUGIN_NAME = "great_expectations"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = [
    "flytekit>=1.5.0",
    "great-expectations>=0.13.30,<1.0.0",
    "sqlalchemy>=1.4.23",
    "pyspark==3.3.2",
    "s3fs<2023.6.0",
]

__version__ = "0.0.0+develop"

