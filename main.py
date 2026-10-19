import cv2
import sys

from src.detection.detector import VehicleDetector
from src.detection.helmet_detector import HelmetDetector
from src.tracking.tracker import VehicleTracker
from src.ptz.biomimetic_controller import BiomimeticOculomotorController
from src.violation.red_light import RedLightDetector
from src.violation.speed_estimator import SpeedEstimator
from src.utils.recorder import ViolationRecorder
from src.utils.dashboard import Dashboard
from src.utils.config import Config
from src.utils.violation_logger import ViolationLogger


def main():
    config = Config()
    video_source = config.get("video", "source")

    print("[INFO] Starting Traffic Violation Detection System...")
    print(f"[INFO] Loading video from {video_source}")

    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print("[ERROR] Cannot open video source")
        sys.exit(1)

    window_name = "Traffic Violation Detection"

    try:
        detector = VehicleDetector(
            model_path=config.get("detection", "model"),
            confidence=config.get("detection", "confidence")
        )

        helmet_detector = HelmetDetector()

        tracker = VehicleTracker(
            config.get("tracking", "max_disappeared")
        )

        red_light = RedLightDetector(
            stop_line_y=config.get("violation", "stop_line_y")
        )

        speed_estimator = SpeedEstimator(
            fps=cap.get(cv2.CAP_PROP_FPS) or config.get("video", "fps"),
            speed_limit=config.get("violation", "speed_limit")
        )

        recorder = ViolationRecorder(output_dir="output")
        dashboard = Dashboard()
        logger = ViolationLogger(recorder, dashboard)
        frame_idx = 0

        ptz_controller = BiomimeticOculomotorController(
            kp_pan=0.05,
            kp_tilt=0.05,
            dead_zone=20
        )

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1280, 720)

        selected_target_id = None
        two_wheeler_classes = [3]

        while True:
            ret, frame = cap.read()

            if not ret:
                print("[INFO] Video stream ended")
                break

            frame_idx += 1

            # Reset controller values for this frame.
            pan_error = 0.0
            tilt_error = 0.0
            pan_command = 0.0
            tilt_command = 0.0

            red_light.simulate_signal(
                interval=config.get("violation", "signal_interval")
            )

            # Detection and tracking.
            results = detector.detect(frame)
            tracked_objects, trajectories = tracker.update(results)

            annotated_frame = detector.annotate(frame, results)
            annotated_frame = red_light.draw_stop_line(annotated_frame)

            # Select and follow one tracked vehicle.
            if tracked_objects:
                if selected_target_id not in tracked_objects:
                    selected_target_id = next(iter(tracked_objects))

                target_box = tracked_objects[selected_target_id]
                tx1, ty1, tx2, ty2 = map(int, target_box)

                target_center = (
                    (tx1 + tx2) / 2,
                    (ty1 + ty2) / 2
                )

                frame_height, frame_width = frame.shape[:2]

                pan_error, tilt_error = ptz_controller.calculate_error(
                    target_center,
                    (frame_width, frame_height)
                )

                pan_command, tilt_command = ptz_controller.generate_commands(
                    pan_error,
                    tilt_error
                )
            else:
                selected_target_id = None

            # Process tracked vehicles.
            for vehicle_id, box in tracked_objects.items():
                x1, y1, x2, y2 = map(int, box)

                # Highlight the selected PTZ target.
                if vehicle_id == selected_target_id:
                    cv2.rectangle(
                        annotated_frame,
                        (x1, y1),
                        (x2, y2),
                        (255, 0, 255),
                        3
                    )

                # Vehicle ID label.
                cv2.putText(
                    annotated_frame,
                    f"ID:{vehicle_id}",
                    (x1, max(y1 - 30, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    2
                )

                # Vehicle trajectory.
                points = trajectories.get(vehicle_id, [])

                for i in range(1, len(points)):
                    cv2.line(
                        annotated_frame,
                        points[i - 1],
                        points[i],
                        (255, 255, 0),
                        2
                    )

                # Helmet check for motorcycles.
                for result in results:
                    matched_motorcycle = False

                    for det_box in result.boxes:
                        cls = int(det_box.cls[0])

                        if cls not in two_wheeler_classes:
                            continue

                        dx1, dy1, dx2, dy2 = map(
                            int, det_box.xyxy[0]
                        )

                        # Approximate match between detection and track.
                        if (
                            abs(dx1 - x1) > 50
                            or abs(dy1 - y1) > 50
                            or abs(dx2 - x2) > 50
                            or abs(dy2 - y2) > 50
                        ):
                            continue

                        matched_motorcycle = True

                        # Use the clean frame for the model.
                        helmet_worn, _ = helmet_detector.detect(
                            frame,
                            box,
                            vehicle_id
                        )

                        annotated_frame = helmet_detector.annotate(
                            annotated_frame,
                            box,
                            helmet_worn,
                            vehicle_id
                        )

                        if helmet_detector.check_violation(
                            vehicle_id,
                            helmet_worn
                        ):
                            logger.log(
                                vehicle_id,
                                "no_helmet",
                                annotated_frame,
                                "No Helmet",
                                frame_idx
                            )

                        break

                    if matched_motorcycle:
                        break

                # Speed checking.
                speed = speed_estimator.update(vehicle_id, box)

                if speed is not None:
                    speeding = speed_estimator.is_speeding(speed)

                    speed_color = (
                        (0, 0, 255) if speeding else (0, 255, 0)
                    )

                    cv2.putText(
                        annotated_frame,
                        f"{speed:.1f} km/h",
                        (x1, min(y2 + 20, frame.shape[0] - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        speed_color,
                        2
                    )

                    if speeding:
                        logger.log(
                            vehicle_id,
                            "speeding",
                            annotated_frame,
                            f"Speeding {speed:.1f} km/h",
                            frame_idx,
                            speed=speed
                        )

                # Red-light crossing verification.
                violation = red_light.check_violation(
                    vehicle_id,
                    box
                )

                if violation:
                    logger.log(
                        vehicle_id,
                        "red_light",
                        annotated_frame,
                        "Red Light",
                        frame_idx
                    )

            annotated_frame = red_light.draw_violations(
                annotated_frame
            )

            # Dashboard is drawn before the PTZ panel.
            annotated_frame = dashboard.draw(
                annotated_frame,
                vehicle_count=len(tracked_objects),
                violation_count=logger.count,
                signal_state=red_light.signal_state
            )

            # Compact PTZ status panel in the top-right.
            if selected_target_id is not None:
                frame_height, frame_width = annotated_frame.shape[:2]

                panel_width = min(330, frame_width - 20)
                panel_height = 100
                panel_x = frame_width - panel_width - 10
                panel_y = 40

                cv2.rectangle(
                    annotated_frame,
                    (panel_x, panel_y),
                    (panel_x + panel_width, panel_y + panel_height),
                    (0, 0, 0),
                    -1
                )

                cv2.putText(
                    annotated_frame,
                    f"PTZ Target: {selected_target_id}",
                    (panel_x + 10, panel_y + 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 0),
                    2
                )

                cv2.putText(
                    annotated_frame,
                    f"Error: ({pan_error:.1f}, {tilt_error:.1f})",
                    (panel_x + 10, panel_y + 55),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    (0, 255, 255),
                    1
                )

                cv2.putText(
                    annotated_frame,
                    f"Pan: {pan_command:.2f}  Tilt: {tilt_command:.2f}",
                    (panel_x + 10, panel_y + 82),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    (0, 255, 255),
                    1
                )

            cv2.imshow(window_name, annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("[INFO] Quit signal received")
                break

    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Resources released")


if __name__ == "__main__":
    main()