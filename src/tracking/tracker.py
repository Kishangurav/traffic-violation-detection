
from __future__ import annotations

from typing import Dict, List, Tuple
import math


Box = Tuple[int, int, int, int]
Point = Tuple[int, int]


class VehicleTracker:
    def __init__(
        self,
        max_history: int = 25,
        max_distance: float = 100.0,
        max_missed: int = 30,
        iou_threshold: float = 0.05,
    ):
        self.next_vehicle_id = 1
        self.max_history = max(1, int(max_history))
        self.max_distance = float(max_distance)
        self.max_missed = max(1, int(max_missed))
        self.iou_threshold = float(iou_threshold)

        # Each track stores its latest box, trajectory and missed frames.
        self.tracks = {}
        self.trajectories: Dict[int, List[Point]] = {}

    def _extract_boxes(self, results) -> List[Box]:
        boxes = []

        for result in results:
            for detection in getattr(result, "boxes", []):
                cls_value = getattr(detection, "cls", None)

                if cls_value is None:
                    continue

                cls = int(cls_value[0])

                # COCO vehicle classes: car, motorcycle, bus, truck.
                if cls not in [2, 3, 5, 7]:
                    continue

                coords = detection.xyxy[0]

                if hasattr(coords, "tolist"):
                    coords = coords.tolist()

                x1, y1, x2, y2 = map(int, coords)
                boxes.append((x1, y1, x2, y2))

        return boxes

    @staticmethod
    def _center(box: Box) -> Point:
        x1, y1, x2, y2 = box
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    @staticmethod
    def _iou(box_a: Box, box_b: Box) -> float:
        ax1, ay1, ax2, ay2 = box_a
        bx1, by1, bx2, by2 = box_b

        ix1 = max(ax1, bx1)
        iy1 = max(ay1, by1)
        ix2 = min(ax2, bx2)
        iy2 = min(ay2, by2)

        intersection_width = max(0, ix2 - ix1)
        intersection_height = max(0, iy2 - iy1)
        intersection = intersection_width * intersection_height

        area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
        area_b = max(0, bx2 - bx1) * max(0, by2 - by1)

        union = area_a + area_b - intersection

        return intersection / union if union > 0 else 0.0

    def update(self, results):
        detected_boxes = self._extract_boxes(results)

        # Mark existing tracks as not updated this frame.
        for track in self.tracks.values():
            track["missed"] += 1

        tracked_objects = {}
        trajectories = {}

        # Build possible matches between existing tracks and detections.
        candidates = []

        for vehicle_id, track in self.tracks.items():
            old_box = track["box"]
            old_center = self._center(old_box)

            for detection_index, new_box in enumerate(detected_boxes):
                new_center = self._center(new_box)

                distance = math.hypot(
                    new_center[0] - old_center[0],
                    new_center[1] - old_center[1],
                )

                overlap = self._iou(old_box, new_box)

                # Reject detections too far away unless boxes overlap.
                if (
                    distance > self.max_distance
                    and overlap < self.iou_threshold
                ):
                    continue

                # Prefer high overlap, then smaller center distance.
                distance_score = max(
                    0.0,
                    1.0 - distance / max(self.max_distance, 1.0),
                )

                score = overlap + 0.25 * distance_score

                candidates.append(
                    (score, vehicle_id, detection_index)
                )

        candidates.sort(reverse=True)

        matched_tracks = set()
        matched_detections = set()

        # Greedily assign each track and detection at most once.
        for _, vehicle_id, detection_index in candidates:
            if vehicle_id in matched_tracks:
                continue

            if detection_index in matched_detections:
                continue

            box = detected_boxes[detection_index]

            self.tracks[vehicle_id]["box"] = box
            self.tracks[vehicle_id]["missed"] = 0

            center = self._center(box)
            history = self.trajectories.setdefault(vehicle_id, [])
            history.append(center)

            if len(history) > self.max_history:
                del history[:-self.max_history]

            tracked_objects[vehicle_id] = box
            trajectories[vehicle_id] = history

            matched_tracks.add(vehicle_id)
            matched_detections.add(detection_index)

        # Give unmatched detections new IDs.
        for detection_index, box in enumerate(detected_boxes):
            if detection_index in matched_detections:
                continue

            vehicle_id = self.next_vehicle_id
            self.next_vehicle_id += 1

            center = self._center(box)

            self.tracks[vehicle_id] = {
                "box": box,
                "missed": 0,
            }

            self.trajectories[vehicle_id] = [center]

            tracked_objects[vehicle_id] = box
            trajectories[vehicle_id] = self.trajectories[vehicle_id]

        # Remove tracks that have been missing for too long.
        expired_ids = [
            vehicle_id
            for vehicle_id, track in self.tracks.items()
            if track["missed"] > self.max_missed
        ]

        for vehicle_id in expired_ids:
            del self.tracks[vehicle_id]
            self.trajectories.pop(vehicle_id, None)

        return tracked_objects, trajectories


__all__ = ["VehicleTracker"]
