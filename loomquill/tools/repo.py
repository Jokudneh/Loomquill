import asyncio
import functools
import os
import tarfile
import tempfile
import typing
from pathlib import Path

import click
from rich import print as rprint

from flytekit.configuration import FastSerializationSettings, ImageConfig, SerializationSettings
from flytekit.constants import CopyFileDetection
from flytekit.core.base_task import PythonTask
from flytekit.core.context_manager import FlyteContextManager, FlyteEntities
from flytekit.core.resources import ResourceSpec
from flytekit.loggers import logger
from flytekit.models import launch_plan, task
from flytekit.models.core.identifier import Identifier
from flytekit.remote import FlyteRemote
from flytekit.remote.remote import RegistrationSkipped, _get_git_repo_url
from flytekit.tools import fast_registration, module_loader
from flytekit.tools.script_mode import _find_project_root
from flytekit.tools.serialize_helpers import get_registrable_entities, persist_registrable_entities
from flytekit.tools.translator import FlyteControlPlaneEntity, Options


class NoSerializableEntitiesError(Exception):
    pass


def serialize_load_only(
    pkgs: typing.List[str],
    settings: SerializationSettings,
    local_source_root: typing.Optional[str] = None,
):
    """
    See {{< py_class_ref flytekit.models.core.identifier.ResourceType >}} to match the trailing index in the file name with the
    entity type.
    :param settings: SerializationSettings to be used
    :param pkgs: Dot-delimited Python packages/subpackages to look into for serialization.
    :param local_source_root: Where to start looking for the code.
    """
    settings.source_root = local_source_root
    ctx_builder = FlyteContextManager.current_context().with_serialization_settings(settings)
    with FlyteContextManager.with_context(ctx_builder):
        # Scan all modules. the act of loading populates the global singleton that contains all objects
        with module_loader.add_sys_path(local_source_root):
            click.secho(f"Loading packages {pkgs} under source root {local_source_root}", fg="yellow")
            module_loader.just_load_modules(pkgs=pkgs)


def serialize_get_control_plane_entities(
    settings: SerializationSettings,
    local_source_root: typing.Optional[str] = None,
    options: typing.Optional[Options] = None,
    is_registration: bool = False,
) -> typing.List[FlyteControlPlaneEntity]:
    """
    See {{< py_class_ref flytekit.models.core.identifier.ResourceType >}} to match the trailing index in the file name with the
    entity type.
    :param options:
    :param settings: SerializationSettings to be used
    :param pkgs: Dot-delimited Python packages/subpackages to look into for serialization.
    :param local_source_root: Where to start looking for the code.
    :param is_registration: Whether this is happening for registration.
    """
    settings.source_root = local_source_root
    ctx_builder = FlyteContextManager.current_context().with_serialization_settings(settings)
    with FlyteContextManager.with_context(ctx_builder) as ctx:
        registrable_entities = get_registrable_entities(ctx, options=options)
        return registrable_entities


def serialize_to_folder(
    pkgs: typing.List[str],
    settings: SerializationSettings,
    local_source_root: typing.Optional[str] = None,
    folder: str = ".",
    options: typing.Optional[Options] = None,
):
    """
    Serialize the given set of python packages to a folder
    """
    if folder is None:
        folder = "."
    serialize_load_only(pkgs, settings, local_source_root)
    loaded_entities = serialize_get_control_plane_entities(settings, local_source_root, options=options)
    click.secho(
        f"Successfully serialized {len(loaded_entities)} flyte entities",
        fg="green",
    )
    persist_registrable_entities(loaded_entities, folder)


def package(
    serializable_entities: typing.List[FlyteControlPlaneEntity],
    source: str = ".",
    output: str = "./flyte-package.tgz",
    deref_symlinks: bool = False,
    fast_options: typing.Optional[fast_registration.FastPackageOptions] = None,
):
    """
    Package the given entities and the source code (if fast is enabled) into a package with the given name in output
    :param serializable_entities: Entities that can be serialized
    :param source: source folder
    :param output: output package name with suffix
    :param deref_symlinks: if enabled then symlinks are dereferenced during packaging
    :param fast_options:

    Temporarily, for fast register, specify both the fast arg as well as copy_style fast == True with
    copy_style == None means use the old fast register tar'ring method.
    In the future the fast bool will be removed, and copy_style == None will mean do not fast register.
    """
    if not serializable_entities:
        raise NoSerializableEntitiesError("Nothing to package")
