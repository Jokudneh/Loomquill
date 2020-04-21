from setuptools import setup

PLUGIN_NAME = "papermill"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = [
    "flytekit",
    "papermill>=1.2.0",
    "nbconvert>=6.0.7",
    "ipykernel>=5.0.0",
]

__version__ = "0.0.0+develop"

setup(
    title="Papermill",
    title_expanded="Flytekit Papermill Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="This is the flytekit papermill plugin",
    namespace_packages=["flytekitplugins"],
    packages=[f"flytekitplugins.{PLUGIN_NAME}"],
    install_requires=plugin_requires,
