# pyright: reportShadowedImports=false
from typing import *

from mousse import Dataclass
from .bbox import BBox, BBoxType

__all__ = ["Point", "Classification", "Detection", "FaceDetection"]


class Point(Dataclass, dynamic=True):
    x: float
    y: float


class Classification(Dataclass, dynamic=True):
    scores: List[float]
    labels: List[str]

    def __getitem__(self, label: str):
        if label not in self.labels:
            raise IndexError(label)

        return self.scores[self.labels.index(label)]


class Detection(Dataclass, dynamic=True):
    left: float
    top: float
    right: float
    bottom: float
    prob: float
    label: int

    track_id: int = -1

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    def to(self, btype: BBoxType) -> BBox:
        bbox = BBox(
            rect=(self.left, self.top, self.right, self.bottom),
            type=BBoxType.ltrb,
            score=self.prob,
        )

        if btype == BBoxType.ltrb:
            return bbox

        return bbox.to(btype)


class FaceDetection(Detection, dynamic=True):
    keypoints: List[Point] = []
