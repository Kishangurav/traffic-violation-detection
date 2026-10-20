import json
import os
from collections import defaultdict, deque

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CALIB_FILE = os.path.join(ROOT, "calibration.json")


class SpeedEstimator:
    def __init__(
        self,
        fps=30,
        speed_limit=50,
        calibration_file=CALIB_FILE,
        margin_x=1.5,
        margin_y=3.0,
        window_seconds=0.8,
        min_samples=8,
        max_step_m=0.8,
        max_speed=150,
    ):
        self.fps = fps if fps and fps > 0 else 30
        self.speed_limit = speed_limit
        self.min_samples = min_samples
        self.max_step_m = max_step_m
        self.max_speed = max_speed
        self.window_frames = max(min_samples + 2, int(self.fps * window_seconds))

        self.history = defaultdict(lambda: deque(maxlen=self.window_frames))
        self.recent = defaultdict(lambda: deque(maxlen=5))
        self.H = None
        self.bounds = None

        if os.path.exists(calibration_file):
            with open(calibration_file, encoding="utf-8") as f:
                data = json.load(f)

            self.H = cv2.getPerspectiveTransform(
                np.float32(data["image_points"]),
                np.float32(data["world_points"]),
            )

            width = max(p[0] for p in data["world_points"])
            length = max(p[1] for p in data["world_points"])
            # Speed is only measured inside the calibrated patch plus a margin.
            self.bounds = (-margin_x, width + margin_x, -margin_y, length + margin_y)

            print(
                f"[INFO] Speed calibration loaded (fps={self.fps:.1f}, "
                f"zone={width:.1f}x{length:.1f} m + margin)"
            )
        else:
            print(
                "[WARNING] calibration.json not found - speed estimation is OFF. "
                "Run: python scripts\\calibrate_speed.py"
            )

    def _to_world(self, x, y):
        pt = np.float32([[[x, y]]])
        wx, wy = cv2.perspectiveTransform(pt, self.H)[0][0]
        return float(wx), float(wy)

    def _in_zone(self, wx, wy):
        x_min, x_max, y_min, y_max = self.bounds
        return x_min <= wx <= x_max and y_min <= wy <= y_max

    def _forget(self, vehicle_id):
        self.history.pop(vehicle_id, None)
        self.recent.pop(vehicle_id, None)

    def update(self, vehicle_id, box, frame_idx):
        if self.H is None:
            return None

        x1, y1, x2, y2 = box
        # Bottom-center of the box = where the vehicle touches the road.
        wx, wy = self._to_world((x1 + x2) / 2, y2)

        if not self._in_zone(wx, wy):
            self._forget(vehicle_id)
            return None

        hist = self.history[vehicle_id]

        if hist:
            last_frame, last_x, last_y = hist[-1]
            gap = frame_idx - last_frame
            step = float(np.hypot(wx - last_x, wy - last_y))
            # A jump this large between frames is a tracker ID switch, not motion.
            if gap <= 0 or step > self.max_step_m * gap:
                self._forget(vehicle_id)
                hist = self.history[vehicle_id]

        hist.append((frame_idx, wx, wy))

        if len(hist) < self.min_samples:
            return None

        f0, x0, y0 = hist[0]
        dframes = frame_idx - f0
        if dframes < self.min_samples:
            return None

        dist = float(np.hypot(wx - x0, wy - y0))
        speed = dist / (dframes / self.fps) * 3.6

        if speed > self.max_speed:
            return None

        self.recent[vehicle_id].append(speed)
        return round(float(np.median(self.recent[vehicle_id])), 1)

    def is_speeding(self, speed):
        return speed is not None and speed > self.speed_limit