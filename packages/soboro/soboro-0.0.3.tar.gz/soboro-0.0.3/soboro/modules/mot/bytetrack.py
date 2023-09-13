# pyright: reportShadowedImports=false
from typing import *

import numpy as np
from scipy.optimize import linear_sum_assignment

from ...runner import Runner, RunnerConfig
from ...common import Detection, BBox, iou
from .track import Track, TrackState


__all__ = ["ByteTrackRunner", "ByteTrackRunnerConfig"]


def area_similarity(target_area: float, ref_bbox: BBox) -> float:
    similarity = 1 - abs(ref_bbox.area - target_area) / target_area
    return max(0, similarity)


def linear_assignment(cost_matrix: np.ndarray, threshold: float):
    if cost_matrix.size == 0:
        return (
            np.empty((0, 2), dtype=int),
            tuple(range(cost_matrix.shape[0])),
            tuple(range(cost_matrix.shape[1])),
        )
    candidate_rows, candidate_cols = linear_sum_assignment(cost_matrix)

    matched_rows = np.zeros(cost_matrix.shape[0])
    matches_cols = np.zeros(cost_matrix.shape[1])

    matches = []
    for row, col in zip(candidate_rows, candidate_cols):
        cost = cost_matrix[row, col]
        if cost < threshold:
            matches.append((row, col))
            matched_rows[row] = 1
            matches_cols[col] = 1

    matches = np.asarray(matches)
    unmatched_a = np.where(matched_rows == 0)[0]
    unmatched_b = np.where(matches_cols == 0)[0]

    return matches, unmatched_a, unmatched_b


def ious(a_bboxes: List[BBox], b_bboxes: List[BBox]) -> np.ndarray:
    """
    Compute cost based on IoU
    :rtype ious np.ndarray
    """
    _ious = np.zeros((len(a_bboxes), len(b_bboxes)), dtype=float)
    if _ious.size == 0:
        return _ious

    for i, a_bbox in enumerate(a_bboxes):
        for j, b_bbox in enumerate(b_bboxes):
            _ious[i, j] = iou(a_bbox, b_bbox)

    return _ious


def localization_cost(
    tracks: Sequence[Track],
    detections: Sequence[Detection],
    iou_weight: float = 0.6,
    diff_weight: float = 0.4,
) -> np.ndarray:
    detections = [detection.to("ltrb") for detection in detections]

    curr_ious = ious([track.pred_bbox for track in tracks], detections)

    area_similarity_matrix = np.zeros(curr_ious.shape)
    inds = np.nonzero(curr_ious > 0)

    tracks_mean_area = [track.mean_area for track in tracks]
    for i, j in zip(inds[0], inds[1]):
        area_similarity_matrix[i][j] = area_similarity(tracks_mean_area[i], detections[j])

    cost_matrix = 1 - (curr_ious * iou_weight + area_similarity_matrix * diff_weight)
    return cost_matrix


def fuse_score(
    cost_matrix: np.ndarray,
    detections: Sequence[Detection],
    tracks: Sequence[Track],
    score_weight: float = 0.3,
    use_label: bool = False,
) -> np.ndarray:
    if cost_matrix.size == 0:
        return cost_matrix

    det_scores = np.array([det.prob for det in detections])
    det_scores = np.expand_dims(det_scores, axis=0).repeat(cost_matrix.shape[0], axis=0)

    mean_scores = np.array([[track.mean_score] for track in tracks])
    assert mean_scores.shape[0] == cost_matrix.shape[0]
    mean_scores = np.repeat(mean_scores, det_scores.shape[1], axis=1)
    
    det_scores = score_weight * mean_scores + (1 - score_weight) * det_scores

    similariry = (1 - cost_matrix) * det_scores
    cost = 1 - similariry

    if use_label:
        for i, track in enumerate(tracks):
            for j, detection in enumerate(detections):
                if track.detection.label != detection.label:
                    cost[i, j] = 1

    return cost


class ByteTrackRunnerConfig(RunnerConfig, dynamic=True):
    type: str = "ByteTrackRunner"

    match_threshold: float = 0.85
    unconfirmed_threshold: float = 0.7
    link_threshold: float = 0.85
    max_time_lost: int = 30
    max_track_id: int = 10000

    max_history: int = 5
    min_history: int = 1

    use_label: bool = False


