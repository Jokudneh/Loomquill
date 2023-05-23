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

setup(
    title="Google IAP",
    title_expanded="Flytekit Identity Aware Proxy",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="External command plugin to generate ID tokens for GCP Identity Aware Proxy",
    url="https://github.com/flyteorg/flytekit/tree/master/plugins/flytekit-identity-aware-proxy",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    namespace_packages=["flytekitplugins"],
    packages=[f"flytekitplugins.{PLUGIN_NAME}"],
