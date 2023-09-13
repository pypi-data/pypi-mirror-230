# pyright: reportShadowedImports=false
from typing import *

import numpy as np
from .types import Detection

__all__ = ["clip", "sigmoid", "nms", "softmax"]


def clip(val: float, lower: float, upper: float):
    return lower if val < lower else upper if val > upper else val


def sigmoid(x: Union[np.ndarray, float]):
    return 1 / (1 + np.exp(-x))


def softmax(x: np.ndarray, axis: int = -1):
    """Compute softmax values for each sets of scores in x."""
    sum_score = np.sum(np.exp(x), axis=axis)
    sum_score = sum_score[:, np.newaxis]
    return np.exp(x) / sum_score


def nms(proposals: List[Detection], nms_threshold: float) -> List[Detection]:
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

            if inter_area / union_area > nms_threshold:
                keep = False
                break

        if keep:
            selections.append(proposal)

    return selections