class ByteTrackRunner(Runner):
    config_type: Type[RunnerConfig] = ByteTrackRunnerConfig
    outputs: List[str] = ["tracks"]

    def prepare(self) -> "ByteTrackRunner":
        self.tracks: List[Track] = []
        self.frame_id = 0
        self.track_id = 0

    def reset(self):
        self.tracks.clear()
        self.frame_id = 0
        self.track_id = 0

    def next_id(self):
        self.track_id = (self.track_id + 1) % self.config.max_track_id
        return self.track_id

    def link_tracks_and_detections(
        self,
        tracks: Sequence[Track],
        detections: Sequence[Detection],
        threshold: float = 0.85,
    ):
        det_ltrbs = [det.to("ltrb") for det in detections]
        track_ltrbs = [
            track.last_bbox.to("ltrb")
            if track.state != TrackState.Tracked
            else track.pred_bbox.to("ltrb")
            for track in tracks
        ]
        dists = 1 - ious(track_ltrbs, det_ltrbs)
        matching_pairs = {}
        confused_tracks = []
        for i, _ in enumerate(dists):
            candidate_ids = [j for j, dist in enumerate(dists[i]) if dist < 1]
            if len(candidate_ids) != 0:
                for j in candidate_ids:
                    if j not in matching_pairs:
                        matching_pairs[j] = [i]
                    else:
                        matching_pairs[j].append(i)
                if len(candidate_ids) > 1:
                    confused_tracks.append(i)

        linked_tracks, linked_dets = [], []
        for det_idx, matching_tracks in matching_pairs.items():
            if len(matching_tracks) == 1 and matching_tracks[0] not in confused_tracks:
                matching_track_id = matching_tracks[0]
                _area_similarity = area_similarity(
                    tracks[matching_track_id].mean_area, det_ltrbs[det_idx]
                )
                if _area_similarity > threshold:
                    linked_dets.append(det_idx)
                    linked_tracks.append(matching_track_id)

        return linked_tracks, linked_dets

    def get_comfirmed_tracks(self):
        tracks_pool: Sequence[Track] = []
        for track in self.tracks:
            if track.state != TrackState.New:
                tracks_pool.append(track)

        return tracks_pool

    def get_unmatched_detections(self, detections: Sequence[Detection]):
        return [detection for detection in detections if not detection.matched]

    def get_unmatched_tracks(self, state: TrackState = None):
        tracks_pool = self.get_comfirmed_tracks()
        return [
            track
            for track in tracks_pool
            if track.frame_id != self.frame_id
            and (state is None or track.state == state)
        ]

    def associate_confirmed_tracks(self, detections: Sequence[Detection]):
        tracks_pool = self.get_comfirmed_tracks()

        for track in tracks_pool:
            track.predict()

        matches, *_ = linear_assignment(
            fuse_score(
                cost_matrix=localization_cost(tracks_pool, detections),
                detections=detections,
                tracks=tracks_pool,
                use_label=self.config.use_label,
            ),
            threshold=self.config.match_threshold,
        )

        for itrack, idet in matches:
            track = tracks_pool[itrack]
            detection = detections[idet]
            detection.matched = True
            track.update(detection, self.frame_id)

        u_detections = self.get_unmatched_detections(detections)
        u_tracks = self.get_unmatched_tracks(TrackState.Tracked)

        linked_tracks, linked_dets = self.link_tracks_and_detections(
            u_tracks, u_detections, self.config.link_threshold
        )
        for track_idx, det_idx in zip(linked_tracks, linked_dets):
            track = u_tracks[track_idx]
            detection = u_detections[det_idx]
            detection.matched = True
            track.update(detection, self.frame_id)

    def get_unconfirmed_trasks(self):
        u_tracks: Sequence[Track] = []
        for track in self.tracks:
            if track.state == TrackState.New:
                u_tracks.append(track)

        return u_tracks

    def associate_unconfirmed_tracks(self, detections: Sequence[Detection]):
        u_tracks = self.get_unconfirmed_trasks()
        u_detections = self.get_unmatched_detections(detections)
        
        dists = fuse_score(
            1 - ious([
                track.last_bbox for track in u_tracks
            ], u_detections),
            detections=u_detections,
            tracks=u_tracks,
            use_label=self.config.use_label,
        )

        matches, _, _ = linear_assignment(
            dists, threshold=self.config.unconfirmed_threshold
        )
        for itrack, idet in matches:
            detection = u_detections[idet]
            track = u_tracks[itrack]
            detection.matched = True
            track.update(detection, self.frame_id)

        u_tracks = self.get_unconfirmed_trasks()
        u_detections = self.get_unmatched_detections(detections)
        linked_tracks, linked_dets = self.link_tracks_and_detections(
            u_tracks, u_detections, threshold=self.config.link_threshold
        )
        for track_idx, det_idx in zip(linked_tracks, linked_dets):
            track = u_tracks[track_idx]
            detection = u_detections[det_idx]
            detection.matched = True
            track.update(detection, self.frame_id)

    def update_current_tracks(self, detections: Sequence[Detection]):
        for track in self.tracks:
            if track.state != TrackState.Lost and track.frame_id != self.frame_id:
                track.state = TrackState.Lost

        for detection in detections:
            if not detection.matched:
                track = Track(max_history=self.config.max_history)
                detection.matched = True
                track.update(detection, self.frame_id, self.next_id())
                self.tracks.append(track)

        for track in self.tracks:
            if self.frame_id - track.frame_id > self.config.max_time_lost:
                track.state = TrackState.Removed

        self.tracks = [
            track for track in self.tracks if track.state != TrackState.Removed
        ]

    def run(self, detections: Sequence[Detection]) -> Sequence[Detection]:
        self.frame_id += 1

        for detection in detections:
            detection.matched = False

        self.associate_confirmed_tracks(detections)
        self.associate_unconfirmed_tracks(detections)
        self.update_current_tracks(detections)

        return [track for track in self.tracks if len(track) >= self.config.min_history]
