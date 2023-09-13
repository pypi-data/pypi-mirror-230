# pyright: reportShadowedImports=false
from enum import Enum
from typing import *

import numpy as np
from mousse import Dataclass


__all__ = ["BBoxType", "BBox", "iou", "ioa"]


class BBoxType(str, Enum):
    ltrb: str = "ltrb"
    ltwh: str = "ltwh"
    xyah: str = "xyah"


def ltrb2ltwh(source: Tuple[float, float, float, float]):
    return (source[0], source[1], source[2] - source[0], source[3] - source[1])


def ltwh2ltrb(source: Tuple[float, float, float, float]):
    return (source[0], source[1], source[2] + source[0], source[3] + source[1])


def ltrb2xyah(source: Tuple[float, float, float, float]):
    return (
        (source[0] + source[2]) / 2,
        (source[1] + source[3]) / 2,
        (source[2] - source[0]) / (source[3] - source[1]),
        source[3] - source[1],
    )


def xyah2ltrb(source: Tuple[float, float, float, float]):
    x, y, aspect, height = source
    width = aspect * height
    return (x - width / 2, y - height / 2, x + width / 2, y + height / 2)


__CONVERTER__ = {
    (BBoxType.ltrb, BBoxType.ltwh): ltrb2ltwh,
    (BBoxType.ltwh, BBoxType.ltrb): ltwh2ltrb,
    (BBoxType.ltrb, BBoxType.xyah): ltrb2xyah,
    (BBoxType.xyah, BBoxType.ltrb): xyah2ltrb,
}


class BBox(Dataclass, dynamic=True):
    rect: Tuple[float, float, float, float]
    type: BBoxType = BBoxType.ltrb
    score: float = -1

    def to(self, btype: BBoxType) -> "BBox":
        if btype == self.type:
            return self

        if (self.type, btype) in __CONVERTER__:
            rect = __CONVERTER__[(self.type, btype)](self.rect)
            return BBox(rect=rect, type=btype, score=self.score)

        for itype in BBoxType:
            if (self.type, itype) in __CONVERTER__ and (itype, btype) in __CONVERTER__:
                rect = __CONVERTER__[(self.type, itype)](self.rect)
                rect = __CONVERTER__[(itype, btype)](rect)
                return BBox(rect=rect, type=btype, score=self.score)

        raise NotImplementedError()

    def asarray(self, dtype: Type[Any] = float) -> np.ndarray:
        return np.asarray(self.astuple(dtype=dtype))

    def astuple(self, dtype: Type[Any] = float) -> Tuple[float, float, float, float]:
        return tuple(dtype(val) for val in self.rect)

    @property
    def valid(self):
        if self.type == BBoxType.ltrb:
            if self.rect[2] < self.rect[0] or self.rect[3] < self.rect[1]:
                return False

            return True

        bbox = self.to(BBoxType.ltrb)
        return bbox.valid

    @property
    def width(self):
        if not self.valid:
            return 0

        if self.type == BBoxType.ltrb:
            return self.rect[2] - self.rect[0]

        return self.to("ltrb").width

    @property
    def height(self):
        if not self.valid:
            return 0

        if self.type == BBoxType.ltrb:
            return self.rect[3] - self.rect[1]

        return self.to("ltrb").height

    @property
    def area(self):
        return self.width * self.height if self.valid else 0

    def __and__(self, other: "BBox") -> "BBox":
        if other.type != BBoxType.ltrb:
            other = other.to("ltrb")

        curr = self
        if curr.type != BBoxType.ltrb:
            curr = self.to("ltrb")

        left = max(curr.rect[0], other.rect[0])
        top = max(curr.rect[1], other.rect[1])
        right = min(curr.rect[2], other.rect[2])
        bottom = min(curr.rect[3], other.rect[3])

        intersection = BBox(
            rect=[left, top, right, bottom],
            type=BBoxType.ltrb,
            score=(self.score + other.score) / 2,
        )
        intersection = intersection.to(self.type)
        if not intersection.valid:
            intersection.rect = (-1, -1, -1, -1)

        return intersection


def iou(a: BBox, b: BBox) -> float:
    intersection = a & b
    if intersection.area == 0:
        return 0
    return intersection.area / (a.area + b.area - intersection.area)


def ioa(a: BBox, b: BBox) -> float:
    intersection = a & b
    if intersection.area == 0:
        return 0
    return intersection.area / a.area
