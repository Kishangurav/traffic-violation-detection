import cv2
import json
import os
import time
from datetime import datetime


class ViolationRecorder:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.screenshots_dir = os.path.join(output_dir, "screenshots")
        self.reports_dir = os.path.join(output_dir, "reports")

        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

        # Prevent duplicate reports for the same vehicle and violation.
        self.recorded_ids = set()

        print("[INFO] Violation Recorder Ready")

    @staticmethod
    def _to_python_number(value):
        """Convert NumPy numeric values to JSON-compatible Python values."""
        if value is None:
            return None

        if hasattr(value, "item"):
            value = value.item()

        return value

    def save(
        self,
        frame,
        vehicle_id,
        violation_type,
        plate_text=None,
        speed=None
    ):
        record_key = (int(vehicle_id), str(violation_type))

        if record_key in self.recorded_ids:
            return None

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = (
            f"violation_{violation_type}_"
            f"ID{vehicle_id}_{timestamp}"
        )

        screenshot_path = os.path.join(
            self.screenshots_dir,
            f"{filename}.jpg"
        )

        report_path = os.path.join(
            self.reports_dir,
            f"{filename}.json"
        )

        safe_vehicle_id = int(vehicle_id)
        safe_speed = self._to_python_number(speed)

        report = {
            "vehicle_id": safe_vehicle_id,
            "violation_type": str(violation_type),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "plate_number": str(plate_text) if plate_text else "Unknown",
            "speed": safe_speed if safe_speed is not None else "Unknown",
            "screenshot": screenshot_path
        }

        screenshot_saved = cv2.imwrite(screenshot_path, frame)

        if not screenshot_saved:
            print(f"[WARNING] Could not save screenshot: {screenshot_path}")

        try:
            with open(report_path, "w", encoding="utf-8") as file:
                json.dump(report, file, indent=4, allow_nan=False)

        except (TypeError, ValueError, OSError) as error:
            print(f"[ERROR] Could not save violation report: {error}")
            return None

        self.recorded_ids.add(record_key)

        print(f"[SAVED] Violation recorded — {report_path}")

        return screenshot_path