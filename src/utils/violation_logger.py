from src.utils.database import ViolationDB


class ViolationLogger:
    """One place that saves evidence, writes to the DB and updates the dashboard.
    Each (vehicle, violation type) pair is logged only once."""

    def __init__(self, recorder, dashboard, db=None, camera_id="cam1"):
        self.recorder = recorder
        self.dashboard = dashboard
        self.db = db or ViolationDB()
        self.camera_id = camera_id
        self._seen = set()
        self.count = 0

    def log(self, vehicle_id, vtype, frame, label, frame_number=None, speed=None):
        key = (vehicle_id, vtype)
        if key in self._seen:
            return False
        self._seen.add(key)

        if speed is not None:
            saved = self.recorder.save(frame, vehicle_id, vtype, speed=speed)
        else:
            saved = self.recorder.save(frame, vehicle_id, vtype)

        self.db.add(
            camera_id=self.camera_id,
            vehicle_id=int(vehicle_id),
            violation_type=vtype,
            speed=float(speed) if speed is not None else None,
            frame_number=frame_number,
            image_path=saved if isinstance(saved, str) else None,
        )

        self.dashboard.add_violation(vehicle_id, label)
        self.count += 1
        print(f"[VIOLATION] Vehicle ID:{vehicle_id} - {label}")
        return True