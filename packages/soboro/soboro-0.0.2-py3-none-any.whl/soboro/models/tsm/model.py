# pyright: reportShadowedImports=false
from collections import deque
from pathlib import Path
from typing import *

import numpy as np

from ...common import Classification, Image, Images, InputFormat
from ...runner import Runner, RunnerConfig
from ..onnx import OnnxNodeInfo, OnnxRunner, OnnxRunnerConfig, OnnxNodeType
from .postproc import TSMPostProcessRunner, TSMPostProcessRunnerConfig
from .preproc import TSMPreProcessRunner, TSMPreProcessRunnerConfig

__all__ = ["TSMModelRunner", "TSMModelRunnerConfig"]


class TSMModelRunnerConfig(
    TSMPreProcessRunnerConfig,
    OnnxRunnerConfig,
    TSMPostProcessRunnerConfig,
    dynamic=True,
):
    type: str = "TSMModelRunner"
    image_node: str = "images"
    score_node: str = "scores"
    batch_size: int = -1


class TSMModelRunner(Runner):
    config_type: Type[RunnerConfig] = TSMModelRunnerConfig

    def prepare(self) -> "TSMModelRunner":
        config: TSMModelRunnerConfig = self.config

        self.onnx_runner = OnnxRunner(config)
        self.onnx_runner.prepare()

        self.input_info: OnnxNodeInfo = self.onnx_runner.metadata[config.image_node]
        self.output_info: OnnxNodeInfo = self.onnx_runner.metadata[config.score_node]

        self.input_buffers: List[OnnxNodeInfo] = []
        self.output_buffers: List[OnnxNodeInfo] = []

        nodes_name = list(self.onnx_runner.metadata.keys())
        nodes_name.sort()

        for name in nodes_name:
            if name == config.image_node or name == config.score_node:
                continue

            node_info: OnnxNodeInfo = self.onnx_runner.metadata[name]
            if node_info.ntype == OnnxNodeType.input:
                self.input_buffers.append(node_info)

            if node_info.ntype == OnnxNodeType.output:
                self.output_buffers.append(node_info)

        self.shift_buffers: Deque[List[np.ndarray]] = deque(
            maxlen=config.max_segments * config.segment_size
        )
        self.zero_buffers: List[np.ndarray] = []
        for node_info in self.input_buffers:
            buffer = np.zeros(node_info.dims, dtype=node_info.dtype)
            self.zero_buffers.append(buffer)

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

        assert config.batch_size == 1, f"Invalid batch size: {config.batch_size}"

        self.preproc_runner = TSMPreProcessRunner(config)
        self.preproc_runner.prepare()

        self.postproc_runner = TSMPostProcessRunner(config)
        self.postproc_runner.prepare()

        return self

    def reset(self):
        self.shift_buffers.clear()
        self.preproc_runner.reset()
        self.postproc_runner.reset()

    def run(
        self,
        images: Union[Image, Images],
        tensor_save_path: str = None,
        tensor_save_txt: Path = None,
        **kwargs,
    ) -> Union[List[Classification], List[List[Classification]]]:
        config: TSMModelRunnerConfig = self.config

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
            mat = preproc_image.mat.astype(self.input_info.dtype)
            preproc_images.append(mat)

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

            inputs = {
                config.image_node: batch,
            }

            next_buffers = None
            if len(self.shift_buffers) >= config.step:
                next_buffers = self.shift_buffers[-config.step]
            else:
                next_buffers = self.zero_buffers

            for node_info, buffer in zip(self.input_buffers, next_buffers):
                inputs[node_info.name] = buffer

            if tensor_save_path:
                image_path = tensor_save_path.format(node_name=config.image_node)
                image_path = Path(image_path)
                image_path.parent.mkdir(parents=True, exist_ok=True)
                inputs[config.image_node].tofile(image_path.as_posix())

                paths = [image_path]
                for node_info in self.input_buffers:
                    node_path = tensor_save_path.format(node_name=node_info.name)
                    node_path = Path(node_path)
                    inputs[node_info.name].tofile(node_path.as_posix())
                    paths.append(node_path)

                if tensor_save_txt:
                    with open(tensor_save_txt, "a") as fout:
                        paths = [
                            path.relative_to(tensor_save_txt.parent).as_posix()
                            for path in paths
                        ]
                        fout.write(",".join(paths) + "\n")

            outputs = self.onnx_runner.run(**inputs)

            output = outputs[config.score_node]
            output_buffer = [
                outputs[node_info.name] for node_info in self.output_buffers
            ]
            self.shift_buffers.append(output_buffer)

            output = output[:batch_size, ...]

            classifications = self.postproc_runner.run(output=output)
            results.extend(classifications)

        if is_single_image:
            return results[0]

        return results
