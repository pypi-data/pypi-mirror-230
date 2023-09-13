# pyright: reportShadowedImports=false
import math
from typing import *

import numpy as np
from mousse import Dataclass

from ...common import Detection, clip
from ...runner import Runner, RunnerConfig

__all__ = ["YoloXPostProcessRunner", "YoloXPostProcessRunnerConfig"]


class YoloXGrid(Dataclass):
    x: int
    y: int
    stride: int


class YoloXPostProcessRunnerConfig(RunnerConfig):
    type: str = "YoloXPostProcessRunner"

    strides: List[int] = []
    conf_threshold: float = 0.5
    nms_threshold: float = 0.3

    height: int = -1
    width: int = -1
    num_anchors: int = -1
    num_classes: int = -1


class YoloxPostProcessInputData(Dataclass):
    images: np.ndarray
    output: np.ndarray


class YoloXPostProcessRunner(Runner):
    config_type = YoloXPostProcessRunnerConfig
    outputs = ["detections"]

    def prepare(self) -> "YoloXPostProcessRunner":
        config: YoloXPostProcessRunnerConfig = self.config

        self.grids: List[YoloXGrid] = []
        if config.width > 0 and config.height > 0:
            self.generate_grids()

        return self

    def generate_grids(self):
        config: YoloXPostProcessRunnerConfig = self.config
        self.grids.clear()

        for stride in config.strides:
            num_grid_w = config.width // stride
            num_grid_h = config.height // stride
            for y in range(num_grid_h):
                for x in range(num_grid_w):
                    self.grids.append(YoloXGrid(x=x, y=y, stride=stride))

        if config.num_anchors > 0:
            assert (
                len(self.grids) == config.num_anchors
            ), f"Number of anchors mismatch, expect {config.num_anchors}, get {len(self.grids)}"

    def generate_proposals(self, output: np.ndarray) -> List[Detection]:
        config: YoloXPostProcessRunnerConfig = self.config
        proposals = []
        for grid_idx, grid in enumerate(self.grids):
            tensor = output[grid_idx, ...]

            x_center = float(tensor[0] + grid.x) * grid.stride
            y_center = float(tensor[1] + grid.y) * grid.stride
            width = math.exp(tensor[2]) * grid.stride
            height = math.exp(tensor[3]) * grid.stride

            objectness = float(tensor[4])

            for class_idx in range(config.num_classes):
                cls_score = tensor[5 + class_idx]
                box_score = objectness * cls_score

                if box_score > config.conf_threshold:
                    left = x_center - width / 2
                    top = y_center - height / 2
                    right = x_center + width / 2
                    bottom = y_center + height / 2
                    proposals.append(
                        Detection(
                            left=left,
                            top=top,
                            right=right,
                            bottom=bottom,
                            label=class_idx,
                            prob=box_score,
                        )
                    )
        return proposals

    def nms(self, proposals: List[Detection]) -> List[Detection]:
        config: Detection = self.config
        selections: List[Detection] = []
        for proposal in proposals:
            keep = True

            area = proposal.width * proposal.height
            for selection in selections:
                left = max(proposal.left, selection.left)
                top = max(proposal.top, selection.top)
                right = min(proposal.right, selection.right)
                bottom = min(proposal.bottom, selection.bottom)

                if right <= left or bottom <= top:
                    continue

                inter_area = (right - left) * (bottom - top)
                union_area = area + selection.width * selection.height - inter_area

                if inter_area / union_area > config.nms_threshold:
                    keep = False
                    break

            if keep:
                selections.append(proposal)

        return selections

    def run(self, output: np.ndarray, **kwargs) -> List[List[Detection]]:
        config: YoloXPostProcessRunnerConfig = self.config

        batch_size, *_ = output.shape

        batch_proposals = []
        for sample_id in range(batch_size):
            sample_output = output[sample_id, ...]
            proposals = self.generate_proposals(sample_output)
            batch_proposals.append(proposals)

        batch_objects = []
        for proposals in batch_proposals:
            proposals.sort(key=lambda proposal: proposal.prob)
            proposals = self.nms(proposals)

            objects = []
            for proposal in proposals:
                proposal.left = clip(proposal.left, 0, config.width)
                proposal.top = clip(proposal.top, 0, config.height)
                proposal.right = clip(proposal.right, 0, config.width)
                proposal.bottom = clip(proposal.bottom, 0, config.height)

                if proposal.right <= proposal.left or proposal.bottom <= proposal.top:
                    continue

                proposal.left /= config.width
                proposal.top /= config.height
                proposal.right /= config.width
                proposal.bottom /= config.height

                objects.append(proposal)

            batch_objects.append(objects)

        return batch_objects
