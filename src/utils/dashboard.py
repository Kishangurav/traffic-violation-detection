import cv2
import time

class Dashboard:
    def __init__(self):
        self.start_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.violation_log = []

    def update_fps(self):
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()

    def add_violation(self, vehicle_id, violation_type):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] ID:{vehicle_id} - {violation_type}"
        self.violation_log.append(log_entry)
        if len(self.violation_log) > 5:
            self.violation_log.pop(0)

    def draw(self, frame, vehicle_count, violation_count, signal_state):
        self.update_fps()
        h, w = frame.shape[:2]

        # Background panel top left
        cv2.rectangle(frame, (0, 0), (280, 160), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, 0), (280, 160), (255, 255, 255), 1)

        # FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Vehicle count
        cv2.putText(frame, f"Vehicles: {vehicle_count}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Violation count
        cv2.putText(frame, f"Violations: {violation_count}", (10, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Signal state
        signal_color = (0, 0, 255) if signal_state == "red" else (0, 255, 0)
        cv2.putText(frame, f"Signal: {signal_state.upper()}", (10, 115),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, signal_color, 2)

        # Signal circle indicator
        cv2.circle(frame, (250, 108), 15, signal_color, -1)

        # Violation log bottom left
        log_y = h - 20
        for entry in reversed(self.violation_log):
            cv2.rectangle(frame, (0, log_y - 18), (400, log_y + 4), (0, 0, 0), -1)
            cv2.putText(frame, entry, (5, log_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            log_y -= 22

        # Title bar top right
        cv2.rectangle(frame, (w - 320, 0), (w, 30), (0, 0, 0), -1)
        cv2.putText(frame, "Traffic Violation Detection System", (w - 318, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return frame