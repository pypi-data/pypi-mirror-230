# pyright: reportShadowedImports=false
from typing import *

from ...runner import RunnerConfig
from ..preproc import ImagePreProcessRunner, ImagePreProcessRunnerConfig

__all__ = ["Yolov5FacePreProcessRunner", "Yolov5FacePreProcessRunnerConfig"]


class Yolov5FacePreProcessRunnerConfig(ImagePreProcessRunnerConfig, dynamic=True):
    type: str = "Yolov5FacePreProcessRunner"
    keep_ratio: bool = True


class Yolov5FacePreProcessRunner(ImagePreProcessRunner):
    config_type: Type[RunnerConfig] = Yolov5FacePreProcessRunnerConfig

    def prepare(self) -> "Yolov5FacePreProcessRunner":
        return self
