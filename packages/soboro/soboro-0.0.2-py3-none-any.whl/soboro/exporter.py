# pyright: reportShadowedImports=false
import inspect
from importlib import import_module
from pathlib import Path
from typing import *

from mousse import get_logger

from .cli import Command
from .runner import Runner, RunnerConfig

logger = get_logger(__name__.split(".")[0])

__all__ = ["scan"]


def scan(package: str):
    curr_frame = inspect.currentframe()

    caller = curr_frame.f_back
    filepath = Path(caller.f_code.co_filename).resolve()
    module_path = filepath.parent

    modules = {}
    for child in module_path.glob("*"):
        if child.is_dir() and not child.name.startswith("_"):
            module = import_module(f".{child.name}", package=package)
            modules[child.name] = module

            predicate = lambda val: (
                inspect.isclass(val) and issubclass(val, (Runner, RunnerConfig))
            ) or isinstance(val, Command)
            for key, val in inspect.getmembers(module, predicate=predicate):
                modules[key] = val

    outer_frames = inspect.getouterframes(curr_frame)
    call_frame = outer_frames[1]
    _globals = call_frame.frame.f_globals
    if "__all__" not in _globals:
        _globals["__all__"] = []

    __all = _globals["__all__"]

    if call_frame.function == "<module>":
        __locals = call_frame.frame.f_locals
    else:
        __locals = vars(inspect.getmodule(call_frame.frame))

    for key, val in modules.items():
        __all.append(key)
        __locals[key] = val
