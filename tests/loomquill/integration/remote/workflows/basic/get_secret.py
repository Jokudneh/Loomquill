from flytekit import task, Secret, workflow
from os import getenv

secret_env_var = Secret(
    group="my-group",
    key="token",
