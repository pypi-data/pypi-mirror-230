# pyright: reportShadowedImports=false
from typing import *

import cv2
import numpy as np

from ...common import InputFormat, ColorFormat, Image, PaddingFormat
from ...runner import RunnerConfig, Runner

__all__ = ["ImagePreProcessRunner", "ImagePreProcessRunnerConfig"]


class ImagePreProcessRunnerConfig(RunnerConfig, dynamic=True):
    type: str = "ImagePreProcessRunner"
    width: int
    height: int
    keep_ratio: bool = False
    interpolation: int = cv2.INTER_LINEAR

    padding_format: PaddingFormat = PaddingFormat.corner
    input_format: InputFormat = InputFormat.hwc
    color_format: ColorFormat = ColorFormat.bgr

    mean: Tuple[float, float, float] = (0, 0, 0)
    std: Tuple[float, float, float] = (1, 1, 1)


class ImagePreProcessRunner(Runner):
    config_type: Type[RunnerConfig] = ImagePreProcessRunnerConfig
    outputs: List[str] = ["output"]

    def prepare(self) -> "ImagePreProcessRunner":
        return self

    def run(self, image: Image, **kwargs) -> Image:
        config: ImagePreProcessRunnerConfig = self.config
        if isinstance(image, np.ndarray):
            image = Image(mat=image)

        mat = image.mat

        resized_height = config.height
        resized_width = config.width

        padding = (0, 0, 0, 0)
        if config.keep_ratio:
            height, width, _ = mat.shape
            tar_ratio = config.width / config.height
            src_ratio = width / height

            if src_ratio > tar_ratio:
                resized_height = int(config.width / src_ratio)

            if src_ratio < tar_ratio:
                resized_width = int(config.height * tar_ratio)

            if config.padding_format == PaddingFormat.corner:
                padding = (
                    0,
                    config.height - resized_height,
                    0,
                    config.width - resized_width,
                )
            elif config.padding_format == PaddingFormat.center:
                pad_width = (config.width - resized_width) // 2
                pad_height = (config.height - resized_height) // 2
                padding = (
                    pad_height,
                    config.height - resized_height - pad_height,
                    pad_width,
                    config.width - resized_width - pad_width,
                )
            else:
                raise ValueError(config.padding_format)

        resized = cv2.resize(
            mat, (resized_width, resized_height), interpolation=config.interpolation
        )

        resized = cv2.copyMakeBorder(
            resized,
            *padding,
            borderType=cv2.BORDER_CONSTANT,
            value=(0, 0, 0),
        )

        padding = (
            padding[0] / config.height,
            padding[1] / config.height,
            padding[2] / config.width,
            padding[3] / config.width,
        )

        if config.color_format == ColorFormat.rgb:
            resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        resized = resized.astype(float)
        resized -= config.mean
        resized /= config.std

        if config.input_format == InputFormat.chw:
            resized = resized.transpose(2, 0, 1)

        resized = Image(mat=resized)
        resized.padding = padding

        return resized
