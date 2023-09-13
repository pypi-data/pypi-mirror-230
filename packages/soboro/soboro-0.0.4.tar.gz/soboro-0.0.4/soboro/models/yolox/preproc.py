# pyright: reportShadowedImports=false
from typing import *

from ...runner import RunnerConfig
from ..preproc import ImagePreProcessRunner, ImagePreProcessRunnerConfig

__all__ = ["YoloXPreProcessRunner", "YoloXPreProcessRunnerConfig"]


class YoloXPreProcessRunnerConfig(ImagePreProcessRunnerConfig, dynamic=True):
    type: str = "YoloXPreProcessRunner"


class YoloXPreProcessRunner(ImagePreProcessRunner):
    config_type: Type[RunnerConfig] = YoloXPreProcessRunnerConfig

    def prepare(self) -> "YoloXPreProcessRunner":
        return self
