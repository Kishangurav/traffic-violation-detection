
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
        entry = f"[{timestamp}] ID:{vehicle_id} - {violation_type}"
        self.violation_log.append(entry)
        self.violation_log = self.violation_log[-4:]

    @staticmethod
    def draw_panel(frame, x1, y1, x2, y2, alpha=0.45):
        h, w = frame.shape[:2]
        x1, x2 = max(0, x1), min(w, x2)
        y1, y2 = max(0, y1), min(h, y2)

        if x2 <= x1 or y2 <= y1:
            return

        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    def draw(self, frame, vehicle_count, violation_count, signal_state):
        self.update_fps()
        h, w = frame.shape[:2]

        # Compact statistics panel
        panel_w = min(255, w - 20)
        panel_h = 112
        self.draw_panel(frame, 8, 8, 8 + panel_w, 8 + panel_h)

        signal_color = (
            (0, 0, 255)
            if str(signal_state).lower() == "red"
            else (0, 255, 0)
        )

        scale = 0.52
        thickness = 2

        cv2.putText(frame, f"FPS: {self.fps:.1f}", (18, 32),
                    cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 255, 255), thickness)
        cv2.putText(frame, f"Vehicles: {vehicle_count}", (18, 57),
                    cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 255, 0), thickness)
        cv2.putText(frame, f"Violations: {violation_count}", (18, 82),
                    cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 255), thickness)
        cv2.putText(frame, f"Signal: {str(signal_state).upper()}", (18, 106),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, signal_color, thickness)

        # Small signal indicator
        cv2.circle(frame, (panel_w - 8, 98), 7, signal_color, -1)

        # Compact title, only if enough room
        title = "Traffic Violation Detection"
        title_w = min(300, w - 16)
        title_x = max(8, w - title_w - 8)

        self.draw_panel(frame, title_x, 8, w - 8, 36, alpha=0.4)

        cv2.putText(
            frame, title, (title_x + 6, 29),
            cv2.FONT_HERSHEY_SIMPLEX, 0.48,
            (0, 0, 0), 1
            )

        # Small recent-violation list at bottom
        if self.violation_log:
            font_scale = 0.42
            line_gap = 21
            max_text_width = max(100, min(460, w - 20))
            visible_entries = []

            for entry in reversed(self.violation_log):
                text = entry
                while text and cv2.getTextSize(
                    text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1
                )[0][0] > max_text_width - 12:
                    text = text[:-1]

                if text != entry and len(text) > 3:
                    text = text[:-3] + "..."

                visible_entries.append(text)

            box_h = len(visible_entries) * line_gap + 10
            box_y = max(8, h - box_h - 8)
            self.draw_panel(
                frame, 8, box_y, min(w - 8, max_text_width + 8),
                h - 8, alpha=0.45
            )

            for i, entry in enumerate(visible_entries):
                y = box_y + 22 + i * line_gap
                if y < h - 5:
                    cv2.putText(frame, entry, (14, y),
                                cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                                (0, 0, 255), 1)

        return frame
