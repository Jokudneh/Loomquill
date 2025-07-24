from setuptools import setup

PLUGIN_NAME = "optuna"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.15.0", "optuna>=4.0.0,<5.0.0", "typing-extensions>=4.10,<5.0"]

__version__ = "0.0.0+develop"

setup(
    title="Optuna (wrapper)",
    title_expanded="Fully Parallelized Wrapper Around Optuna Using Flyte",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="Optuna plugin for flytekit",
    namespace_packages=["flytekitplugins"],
    packages=[f"flytekitplugins.{PLUGIN_NAME}"],
    install_requires=plugin_requires,
