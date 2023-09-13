# pyright: reportShadowedImports=false
from typing import *

from ...runner import RunnerConfig
from ..preproc import ImagePreProcessRunner, ImagePreProcessRunnerConfig

__all__ = ["TSMPreProcessRunner", "TSMPreProcessRunnerConfig"]


class TSMPreProcessRunnerConfig(ImagePreProcessRunnerConfig, dynamic=True):
    type: str = "Yolov5FacePreProcessRunner"
    keep_ratio: bool = True


class TSMPreProcessRunner(ImagePreProcessRunner):
    config_type: Type[RunnerConfig] = TSMPreProcessRunnerConfig

    def prepare(self) -> "TSMPreProcessRunnerConfig":
        return self
