import time
import cv2


class RedLightDetector:
    def __init__(self, stop_line_y=300, signal_state="red"):
        self.stop_line_y = stop_line_y
        self.signal_state = signal_state
        self.previous_y = {}
        self.crossed_ids = set()
        self.violations = {}

    def set_signal(self, state):
        self.signal_state = state

    def _get_bottom_center(self, box):
        x1, y1, x2, y2 = box
        return (int((x1 + x2) / 2), y2)

    def crossing_condition(self, vehicle_id, box):
        """Return True only when a tracked vehicle moves from before to after the line while red."""
        _, current_y = self._get_bottom_center(box)
        previous_y = self.previous_y.get(vehicle_id)
        self.previous_y[vehicle_id] = current_y

        if previous_y is None:
            return False

        return (
            self.signal_state == "red"
            and previous_y < self.stop_line_y
            and current_y >= self.stop_line_y
        )

    def record_violation(self, vehicle_id, box):
        bottom_center = self._get_bottom_center(box)
        if vehicle_id in self.crossed_ids:
            return False

        self.crossed_ids.add(vehicle_id)
        self.violations[vehicle_id] = {
            "type": "red_light",
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "position": bottom_center,
            "signal_state": self.signal_state,
            "stop_line_y": self.stop_line_y,
            "verification": "temporal",
        }
        return True

    def check_violation(self, vehicle_id, box):
        """Backward-compatible direct check; use crossing_condition + temporal verification in the main pipeline."""
        if self.crossing_condition(vehicle_id, box):
            return self.record_violation(vehicle_id, box)
        return False

    def draw_stop_line(self, frame):
        h, w = frame.shape[:2]
        color = (0, 0, 255) if self.signal_state == "red" else (0, 255, 0)
        cv2.line(frame, (0, self.stop_line_y), (w, self.stop_line_y), color, 3)
        label = f"Signal: {self.signal_state.upper()}"
        cv2.putText(frame, label, (10, self.stop_line_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        return frame

    def draw_violations(self, frame):
        for vid, info in self.violations.items():
            px, py = info["position"]
            cv2.putText(
                frame, f"VIOLATION! ID:{vid}", (px - 60, py - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
            )
        return frame

    def get_violations(self):
        return self.violations

    def simulate_signal(self, interval=10):
        current = int(time.time())
        self.signal_state = "red" if (current // interval) % 2 == 0 else "green"


__all__ = ["RedLightDetector"]
