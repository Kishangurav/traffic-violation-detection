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

        self.recorded_ids = set()
        print("[INFO] Violation Recorder Ready")

    def save(self, frame, vehicle_id, violation_type, plate_text=None, speed=None):
        if vehicle_id in self.recorded_ids:
            return
        self.recorded_ids.add(vehicle_id)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"violation_{violation_type}_ID{vehicle_id}_{timestamp}"

        # Save screenshot
        screenshot_path = os.path.join(self.screenshots_dir, f"{filename}.jpg")
        cv2.imwrite(screenshot_path, frame)

        # Save JSON report
        report = {
            "vehicle_id": vehicle_id,
            "violation_type": violation_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "plate_number": plate_text if plate_text else "Unknown",
            "speed": speed if speed else "Unknown",
            "screenshot": screenshot_path
        }

        report_path = os.path.join(self.reports_dir, f"{filename}.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=4)

        print(f"[SAVED] Violation recorded — {report_path}")