# pyright: reportShadowedImports=false
from enum import Enum
from typing import *

import numpy as np
from mousse import Dataclass


__all__ = ["Image", "Images", "InputFormat", "ColorFormat", "PaddingFormat"]

Number = Union[int, float]


class Image(Dataclass, dynamic=True):
    mat: np.ndarray
    padding: Tuple[Number, Number, Number, Number] = (0, 0, 0, 0)


Images = List[Image]


class InputFormat(str, Enum):
    hwc: str = "hwc"
    chw: str = "chw"


class ColorFormat(str, Enum):
    rgb: str = "rgb"
    bgr: str = "bgr"
    yuv: str = "yuv"


class PaddingFormat(str, Enum):
    corner: str = "corner"
    center: str = "center"
