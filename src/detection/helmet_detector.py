import cv2
from ultralytics import YOLO
import os

class HelmetDetector:
    def __init__(self, model_path="models/helmet.pt", confidence=0.5):
        self.confidence = confidence
        self.violation_ids = set()

        if os.path.exists(model_path):
            print("[INFO] Loading helmet model...")
            self.model = YOLO(model_path)
            print("[INFO] Helmet model loaded")
        else:
            print("[WARNING] Helmet model not found, downloading...")
            self._download_model()

    def _download_model(self):
        try:
            from roboflow import Roboflow
            rf = Roboflow(api_key= oHE8xsuTGviNm9lWvaXA)
            project = rf.workspace("joseph-nelson").project("helmet-detection-jmmyd")
            dataset = project.version(2).download("yolov8")
            self.model = YOLO("yolov8n.pt")
            print("[INFO] Using base model - train on helmet dataset for better results")
        except Exception as e:
            print(f"[WARNING] Could not download model: {e}")
            print("[INFO] Falling back to base YOLOv8 model")
            self.model = YOLO("yolov8n.pt")

    def detect(self, frame, vehicle_box, vehicle_id):
        x1, y1, x2, y2 = vehicle_box

        # Focus on top half of vehicle — where rider's head is
        head_region_y2 = y1 + (y2 - y1) // 2
        head_crop = frame[y1:head_region_y2, x1:x2]

        if head_crop.size == 0:
            return None, None

        results = self.model(head_crop, conf=self.confidence, verbose=False)

        helmet_worn = None
        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                label = result.names[cls].lower()

                if "helmet" in label or "with_helmet" in label:
                    helmet_worn = True
                elif "no_helmet" in label or "without_helmet" in label:
                    helmet_worn = False

        return helmet_worn, head_crop

    def check_violation(self, vehicle_id, helmet_worn):
        if helmet_worn is False:
            if vehicle_id not in self.violation_ids:
                self.violation_ids.add(vehicle_id)
                return True
        return False

    def annotate(self, frame, vehicle_box, helmet_worn, vehicle_id):
        x1, y1, x2, y2 = vehicle_box

        if helmet_worn is True:
            color = (0, 255, 0)
            label = f"ID:{vehicle_id} Helmet OK"
        elif helmet_worn is False:
            color = (0, 0, 255)
            label = f"ID:{vehicle_id} NO HELMET!"
        else:
            return frame

        cv2.putText(frame, label, (x1, y1 - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        return frame