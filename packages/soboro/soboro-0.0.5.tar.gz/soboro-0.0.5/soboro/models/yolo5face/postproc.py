# pyright: reportShadowedImports=false
import math
from typing import *

import numpy as np
from mousse import Dataclass

from ...common import Detection, FaceDetection, Point, clip, nms, sigmoid
from ...runner import Runner, RunnerConfig

__all__ = ["Yolov5FacePostProcessRunner", "Yolov5FacePostProcessRunnerConfig"]

Size = Tuple[int, int]
Dims = Tuple[int, int, int, int, int]


class Yolov5FaceGrid(Dataclass):
    width: int
    height: int
    x: int
    y: int
    idx: int


class Yolov5FacePostProcessRunnerConfig(RunnerConfig):
    type: str = "Yolov5FacePostProcessRunner"

    outputs: Dict[str, Dims] = {}
    anchors: Dict[str, List[Size]] = []

    conf_threshold: float = 0.5
    nms_threshold: float = 0.3

    top_k: int = 1000

    height: int = -1
    width: int = -1
    batch_size: int = -1


class YoloxPostProcessInputData(Dataclass):
    images: np.ndarray
    output: np.ndarray


class Yolov5FacePostProcessRunner(Runner):
    config_type = Yolov5FacePostProcessRunnerConfig
    outputs = ["detections"]

    def prepare(self) -> "Yolov5FacePostProcessRunner":
        config: Yolov5FacePostProcessRunnerConfig = self.config

        self.grids: Dict[str, List[Yolov5FaceGrid]] = {}
        if config.width > 0 and config.height > 0:
            self.generate_grids()

        return self

    def generate_grids(self):
        config: Yolov5FacePostProcessRunnerConfig = self.config
        self.grids.clear()

        for key, dims in config.outputs.items():
            anchors = config.anchors[key]

            _, num_anchors_per_layer, num_grid_h, num_grid_w, _ = dims
            assert num_anchors_per_layer == len(
                anchors
            ), f"Mismatch num anchors per layer for {key}"

            grids = []
            for idx, (width, height) in enumerate(anchors):
                for y in range(num_grid_h):
                    for x in range(num_grid_w):
                        grids.append(
                            Yolov5FaceGrid(
                                x=x, y=y, width=width, height=height, idx=idx
                            )
                        )

            self.grids[key] = grids

    def generate_proposals(self, key: str, output: np.ndarray) -> List[Detection]:
        config: Yolov5FacePostProcessRunnerConfig = self.config

        proposals = []
        grids: List[Yolov5FaceGrid] = self.grids[key]
        _, num_grid_h, num_grid_w, num_features = output.shape

        for grid in grids:
            tensor = output[grid.idx, grid.y, grid.x, ...]

            stride_h = config.height / num_grid_h
            stride_w = config.width / num_grid_w

            obj_score = sigmoid(tensor[4])
            if obj_score < config.conf_threshold:
                continue

            cls_score = sigmoid(tensor[-1])
            if cls_score < config.conf_threshold:
                continue

            dx, dy, dw, dh = sigmoid(tensor[:4])

            x_center = (2 * dx - 0.5 + grid.x) * stride_w
            y_center = (2 * dy - 0.5 + grid.y) * stride_h
            width = math.pow(2 * dw, 2) * grid.width
            height = math.pow(2 * dh, 2) * grid.height

            proposal = FaceDetection(
                left=x_center - width / 2,
                top=y_center - height / 2,
                right=x_center + width / 2,
                bottom=y_center + height / 2,
                prob=cls_score,
            )

            num_keypoints = (num_features - 6) // 2
            for i in range(0, 2 * num_keypoints, 2):
                dx = float(tensor[i + 5])
                dy = float(tensor[i + 6])

                proposal.keypoints.append(
                    Point(
                        x=dx * grid.width + grid.x * stride_w,
                        y=dy * grid.height + grid.y * stride_h,
                    )
                )
            proposals.append(proposal)

        return proposals

    def run(self, **outputs: Dict[str, np.ndarray]) -> List[List[Detection]]:
        config: Yolov5FacePostProcessRunnerConfig = self.config

        min_batch_size = min(tensor.shape[0] for tensor in outputs.values())
        max_batch_size = max(tensor.shape[0] for tensor in outputs.values())
        assert min_batch_size == max_batch_size, f"Batch size mismatch"

        keys = list(outputs.keys())
        batch_size = min_batch_size

        outputs = [{key: outputs[key][i] for key in outputs} for i in range(batch_size)]

        batch_proposals = []
        for sample_id in range(batch_size):
            sample_proposals = []
            for key in keys:
                proposals = self.generate_proposals(key, outputs[sample_id][key])
                sample_proposals.extend(proposals)

            sample_proposals.sort(key=lambda proposal: proposal.prob, reverse=True)
            batch_proposals.append(sample_proposals[: config.top_k])

        batch_objects = []
        for proposals in batch_proposals:
            proposals = nms(proposals, config.nms_threshold)

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

                for point in proposal.keypoints:
                    point.x /= config.width
                    point.y /= config.height

                objects.append(proposal)

            batch_objects.append(objects)

        return batch_objects
