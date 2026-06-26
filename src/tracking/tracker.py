from __future__ import annotations

from typing import Dict, List, Tuple


class VehicleTracker:
    def __init__(self, max_history: int = 25):
        self.next_vehicle_id = 1
        self.max_history = max_history
        self.trajectories: Dict[int, List[Tuple[int, int]]] = {}

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

                x1, y1, x2, y2 = map(float, coords)
                boxes.append((int(x1), int(y1), int(x2), int(y2)))

        return boxes

    def update(self, results):
        detected_boxes = self._extract_boxes(results)
        tracked_objects = {}
        trajectories = {}

        for idx, box in enumerate(detected_boxes):
            vehicle_id = self.next_vehicle_id + idx
            tracked_objects[vehicle_id] = box

            center = ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)
            history = self.trajectories.get(vehicle_id, [])
            history.append(center)

            if len(history) > self.max_history:
                history.pop(0)

            trajectories[vehicle_id] = history

        if tracked_objects:
            self.next_vehicle_id = max(self.next_vehicle_id, max(tracked_objects.keys()) + 1)

        return tracked_objects, trajectories


__all__ = ["VehicleTracker"]
