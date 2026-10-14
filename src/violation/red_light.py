
import time
import cv2


class RedLightDetector:
    def __init__(self, stop_line_y=300, signal_state="red"):
        self.stop_line_y = int(stop_line_y)
        self.signal_state = signal_state.lower()

        # Previous bottom-edge position for each tracked vehicle
        self.previous_bottom_y = {}

        # Vehicles that have already crossed the stop line
        self.crossed_ids = set()

        # Confirmed red-light violations
        self.violations = {}

    def set_signal(self, state):
        self.signal_state = state.lower()

    def _get_bottom_center(self, box):
        x1, y1, x2, y2 = box
        return int((x1 + x2) / 2), int(y2)

    def check_violation(self, vehicle_id, box):
        _, current_y = self._get_bottom_center(box)
        previous_y = self.previous_bottom_y.get(vehicle_id)

        # Save the current position for the next frame.
        self.previous_bottom_y[vehicle_id] = current_y

        # We need a previous position to confirm a crossing.
        if previous_y is None:
            return False

        # Detect crossing from above the line to the line or below it.
        crossed_line = (
            previous_y < self.stop_line_y
            and current_y >= self.stop_line_y
        )

        if not crossed_line or vehicle_id in self.crossed_ids:
            return False

        # Mark the crossing so it cannot be counted repeatedly.
        self.crossed_ids.add(vehicle_id)

        # Only crossings during a red signal are violations.
        if self.signal_state != "red":
            return False

        self.violations[vehicle_id] = {
            "type": "red_light",
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "position": self._get_bottom_center(box),
        }

        return True

    def draw_stop_line(self, frame):
        height, width = frame.shape[:2]

        # Keep the configured line inside the image.
        line_y = max(0, min(self.stop_line_y, height - 1))

        color = (
            (0, 0, 255)
            if self.signal_state == "red"
            else (0, 255, 0)
        )

        cv2.line(
            frame,
            (0, line_y),
            (width - 1, line_y),
            color,
            3,
        )

        label_y = max(20, line_y - 10)

        cv2.putText(
            frame,
            f"Signal: {self.signal_state.upper()}",
            (10, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

        return frame

    def draw_violations(self, frame):
        # The dashboard already displays recent violations.
        # Avoid drawing additional labels over vehicles.
        return frame

    def get_violations(self):
        return self.violations

    def simulate_signal(self, interval=10):
        interval = max(1, int(interval))
        current_time = int(time.time())

        if (current_time // interval) % 2 == 0:
            self.signal_state = "red"
        else:
            self.signal_state = "green"


__all__ = ["RedLightDetector"]
