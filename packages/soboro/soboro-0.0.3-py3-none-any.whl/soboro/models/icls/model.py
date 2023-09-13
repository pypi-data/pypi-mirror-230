# pyright: reportShadowedImports=false
from typing import *

import numpy as np

from ...common import Detection, Image, Images, InputFormat
from ...runner import Runner, RunnerConfig
from ..onnx import OnnxNodeInfo, OnnxRunner, OnnxRunnerConfig
from .postproc import ICLSPostProcessRunner, ICLSPostProcessRunnerConfig
from .preproc import ICLSPreProcessRunner, ICLSPreProcessRunnerConfig

__all__ = ["ICLSModelRunner", "ICLSModelRunnerConfig"]


class ICLSModelRunnerConfig(
    ICLSPreProcessRunnerConfig,
    OnnxRunnerConfig,
    ICLSPostProcessRunnerConfig,
    dynamic=True,
):
    type: str = "ICLSModelRunner"
    input_node: str = "images"
    output_node: str = "output"
    batch_size: int = -1


class ICLSModelRunner(Runner):
    config_type: Type[RunnerConfig] = ICLSModelRunnerConfig

    def prepare(self) -> "ICLSModelRunner":
        config: ICLSModelRunner = self.config

        self.onnx_runner = OnnxRunner(config)
        self.onnx_runner.prepare()

        self.input_info: OnnxNodeInfo = self.onnx_runner.metadata[config.input_node]

        if config.input_format == InputFormat.hwc:
            (
                config.batch_size,
                config.height,
                config.width,
                _,
            ) = self.input_info.dims

        if config.input_format == InputFormat.chw:
            (
                config.batch_size,
                _,
                config.height,
                config.width,
            ) = self.input_info.dims

        self.preproc_runner = ICLSPreProcessRunner(config)
        self.preproc_runner.prepare()

        self.postproc_runner = ICLSPostProcessRunner(config)
        self.postproc_runner.prepare()

        return self

    def run(
        self, images: Union[Image, Images], **kwargs
    ) -> Union[List[Detection], List[List[Detection]]]:
        config: ICLSModelRunnerConfig = self.config

        is_single_image = type(images) is not list
        if is_single_image:
            images = [images]

        images = [
            Image(mat=image) if isinstance(image, np.ndarray) else image
            for image in images
        ]

        preproc_images = []
        for image in images:
            preproc_image = self.preproc_runner.run(image)
            preproc_images.append(preproc_image.mat)

        results = []
        for i in range(0, len(preproc_images), config.batch_size):
            batch = preproc_images[i : i + config.batch_size]
            batch_size = len(batch)
            if batch_size < config.batch_size:
                batch += [
                    np.zeros(self.input_info.dims[1:], dtype=self.input_info.dtype)
                    for _ in range(config.batch_size - batch_size)
                ]

            batch = np.stack(batch)
            output = self.onnx_runner.run(**{config.input_node: batch})[
                config.output_node
            ]

            batch = batch[:batch_size, ...]
            output = output[:batch_size, ...]

            classifications = self.postproc_runner.run(output=output)
            results.extend(classifications)

        if is_single_image:
            return results[0]

        return results
