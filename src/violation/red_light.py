import json
import os
import time

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LINE_FILE = os.path.join(ROOT, "stop_line.json")


class RedLightDetector:
    def __init__(
        self,
        stop_line_y=500,
        line_file=LINE_FILE,
        min_track_frames=5,
        deadband_px=4,
    ):
        self.min_track_frames = min_track_frames
        self.deadband_px = deadband_px

        self.signal_state = "GREEN"
        self._last_toggle = time.time()

        self._last_side = {}
        self._seen_frames = {}
        self._violation_ids = []
        self._flash = {}

        # Default: a horizontal line; vehicles approach from above (smaller y).
        self.p1 = (0.0, float(stop_line_y))
        self.p2 = (10000.0, float(stop_line_y))
        self.approach_sign = -1

        if os.path.exists(line_file):
            with open(line_file, encoding="utf-8") as f:
                data = json.load(f)
            self.p1 = tuple(data["p1"])
            self.p2 = tuple(data["p2"])
            self.approach_sign = 1 if self._cross(tuple(data["approach_point"])) > 0 else -1
            print("[INFO] Stop line loaded from stop_line.json")
        else:
            print(
                "[WARNING] stop_line.json not found - using horizontal stop_line_y. "
                "Run: python scripts\\set_stop_line.py"
            )

    # ----- geometry -----

    def _cross(self, pt):
        (x1, y1), (x2, y2) = self.p1, self.p2
        return (x2 - x1) * (pt[1] - y1) - (y2 - y1) * (pt[0] - x1)

    def _signed_distance(self, pt):
        (x1, y1), (x2, y2) = self.p1, self.p2
        length = float(np.hypot(x2 - x1, y2 - y1)) or 1.0
        return self._cross(pt) / length

    def _along_segment(self, pt):
        (x1, y1), (x2, y2) = self.p1, self.p2
        dx, dy = x2 - x1, y2 - y1
        denom = dx * dx + dy * dy or 1.0
        return ((pt[0] - x1) * dx + (pt[1] - y1) * dy) / denom

    # ----- signal (simulated) -----

    def simulate_signal(self, interval=10):
        if os.environ.get("FORCE_RED") == "1":
            self.signal_state = "RED"
            return

        now = time.time()
        if now - self._last_toggle >= interval:
            self.signal_state = "RED" if self.signal_state == "GREEN" else "GREEN"
            self._last_toggle = now

    # ----- violation logic -----

    def check_violation(self, vehicle_id, box):
        x1, y1, x2, y2 = box
        # Bottom-center of the box = where the vehicle touches the road.
        pt = ((x1 + x2) / 2.0, float(y2))

        count = self._seen_frames.get(vehicle_id, 0) + 1
        self._seen_frames[vehicle_id] = count

        # Ignore vehicles beside the ends of the line.
        if not (-0.05 <= self._along_segment(pt) <= 1.05):
            return False

        dist = self._signed_distance(pt)
        if abs(dist) <= self.deadband_px:
            return False

        side = 1 if dist > 0 else -1
        prev = self._last_side.get(vehicle_id)
        self._last_side[vehicle_id] = side

        if prev is None or count < self.min_track_frames:
            return False

        crossed = prev == self.approach_sign and side == -self.approach_sign

        if (
            crossed
            and self.signal_state == "RED"
            and vehicle_id not in self._violation_ids
        ):
            self._violation_ids.append(vehicle_id)
            self._flash[vehicle_id] = (
                tuple(int(v) for v in box),
                time.time() + 3.0,
            )
            return True

        return False

    def get_violations(self):
        return list(self._violation_ids)

    # ----- drawing -----

    def draw_stop_line(self, frame):
        color = (0, 0, 255) if self.signal_state == "RED" else (0, 255, 0)
        p1 = (int(self.p1[0]), int(self.p1[1]))
        p2 = (int(self.p2[0]), int(self.p2[1]))
        cv2.line(frame, p1, p2, color, 3)
        cv2.putText(
            frame, "STOP LINE", (p1[0] + 5, max(p1[1] - 8, 15)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
        )
        return frame

    def draw_violations(self, frame):
        now = time.time()
        for vid in list(self._flash):
            box, expires = self._flash[vid]
            if now > expires:
                del self._flash[vid]
                continue
            x1, y1, x2, y2 = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(
                frame, f"RED LIGHT ID:{vid}", (x1, max(y1 - 10, 15)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
            )
        return frame