import cv2
import numpy as np
import time
from collections import defaultdict

class SpeedEstimator:
    def __init__(self, fps=30, speed_limit=50):
        self.fps = fps
        self.speed_limit = speed_limit
        self.entry_time = {}
        self.entry_position = {}
        self.speed_records = defaultdict(list)

        # Calibration points - adjust these to match your video
        self.pixel_points = np.float32([
            [100, 400],
            [540, 400],
            [540, 280],
            [100, 280]
        ])
        self.world_points = np.float32([
            [0, 0],
            [10, 0],
            [10, 20],
            [0, 20]
        ])

        self.H, _ = cv2.findHomography(self.pixel_points, self.world_points)

    def _pixel_to_world(self, pixel_point):
        pt = np.float32([[pixel_point]])
        world = cv2.perspectiveTransform(pt, self.H)
        return world[0][0]

    def _get_center(self, box):
        x1, y1, x2, y2 = box
        return (int((x1 + x2) / 2), int((y1 + y2) / 2))

    def update(self, vehicle_id, box):
        center = self._get_center(box)
        current_time = time.time()

        if vehicle_id not in self.entry_time:
            self.entry_time[vehicle_id] = current_time
            self.entry_position[vehicle_id] = center
            return None

        time_elapsed = current_time - self.entry_time[vehicle_id]

        if time_elapsed < 0.5:
            return None

        # Convert to world coordinates
        world_entry = self._pixel_to_world(self.entry_position[vehicle_id])
        world_current = self._pixel_to_world(center)

        # Distance in meters
        dx = world_current[0] - world_entry[0]
        dy = world_current[1] - world_entry[1]
        distance = np.sqrt(dx**2 + dy**2)

        # Speed in km/h
        speed = (distance / time_elapsed) * 3.6

        # Smooth over last 5 readings
        self.speed_records[vehicle_id].append(speed)
        if len(self.speed_records[vehicle_id]) > 5:
            self.speed_records[vehicle_id].pop(0)

        avg_speed = np.mean(self.speed_records[vehicle_id])

        # Update for next calculation
        self.entry_time[vehicle_id] = current_time
        self.entry_position[vehicle_id] = center

        return round(avg_speed, 1)

    def is_speeding(self, speed):
        if speed is None:
            return False
        return speed > self.speed_limit