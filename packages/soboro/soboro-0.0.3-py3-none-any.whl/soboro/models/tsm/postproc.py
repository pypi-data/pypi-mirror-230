# pyright: reportShadowedImports=false
from collections import deque
from typing import *

import numpy as np

from ...common import Classification, softmax
from ...runner import Runner, RunnerConfig

__all__ = ["TSMPostProcessRunner", "TSMPostProcessRunnerConfig"]


class TSMPostProcessRunnerConfig(RunnerConfig, dynamic=True):
    type: str = "TSMPostProcessRunnerConfig"
    classes: List[str]
    weights: List[float] = []

    max_segments: int = 30
    segment_size: int = 8
    overlap_size: int = 4
    step: int = 8

    @property
    def num_classes(self):
        return len(self.classes)


class TSMPostProcessRunner(Runner):
    config_type: Type[RunnerConfig] = TSMPostProcessRunnerConfig
    outputs: List[str] = ["classifications"]

    def prepare(self) -> "TSMPostProcessRunner":
        config: TSMPostProcessRunnerConfig = self.config
        assert (
            config.overlap_size < config.segment_size
        ), f"Segment size must be greater than overlap size"

        if len(config.weights) == 0:
            config.weights = [1] * config.num_classes

        assert len(config.weights) == config.num_classes, f"Invalid weight config"

        self.cls_scores = deque(maxlen=config.max_segments * config.segment_size)
        return self

    def reset(self):
        self.cls_scores.clear()

    def run(self, output: np.ndarray, **kwargs) -> List[Classification]:
        config: TSMPostProcessRunnerConfig = self.config
        batch_size, *_ = output.shape

        scores = []
        num_supporters = []

        for i in range(batch_size):
            self.cls_scores.append(output[i, ...])

            cls_scores = np.asarray(self.cls_scores)

            num_frames, *_ = cls_scores.shape
            index = num_frames - 1
            indices = []
            segment = []
            while True:
                segment.append(index)
                if len(segment) == config.segment_size:
                    indices.extend(segment)
                    index = segment[-config.overlap_size]
                    segment.clear()
                    continue

                index -= config.step
                if index < 0:
                    break

            segment_size = config.segment_size
            if not indices:
                segment_size = len(segment)
                indices.extend(segment)

            indices.reverse()

            cls_scores = cls_scores.take(indices, axis=0)
            cls_scores = cls_scores.reshape((-1, segment_size, config.num_classes))
            num_segments, *_ = cls_scores.shape
            num_supporters.append(num_segments * segment_size)

            avg_scores = np.mean(cls_scores, axis=1)
            scores.append(softmax(avg_scores))

        scores = np.asarray(scores)
        scores = np.mean(scores, axis=1)

        _, num_classes = scores.shape
        assert num_classes == len(config.classes), f"Missing classes"

        # labels = np.argmax(scores, axis=-1)
        classifications = []

        for i, (score, num_support) in enumerate(zip(scores, num_supporters)):
            classifications.append(
                Classification(scores=score, support=num_support, labels=config.classes)
            )

        return classifications
