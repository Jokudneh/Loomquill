import importlib
import inspect
import os
import sys
import typing
from pathlib import Path
from types import ModuleType
from typing import Callable, Optional, Tuple, Union

from flytekit.configuration.feature_flags import FeatureFlags
from flytekit.exceptions import system as _system_exceptions
from flytekit.loggers import developer_logger, logger
from flytekit.tools.interactive import ipython_check


def import_module_from_file(module_name, file):
    try:
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        return module
    except Exception as exc:
        raise ModuleNotFoundError(f"Module from file {file} cannot be loaded") from exc


class InstanceTrackingMeta(type):
    """
    Please see the original class :flytekit.common.mixins.registerable._InstanceTracker` also and also look
    at the tests in the ``tests/flytekit/unit/core/tracker/test_tracking/`` folder to see how it's used.

    Basically, this will make instances of classes that use this metaclass aware of the module (the .py file) that
    caused the instance to be created. This is useful because it means that we can then (at least try to) find the
    variable that the instance was assigned to.
    """

    @staticmethod
    def _get_module_from_main(globals) -> Optional[str]:
        curdir = Path.cwd()
        file = globals.get("__file__")
        if file is None:
            return None

        file = Path(file)
        try:
            file_relative = file.relative_to(curdir)
        except ValueError:
            return None

        module_components = [*file_relative.with_suffix("").parts]
        module_name = ".".join(module_components)
        if len(module_components) == 0:
            return None

        # make sure current directory is in the PYTHONPATH.
        sys.path.insert(0, str(curdir))
        try:
            return import_module_from_file(module_name, file)
        except ModuleNotFoundError:
            return None

    @staticmethod
    def _find_instance_module():
        frame = inspect.currentframe()
        while frame:
            if frame.f_code.co_name == "<module>" and "__name__" in frame.f_globals:
                if frame.f_globals["__name__"] != "__main__":
                    return frame.f_globals["__name__"], frame.f_globals.get("__file__")

                # Try to find the module and filename in the case that we're in the __main__ module
                # This is useful in cases that use FlyteRemote to load tasks/workflows that are defined
                # in the same file as where FlyteRemote is being invoked to register and execute Flyte
                # entities. One such case is with the `eager` decorator.
                mod = InstanceTrackingMeta._get_module_from_main(frame.f_globals)
                if mod is None:
                    return None, None

                # This is used in find_lhs to find the trackable instances when the module is loaded from the __file__.
                return mod.__name__, mod.__file__
            frame = frame.f_back
        return None, None

    def __call__(cls, *args, **kwargs):
        o = super(InstanceTrackingMeta, cls).__call__(*args, **kwargs)
        mod_name, mod_file = InstanceTrackingMeta._find_instance_module()
        o._instantiated_in = mod_name
        o._module_file = Path(mod_file).resolve() if mod_file else None
        return o


class TrackedInstance(metaclass=InstanceTrackingMeta):
    """
    Please see the notes for the metaclass above first.

    This functionality has two use-cases currently,
    * Keep track of naming for non-function ``PythonAutoContainerTasks``.  That is, things like the
      {{< py_class_ref flytekit.extras.sqlite3.task.SQLite3Task >}} task.
    * Task resolvers, because task resolvers are instances of {{< py_class_ref flytekit.core.python_auto_container.TaskResolverMixin >}}
      classes, not the classes themselves, which means we need to look on the left hand side of them to see how to
      find them at task execution time.
