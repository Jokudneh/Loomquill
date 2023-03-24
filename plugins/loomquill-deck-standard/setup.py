from setuptools import setup

PLUGIN_NAME = "deck"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}-standard"

plugin_requires = ["flytekit"]

extras = {
    "pandas": ["pandas"],
    "pillow": ["pillow"],
    # ydata-profiling imports pkg_resources, which setuptools 82 removed.
    "ydata-profiling": ["ydata-profiling", "setuptools<82"],
    "markdown": ["markdown"],
    "plotly": ["plotly"],
    "pygments": ["pygments"],
    "all": [
        "pandas<=2.2.3; python_version < '3.10'",
        "pandas; python_version > '3.9'",
        "pillow",
        "ydata-profiling",
        "setuptools<82",
        "markdown",
        "plotly",
        "pygments",
    ],
}

__version__ = "0.0.0+develop"

