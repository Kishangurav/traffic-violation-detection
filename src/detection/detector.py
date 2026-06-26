from ultralytics import YOLO
import cv2

class VehicleDetector:
    def __init__(self, model_path="yolov8n.pt", confidence=0.4):
        print("[INFO] Loading YOLOv8 Model...")
        self.model = YOLO("yolov8n.pt")
        self.confidence = confidence
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        print("[INFO] Model Loaded Successfully")

    def detect(self, frame):
        results = self.model(frame, conf=self.confidence, verbose=False)
        return results

    def annotate(self, frame, results):
        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                if cls not in self.vehicle_classes:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                label = f"{result.names[cls]} {conf:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        return frame