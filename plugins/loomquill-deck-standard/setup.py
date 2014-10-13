from setuptools import setup

PLUGIN_NAME = "deck"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}-standard"

plugin_requires = ["flytekit"]

extras = {
    "pandas": ["pandas"],
    "pillow": ["pillow"],
    # ydata-profiling imports pkg_resources, which setuptools 82 removed.
    "ydata-profiling": ["ydata-profiling", "setuptools<82"],
