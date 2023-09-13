# pyright: reportShadowedImports=false
from collections import deque
from enum import Enum
from typing import *

from mousse import Dataclass, Field

from ...common import BBox, BBoxType, Detection
from .kalman_filter import KalmanFilter

__all__ = ["TrackState", "Track"]


class TrackState(str, Enum):
    New = "new"
    Tracked = "tracked"
    Lost = "lost"
    Removed = "removed"


class Track(Dataclass, dynamic=True):
    max_history: int = 5
    detection: Detection = None

    label: int
    frame_id: int = 0
    track_id: int = 0
    state: TrackState = TrackState.New

    kf: KalmanFilter = Field(factory=KalmanFilter, private=True)

    def __build__(self, **kwargs):
        self.bboxes: Sequence[BBox] = deque([], maxlen=self.max_history)

    @property
    def last_bbox(self) -> BBox:
        assert len(self.bboxes) > 0, "List of bboxes is empty"
        return self.bboxes[-1]

    @property
    def pred_bbox(self) -> BBox:
        bbox = BBox(rect=self.kf.mean[:4], type=BBoxType.xyah)
        return bbox.to("ltrb")

    @property
    def mean_area(self):
        return sum(bbox.area for bbox in self.bboxes) / (len(self.bboxes) or 1)

    @property
    def mean_score(self):
        return sum(bbox.score for bbox in self.bboxes) / (len(self.bboxes) or 1)
    
    def update(self, detection: Detection, frame_id: int, track_id: int = -1, *kwargs):
        self.detection = detection
        
        bbox = self.detection.to("ltrb")
        self.bboxes.append(bbox)
        self.label = self.detection.label

        self.frame_id = frame_id
        if self.track_id > 0:
            self.kf.update(self.last_bbox.to("xyah").astuple())
        else:
            self.kf.initiate(self.last_bbox.to("xyah").astuple())

        
        if track_id > 0:
            self.track_id = track_id
        
        self.state = TrackState.Tracked
        self.detection.track_id = track_id

    def predict(self):
        self.kf.predict()

    def __len__(self):
        return len(self.bboxes)
