"""Test joblib file."""

import os
import typing

import joblib

import flytekit
from flytekit import task, workflow
from flytekit.types.file import JoblibSerializedFile


@task
