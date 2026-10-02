import cv2
import json
import os
import time


class ViolationRecorder:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.screenshots_dir = os.path.join(output_dir, "screenshots")
        self.reports_dir = os.path.join(output_dir, "reports")

        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

        # Prevent duplicate records for the same vehicle + violation type,
        # while still allowing different violation types for one vehicle.
        self.recorded_events = set()
        print("[INFO] Violation Recorder Ready")

    def save(
        self,
        frame,
        vehicle_id,
        violation_type,
        plate_text=None,
        speed=None,
        verification="unverified",
        confidence=None,
    ):
        event_key = (vehicle_id, violation_type)
        if event_key in self.recorded_events:
            return None
        self.recorded_events.add(event_key)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"violation_{violation_type}_ID{vehicle_id}_{timestamp}"

        screenshot_path = os.path.join(self.screenshots_dir, f"{filename}.jpg")
        cv2.imwrite(screenshot_path, frame)

        report = {
            "vehicle_id": vehicle_id,
            "violation_type": violation_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "plate_number": plate_text if plate_text else "Unknown",
            "speed": speed if speed is not None else "Unknown",
            "verification": verification,
            "confidence": confidence,
            "screenshot": screenshot_path,
        }

        report_path = os.path.join(self.reports_dir, f"{filename}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)

        print(f"[SAVED] Violation recorded — {report_path}")
        return report_path
