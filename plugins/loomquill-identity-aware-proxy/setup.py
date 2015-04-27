from setuptools import setup

PLUGIN_NAME = "identity_aware_proxy"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = [
    "click",
    "google-cloud-secret-manager",
    "google-auth",
    "flytekit>=1.10",
    # https://github.com/grpc/grpc/issues/33935
    # https://github.com/grpc/grpc/issues/35323
    "grpcio>=1.62.0",
]

__version__ = "0.0.0+develop"

