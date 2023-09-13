# pyright: reportShadowedImports=false
from typing import *

from ...runner import RunnerConfig
from ..preproc import ImagePreProcessRunner, ImagePreProcessRunnerConfig

__all__ = ["ICLSPreProcessRunner", "ICLSPreProcessRunnerConfig"]


class ICLSPreProcessRunnerConfig(ImagePreProcessRunnerConfig, dynamic=True):
    type: str = "ICLSPreProcessRunner"


class ICLSPreProcessRunner(ImagePreProcessRunner):
    config_type: Type[RunnerConfig] = ICLSPreProcessRunnerConfig

    def prepare(self) -> "ICLSPreProcessRunner":
        return self
