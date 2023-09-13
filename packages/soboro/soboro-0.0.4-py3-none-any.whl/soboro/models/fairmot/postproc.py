# pyright: reportShadowedImports=false
from typing import *

import numpy as np

from ...common import Detection, clip, nms
from ...runner import Runner, RunnerConfig

__all__ = ["FairMOTPostProcessRunner", "FairMOTPostProcessRunnerConfig"]


class FairMOTPostProcessRunnerConfig(RunnerConfig):
    type: str = "FairMOTPostProcessRunner"
    hm_layer: str = "hm"
    wh_layer: str = "wh"
    reg_layer: str = "reg"

    conf_threshold: float = 0.5
    nms_threshold: float = 0.3

    top_k: int = 200

    height: int = -1
    width: int = -1
    batch_size: int = -1


class FairMOTPostProcessRunner(Runner):
    config_type = FairMOTPostProcessRunnerConfig
    outputs = ["detections"]

    def prepare(self) -> "FairMOTPostProcessRunner":
        config: FairMOTPostProcessRunnerConfig = self.config
        self.mapping = {
            config.hm_layer: "hm",
            config.wh_layer: "wh",
            config.reg_layer: "reg",
        }
        return self

    def generate_proposals(
        self, hm: np.ndarray, wh: np.ndarray, reg: np.ndarray
    ) -> List[Detection]:
        config: FairMOTPostProcessRunnerConfig = self.config

        _, output_height, output_width = hm.shape
        scores = []
        for row in range(output_height):
            for col in range(output_width):
                score = float(hm[0, row, col])
                if score > config.conf_threshold:
                    scores.append((score, row, col))

        scores.sort(key=lambda val: val[0], reverse=True)
        scores = scores[: config.top_k]

        proposals = []
        for score, row, col in scores:
            cx_offset, cy_offset = reg[row, col, :]
            left, top, right, bottom = wh[row, col, :]

            cx = col + cx_offset
            cy = row + cy_offset

            detection = Detection(
                prob=score,
                left=clip((cx - left) / output_width, 0, 1),
                top=clip((cy - top) / output_height, 0, 1),
                right=clip((cx + right) / output_width, 0, 1),
                bottom=clip((cy + bottom) / output_height, 0, 1),
            )
            # print(detection)

            proposals.append(detection)

        return proposals

    def run(self, **outputs: Dict[str, np.ndarray]) -> List[List[Detection]]:
        config: FairMOTPostProcessRunnerConfig = self.config

        outputs = {
            self.mapping[key]: val
            for key, val in outputs.items()
            if key in self.mapping
        }
        assert len(outputs) == len(self.mapping), "Missing keys"

        min_batch_size = min(tensor.shape[0] for tensor in outputs.values())
        max_batch_size = max(tensor.shape[0] for tensor in outputs.values())
        assert min_batch_size == max_batch_size, f"Batch size mismatch"

        batch_size = min_batch_size
        outputs = [{key: outputs[key][i] for key in outputs} for i in range(batch_size)]

        batch_proposals = []
        for output in outputs:
            batch_proposals.append(self.generate_proposals(**output))

        batch_objects = []
        for proposals in batch_proposals:
            proposals = nms(proposals, config.nms_threshold)

            objects = []
            for proposal in proposals:
                if proposal.right <= proposal.left or proposal.bottom <= proposal.top:
                    continue

                objects.append(proposal)

            batch_objects.append(objects)

        return batch_objects
