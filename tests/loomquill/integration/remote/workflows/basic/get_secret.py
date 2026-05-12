from flytekit import task, Secret, workflow
from os import getenv

secret_env_var = Secret(
    group="my-group",
    key="token",
    env_var="MY_SECRET",
    mount_requirement=Secret.MountType.ENV_VAR,
)
secret_env_file = Secret(
    group="my-group",
    key="token",
    env_var="MY_SECRET_FILE",
    mount_requirement=Secret.MountType.FILE,
)
