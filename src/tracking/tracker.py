from __future__ import annotations

from typing import Dict, List, Tuple
import math


class VehicleTracker:
    """Lightweight IoU-based multi-object tracker.

    This keeps a persistent vehicle ID when a detection in the next frame
    overlaps sufficiently with the previous frame's bounding box.
    """

    def __init__(self, max_history: int = 25, max_distance: float = 100.0, iou_threshold: float = 0.25):
        self.next_vehicle_id = 1
        self.max_history = max_history
        self.max_distance = max_distance
        self.iou_threshold = iou_threshold
        self.tracks: Dict[int, Tuple[int, int, int, int]] = {}
        self.trajectories: Dict[int, List[Tuple[int, int]]] = {}
        self.missed: Dict[int, int] = {}

    @staticmethod
    def _iou(a, b) -> float:
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
        inter = iw * ih
        area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
        area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
        union = area_a + area_b - inter
        return inter / union if union else 0.0

    @staticmethod
    def _center(box):
        x1, y1, x2, y2 = box
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    def _extract_boxes(self, results):
        boxes = []
        for result in results:
            for box in getattr(result, "boxes", []) or []:
                cls = int(box.cls[0]) if getattr(box, "cls", None) is not None else None
                if cls not in [2, 3, 5, 7]:
                    continue
                coords = box.xyxy[0]
                if hasattr(coords, "tolist"):
                    coords = coords.tolist()
                x1, y1, x2, y2 = map(int, coords)
                boxes.append((x1, y1, x2, y2))
        return boxes

    def update(self, results):
        detections = self._extract_boxes(results)
        assignments = {}
        unused_tracks = set(self.tracks)

        # Greedy matching by highest IoU.
        candidates = []
        for vid, old_box in self.tracks.items():
            for idx, new_box in enumerate(detections):
                iou = self._iou(old_box, new_box)
                old_c = self._center(old_box)
                new_c = self._center(new_box)
                distance = math.hypot(old_c[0] - new_c[0], old_c[1] - new_c[1])
                if iou >= self.iou_threshold or distance <= self.max_distance:
                    candidates.append((iou, -distance, vid, idx))

        for _, __, vid, idx in sorted(candidates, reverse=True):
            if vid not in unused_tracks or idx in assignments:
                continue
            assignments[idx] = vid
            unused_tracks.remove(vid)

        # Unmatched detections start new tracks.
        for idx in range(len(detections)):
            if idx not in assignments:
                assignments[idx] = self.next_vehicle_id
                self.next_vehicle_id += 1

        tracked_objects = {}
        trajectories = {}

        for idx, box in enumerate(detections):
            vid = assignments[idx]
            tracked_objects[vid] = box
            self.tracks[vid] = box
            self.missed[vid] = 0

            history = self.trajectories.setdefault(vid, [])
            history.append(self._center(box))
            if len(history) > self.max_history:
                del history[0]
            trajectories[vid] = list(history)

        for vid in list(unused_tracks):
            self.missed[vid] = self.missed.get(vid, 0) + 1
            if self.missed[vid] > 30:
                self.tracks.pop(vid, None)
                self.missed.pop(vid, None)

        return tracked_objects, trajectories


__all__ = ["VehicleTracker"]
