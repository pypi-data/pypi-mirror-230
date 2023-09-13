# pyright: reportShadowedImports=false
import math
from typing import *

import numpy as np

from ...common import Detection, Image, Images, InputFormat, clip
from ...runner import Runner, RunnerConfig
from ..onnx import OnnxNodeType, OnnxRunner, OnnxRunnerConfig
from .postproc import FairMOTPostProcessRunner, FairMOTPostProcessRunnerConfig
from .preproc import FairMOTPreProcessRunner, FairMOTPreProcessRunnerConfig

__all__ = ["FairMOTModelRunner", "FairMOTModelRunnerConfig"]


class FairMOTModelRunnerConfig(
    FairMOTPreProcessRunnerConfig,
    OnnxRunnerConfig,
    FairMOTPostProcessRunnerConfig,
    dynamic=True,
):
    type: str = "FairMOTModelRunner"


class FairMOTModelRunner(Runner):
    config_type: Type[RunnerConfig] = FairMOTModelRunnerConfig
    outputs: List[str] = ["detections"]

    def prepare(self) -> "FairMOTModelRunner":
        config: FairMOTModelRunnerConfig = self.config

        self.onnx_runner = OnnxRunner(config)
        self.onnx_runner.prepare()

        for _, node_info in self.onnx_runner.metadata.items():
            if node_info.ntype == OnnxNodeType.input:
                self.input_info = node_info
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

        self.preproc_runner = FairMOTPreProcessRunner(config)
        self.preproc_runner.prepare()

        self.postproc_runner = FairMOTPostProcessRunner(config)
        self.postproc_runner.prepare()

        return self

    def run(
        self, images: Union[Image, Images], **kwargs
    ) -> Union[List[Detection], List[List[Detection]]]:
        config: FairMOTModelRunnerConfig = self.config

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

        candidates = []
        for i in range(0, len(preproc_images), config.batch_size):
            batch = preproc_images[i : i + config.batch_size]
            batch_size = len(batch)
            if batch_size < config.batch_size:
                batch += [
                    np.zeros(self.input_info.dims[1:], dtype=self.input_info.dtype)
                    for _ in range(config.batch_size - batch_size)
                ]

            batch = np.stack(batch)
            outputs = self.onnx_runner.run(**{self.input_info.name: batch})

            batch = batch[:batch_size, ...]
            outputs = {key: val[:batch_size, ...] for key, val in outputs.items()}

            detections = self.postproc_runner.run(**outputs)
            candidates.extend(detections)

        results = []
        for candidate, image in zip(candidates, images):
            height, width, _ = image.mat.shape
            top, bottom, left, right = image.padding

            result = []
            for detection in candidate:
                detection.left = clip(detection.left - left, 0, 1)
                detection.top = clip(detection.top - top, 0, 1)
                detection.right = clip(detection.right - right, 0, 1)
                detection.bottom = clip(detection.bottom - bottom, 0, 1)

                if (
                    detection.right <= detection.left
                    or detection.bottom <= detection.top
                ):
                    continue

                detection.left = math.floor(detection.left * width)
                detection.top = math.floor(detection.top * height)
                detection.right = math.floor(detection.right * width)
                detection.bottom = math.floor(detection.bottom * height)

                result.append(detection)

        results.append(result)

        if is_single_image:
            return results[0]

        return results
