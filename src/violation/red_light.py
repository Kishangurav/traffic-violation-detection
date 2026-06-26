import time

import cv2


class RedLightDetector:
    def __init__(self, stop_line_y=300, signal_state="red"):
        self.stop_line_y = stop_line_y
        self.signal_state = signal_state
        self.crossed_ids = set()
        self.violations = {}

    def set_signal(self, state):
        self.signal_state = state

    def _get_bottom_center(self, box):
        x1, y1, x2, y2 = box
        return (int((x1 + x2) / 2), y2)

    def check_violation(self, vehicle_id, box):
        bottom_center = self._get_bottom_center(box)
        bx, by = bottom_center

        if by >= self.stop_line_y:
            if self.signal_state == "red":
                if vehicle_id not in self.crossed_ids:
                    self.crossed_ids.add(vehicle_id)
                    self.violations[vehicle_id] = {
                        "type": "red_light",
                        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "position": bottom_center,
                    }
                    return True
        return False

    def draw_stop_line(self, frame):
        h, w = frame.shape[:2]
        color = (0, 0, 255) if self.signal_state == "red" else (0, 255, 0)
        cv2.line(frame, (0, self.stop_line_y), (w, self.stop_line_y), color, 3)
        label = f"Signal: {self.signal_state.upper()}"
        cv2.putText(frame, label, (10, self.stop_line_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        return frame

    def draw_violations(self, frame):
        for vid, info in self.violations.items():
            px, py = info["position"]
            cv2.putText(frame, f"VIOLATION! ID:{vid}", (px - 60, py - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame

    def get_violations(self):
        return self.violations

    def simulate_signal(self, interval=10):
        current = int(time.time())
        if (current // interval) % 2 == 0:
            self.signal_state = "red"
        else:
            self.signal_state = "green"


__all__ = ["RedLightDetector"]
