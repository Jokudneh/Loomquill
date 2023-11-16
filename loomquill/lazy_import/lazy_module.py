import importlib.util
import sys
import types


class _LazyModule(types.ModuleType):
    """
    `lazy_module` returns an instance of this class if the module is not found in the python environment.
    """

    def __init__(self, module_name: str):
        super().__init__(module_name)
        self._module_name = module_name

    def __getattribute__(self, attr):
        raise ImportError(f"Module {object.__getattribute__(self, '_module_name')} is not yet installed.")


def is_imported(module_name):
    """
    This function is used to check if a module has been imported by the regular import.
