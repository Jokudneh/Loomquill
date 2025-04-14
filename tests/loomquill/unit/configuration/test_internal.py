import os

import mock

from flytekit.configuration import AuthType, PlatformConfig, get_config_file, read_file_if_exists
from flytekit.configuration.internal import AWS, Credentials, Images


def test_load_images():
    cfg = get_config_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs/images.config"))
    imgs = Images.get_specified_images(cfg)
    assert imgs == {"abc": "docker.io/abc", "xyz": "docker.io/xyz:latest"}

    cfg = get_config_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs/sample.yaml"))
    imgs = Images.get_specified_images(cfg)
    assert imgs == {
        "abc": "docker.io/abc",
        "bcd": "docker.io/bcd@sha256:26c68657ccce2cb0a31b330cb0hu3b5e108d467f641c62e13ab40cbec258c68d",
        "xyz": "docker.io/xyz:latest",
    }


def test_no_images():
    cfg = get_config_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs/good.config"))
    imgs = Images.get_specified_images(cfg)
    assert imgs == {}


def test_client_secret_location():
    cfg = get_config_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs/sample.yaml"))
    secret_location = Credentials.CLIENT_CREDENTIALS_SECRET_LOCATION.read(cfg)
    assert secret_location is None

    cfg = get_config_file(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs/creds_secret_location.yaml")
    )
    secret_location = Credentials.CLIENT_CREDENTIALS_SECRET_LOCATION.read(cfg)
