import os

import cv2
from ultralytics import YOLO


class HelmetDetector:
    NEGATIVE_WORDS = ("no", "without", "nohelmet", "no_helmet", "no-helmet")

    def __init__(self, model_path="models/helmet.pt", confidence=0.5, min_hits=3):
        self.confidence = confidence
        self.min_hits = min_hits
        self.violation_ids = set()
        self.no_helmet_hits = {}
        self.model = None

        if os.path.exists(model_path):
            print("[INFO] Loading helmet model...")
            self.model = YOLO(model_path)
            print(f"[INFO] Helmet model loaded. Classes: {self.model.names}")
        else:
            print(
                f"[WARNING] {model_path} not found - helmet detection is DISABLED. "
                "Run: python scripts/train_helmet.py"
            )

    @staticmethod
    def _is_negative(label):
        label = label.lower().replace("-", "_").replace(" ", "_")
        return (
            label.startswith("no")
            or "without" in label
            or "_no_" in label
        )

    def detect(self, frame, vehicle_box, vehicle_id):
        if self.model is None:
            return None, None

        h, w = frame.shape[:2]
        x1, y1, x2, y2 = [int(v) for v in vehicle_box]

        # Rider's head is above the motorcycle box, so extend the crop upwards.
        box_h = y2 - y1
        top = max(0, y1 - int(0.8 * box_h))
        bottom = max(0, min(h, y1 + int(0.4 * box_h)))
        left = max(0, x1)
        right = min(w, x2)

        head_crop = frame[top:bottom, left:right]

        if head_crop.size == 0:
            return None, None

        results = self.model(head_crop, conf=self.confidence, verbose=False)

        helmet_worn = None
        best_conf = 0.0

        for result in results:
            for det in result.boxes:
                conf = float(det.conf[0])
                if conf < best_conf:
                    continue

                label = result.names[int(det.cls[0])]

                if self._is_negative(label):
                    helmet_worn, best_conf = False, conf
                elif "helmet" in label.lower():
                    helmet_worn, best_conf = True, conf

        return helmet_worn, head_crop

    def check_violation(self, vehicle_id, helmet_worn):
        if helmet_worn is False:
            hits = self.no_helmet_hits.get(vehicle_id, 0) + 1
            self.no_helmet_hits[vehicle_id] = hits

            if hits >= self.min_hits and vehicle_id not in self.violation_ids:
                self.violation_ids.add(vehicle_id)
                return True

        elif helmet_worn is True:
            self.no_helmet_hits[vehicle_id] = 0

        return False

    def annotate(self, frame, vehicle_box, helmet_worn, vehicle_id):
        x1, y1, x2, y2 = [int(v) for v in vehicle_box]

        if helmet_worn is True:
            color = (0, 255, 0)
            label = f"ID:{vehicle_id} Helmet OK"
        elif helmet_worn is False:
            color = (0, 0, 255)
            label = f"ID:{vehicle_id} NO HELMET!"
        else:
            return frame

        cv2.putText(
            frame, label, (x1, max(y1 - 50, 15)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
        )
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        return frame