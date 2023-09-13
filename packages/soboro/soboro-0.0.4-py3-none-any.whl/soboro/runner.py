# pyright: reportShadowedImports=false
import inspect
from abc import abstractproperty
from pathlib import Path
from typing import *

from mousse import AutoRegistry, Dataclass, Registry, asclass
from mousse.types.parser import asdict
from typer import Argument

from .cli import cli

__all__ = ["runner_registry", "Runner", "RunnerConfig", "query"]

runner_registry = Registry.get("runner")


class RunnerConfig(Dataclass, dynamic=True):
    type: str
    # tag: str = None
    # inputs: Dict[str, str] = {}
    # outputs: Dict[str, str] = {}
    # metadata: Dict[str, str] = {}


class Runner(metaclass=AutoRegistry, registry="runner"):
    def __init__(self, config: RunnerConfig) -> None:
        if type(config) is not self.config_type:
            config = asclass(self.config_type, asdict(config))

        self.config = config
        self.metadata = {}

    @property
    def config_type(self) -> Type[RunnerConfig]:
        return RunnerConfig

    def prepare(self) -> "Runner":
        pass

    @abstractproperty
    def outputs(self) -> List[str]:
        pass

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError()

    def reset(self):
        pass

    def __call__(self, **inputs: Dict[str, Any]) -> Dict[str, Any]:
        return self.run(**inputs)

    @classmethod
    def create(cls, config: RunnerConfig = None, path: Union[str, Path] = None):
        assert (config is not None) ^ (path is not None), f"Invalid argument"

        if path is not None:
            config = asclass(RunnerConfig, path=path)

        runner_cls = runner_registry[config.type]
        return runner_cls(config)


@cli.command()
def query(runner: str = Argument(..., help="Runner")):
    runner_cls = runner_registry[runner]
    signature = inspect.signature(runner_cls.run)

    print("Inputs:")
    for name, info in signature.parameters.items():
        if name == "self":
            continue

        if info.kind == info.VAR_POSITIONAL:
            name = f"*{name}"

        if info.kind == info.VAR_KEYWORD:
            name = f"**{name}"

        annotation = info.annotation if info.annotation != inspect._empty else Any
        default = info.default if info.default != inspect._empty else ""

        annotation = str(annotation)

        summary = f"\t{name: <16}: {annotation: <8} [{default}]"
        print(summary)

    print("Outputs")
    print(f"\t{signature.return_annotation}")


@cli.command()
def ls():
    runners_cls = list(runner_registry.keys())
    runners_cls.sort()
    for key in runners_cls:
        if key != "Runner":
            print(key)
