# pyright: reportShadowedImports=false
from collections import OrderedDict
from enum import Enum
from typing import *
from mousse.types.dataclass import Dataclass

import numpy as np
import onnxruntime as ort

import onnx
from onnx.mapping import TENSOR_TYPE_TO_NP_TYPE

from ...runner import Runner, RunnerConfig

__all__ = ["OnnxRunner", "OnnxRunnerConfig", "OnnxNodeInfo", "OnnxNodeType"]


class OnnxNodeType(str, Enum):
    input: str = "input"
    output: str = "output"


class OnnxNodeInfo(Dataclass, dynamic=True):
    name: str
    dims: Tuple[int, ...]
    dtype: Any
    ntype: OnnxNodeType


class ProviderConfig(Dataclass, dynamic=True):
    type: str = "CPUExecutionProvider"
    params: Dict[str, Any] = {}


class OnnxRunnerConfig(RunnerConfig, dynamic=True):
    type: str = "OnnxRunner"
    path: str
    providers: List[ProviderConfig] = [ProviderConfig()]


class OnnxRunner(Runner):
    config_type: Type[RunnerConfig] = OnnxRunnerConfig

    @property
    def outputs(self) -> List[str]:
        return [output_node.name for output_node in self.model.graph.output]

    def prepare(self) -> "OnnxRunner":
        config: OnnxRunnerConfig = self.config
        self.model = onnx.load(config.path)
        self.nodes = OrderedDict()
        
        providers = []
        for provider in config.providers:
            if provider.params:
                providers.append((provider.type, provider.params))
                continue
            providers.append(provider.type)

        self.sess = ort.InferenceSession(
            config.path,
            providers=providers,
        )

        self.metadata.clear()
        for input_node in self.model.graph.input:
            dims = []
            for dim in input_node.type.tensor_type.shape.dim:
                dims.append(dim.dim_value)
            dtype = TENSOR_TYPE_TO_NP_TYPE[input_node.type.tensor_type.elem_type]
            node_info = OnnxNodeInfo(
                name=input_node.name,
                dims=tuple(dims),
                dtype=dtype,
                ntype=OnnxNodeType.input,
            )

            self.nodes[input_node.name] = node_info
            self.metadata[input_node.name] = node_info

        for output_node in self.model.graph.output:
            dims = []
            for dim in output_node.type.tensor_type.shape.dim:
                dims.append(dim.dim_value)
            dtype = TENSOR_TYPE_TO_NP_TYPE[output_node.type.tensor_type.elem_type]
            node_info = OnnxNodeInfo(
                name=output_node.name,
                dims=tuple(dims),
                dtype=dtype,
                ntype=OnnxNodeType.output,
            )

            self.nodes[output_node.name] = node_info
            self.metadata[output_node.name] = node_info

        return self

    def run(self, **inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        for input_node in self.model.graph.input:
            assert input_node.name in inputs, f"{input_node.name} not found"
            dtype = TENSOR_TYPE_TO_NP_TYPE[input_node.type.tensor_type.elem_type]
            inputs[input_node.name] = inputs[input_node.name].astype(dtype)

        output_mats = self.sess.run(None, inputs)
        return {key: val for key, val in zip(self.outputs, output_mats)}
