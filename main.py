import cv2
import sys
from src.detection.detector import VehicleDetector
from src.detection.helmet_detector import HelmetDetector
from src.tracking.tracker import VehicleTracker
from src.violation.red_light import RedLightDetector
from src.violation.speed_estimator import SpeedEstimator
from src.utils.recorder import ViolationRecorder
from src.utils.dashboard import Dashboard
from src.utils.config import Config

def main():
    config = Config()
    video_source = config.get("video", "source")

    print("[INFO] Starting Traffic Violation Detection System...")
    print(f"[INFO] Loading video from {video_source}")

    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print("[ERROR] Cannot open video source")
        sys.exit(1)

    detector = VehicleDetector(
        model_path=config.get("detection", "model"),
        confidence=config.get("detection", "confidence")
    )
    helmet_detector = HelmetDetector()
    tracker = VehicleTracker(config.get("tracking", "max_disappeared"))
    red_light = RedLightDetector(stop_line_y=config.get("violation", "stop_line_y"))
    speed_estimator = SpeedEstimator(
        fps=config.get("video", "fps"),
        speed_limit=config.get("violation", "speed_limit")
    )
    recorder = ViolationRecorder(output_dir="output")
    dashboard = Dashboard()

    # Only check helmets on bikes and motorcycles
    two_wheeler_classes = [3]  # motorcycle class in YOLO

    while True:
        ret, frame = cap.read()

        if not ret:
            print("[INFO] Video stream ended")
            break

        red_light.simulate_signal(interval=config.get("violation", "signal_interval"))

        results = detector.detect(frame)
        tracked_objects, trajectories = tracker.update(results)
        annotated_frame = detector.annotate(frame, results)
        annotated_frame = red_light.draw_stop_line(annotated_frame)

        for vehicle_id, box in tracked_objects.items():
            x1, y1, x2, y2 = box

            # Draw ID
            cv2.putText(annotated_frame, f"ID:{vehicle_id}", (x1, y1 - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            # Draw trajectory
            points = trajectories[vehicle_id]
            for i in range(1, len(points)):
                cv2.line(annotated_frame, points[i-1], points[i], (255, 255, 0), 2)

            # Helmet check for two wheelers
            for result in results:
                for det_box in result.boxes:
                    cls = int(det_box.cls[0])
                    if cls in two_wheeler_classes:
                        helmet_worn, _ = helmet_detector.detect(
                            annotated_frame, box, vehicle_id
                        )
                        annotated_frame = helmet_detector.annotate(
                            annotated_frame, box, helmet_worn, vehicle_id
                        )
                        if helmet_detector.check_violation(vehicle_id, helmet_worn):
                            print(f"[VIOLATION] Vehicle ID:{vehicle_id} — NO HELMET!")
                            recorder.save(
                                annotated_frame,
                                vehicle_id,
                                "no_helmet"
                            )
                            dashboard.add_violation(vehicle_id, "No Helmet")

            # Speed check
            speed = speed_estimator.update(vehicle_id, box)
            if speed is not None:
                speed_color = (0, 0, 255) if speed_estimator.is_speeding(speed) else (0, 255, 0)
                cv2.putText(annotated_frame, f"{speed} km/h", (x1, y2 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, speed_color, 2)
                if speed_estimator.is_speeding(speed):
                    print(f"[SPEEDING] Vehicle ID:{vehicle_id} going {speed} km/h!")
                    recorder.save(annotated_frame, vehicle_id, "speeding", speed=speed)
                    dashboard.add_violation(vehicle_id, f"Speeding {speed}km/h")

            # Red light check
            violation = red_light.check_violation(vehicle_id, box)
            if violation:
                print(f"[VIOLATION] Vehicle ID:{vehicle_id} ran a red light!")
                recorder.save(annotated_frame, vehicle_id, "red_light")
                dashboard.add_violation(vehicle_id, "Red Light")

        annotated_frame = red_light.draw_violations(annotated_frame)
        annotated_frame = dashboard.draw(
            annotated_frame,
            vehicle_count=len(tracked_objects),
            violation_count=len(red_light.get_violations()),
            signal_state=red_light.signal_state
        )

        cv2.imshow("Traffic Violation Detection", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Quit signal received")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()