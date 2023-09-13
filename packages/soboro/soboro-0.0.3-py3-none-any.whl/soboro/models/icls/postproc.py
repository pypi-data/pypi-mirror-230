# pyright: reportShadowedImports=false
from typing import *

import numpy as np

from ...common import Classification
from ...runner import Runner, RunnerConfig

__all__ = ["ICLSPostProcessRunner", "ICLSPostProcessRunnerConfig"]


class ICLSPostProcessRunnerConfig(RunnerConfig, dynamic=True):
    type: str = "ICLSPostProcessRunnerConfig"
    classes: List[str]


class ICLSPostProcessRunner(Runner):
    config_type: Type[RunnerConfig] = ICLSPostProcessRunnerConfig
    outputs: List[str] = ["classifications"]

    def prepare(self) -> "ICLSPostProcessRunner":
        return self

    def run(self, output: np.ndarray, **kwargs) -> List[Classification]:
        config: ICLSPostProcessRunnerConfig = self.config

        _, num_classes = output.shape
        assert num_classes == len(config.classes), f"Missing classes"

        classifications = []
        for i, scores in enumerate(output):
            scores = output[i, ...].tolist()
            classifications.append(Classification(scores=scores, labels=config.classes))

        return classifications
