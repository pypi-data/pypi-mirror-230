# pyright: reportShadowedImports=false
from typing import *

from ...runner import RunnerConfig
from ..preproc import ImagePreProcessRunner, ImagePreProcessRunnerConfig

__all__ = ["FairMOTPreProcessRunner", "FairMOTPreProcessRunnerConfig"]


class FairMOTPreProcessRunnerConfig(ImagePreProcessRunnerConfig, dynamic=True):
    type: str = "FairMOTPreProcessRunner"


class FairMOTPreProcessRunner(ImagePreProcessRunner):
    config_type: Type[RunnerConfig] = FairMOTPreProcessRunnerConfig

    def prepare(self) -> "FairMOTPreProcessRunner":
        return self
