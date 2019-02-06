from setuptools import setup

PLUGIN_NAME = "awsemrserverless"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = [
    "flytekit>=1.14.6",
    "aioboto3>=12.3.0",
    "boto3>=1.28.0",
]

__version__ = "0.0.0+develop"

setup(
    title="AWS EMR Serverless",
    title_expanded="Flytekit AWS EMR Serverless Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="Flytekit AWS EMR Serverless Plugin: run Spark and Hive jobs from Flyte tasks",
    long_description=open("README.md").read(),
