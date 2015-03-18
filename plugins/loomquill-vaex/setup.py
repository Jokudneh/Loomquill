from setuptools import setup

PLUGIN_NAME = "vaex"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

# vaex doesn't support pydantic 2.0 yet. https://github.com/vaexio/vaex/issues/2384
plugin_requires = [
    "flytekit>=1.3.0b2,<2.0.0",
    "vaex-core>=4.13.0,<4.14; python_version < '3.10'",
    "vaex-core>=4.16.0; python_version >= '3.10'",
