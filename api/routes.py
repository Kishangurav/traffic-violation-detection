import os
from datetime import timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func

from api.models import CameraConfig, DashboardStats, ViolationRecord
from src.utils.database import Violation, ViolationDB

router = APIRouter()

# Same SQLite file the detector writes to (run the API from the repo root).
db = ViolationDB()

# Cameras are still in memory (moved to the database in a later step).
cameras_db = [
    {
        "camera_id": 1,
        "name": "Silk Board Junction",
        "location": "Silk Board, Bangalore",
        "video_source": "data/raw/traffic.mp4",
        "stop_line_y": 300,
        "speed_limit": 50,
        "status": "active",
    },
    {
        "camera_id": 2,
        "name": "Hebbal Flyover",
        "location": "Hebbal, Bangalore",
        "video_source": "data/raw/traffic.mp4",
        "stop_line_y": 320,
        "speed_limit": 60,
        "status": "active",
    },
]


def _to_dict(row: Violation) -> dict:
    ts = row.timestamp
    if ts is not None:
        ts = ts.replace(tzinfo=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")

    path = (row.image_path or "").replace("\\", "/")
    filename = os.path.basename(path)

    return {
        "id": row.id,
        "vehicle_id": row.vehicle_id,
        "violation_type": row.violation_type,
        "plate_number": row.plate or "Unknown",
        "speed": row.speed,
        "timestamp": ts or "",
        "camera_id": row.camera_id,
        "frame_number": row.frame_number,
        "screenshot_path": path or None,
        "screenshot_url": f"/screenshots/{filename}" if filename else None,
    }


# ----- Violations -----

@router.get("/violations", response_model=List[ViolationRecord])
def get_all_violations(
    violation_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    with db.Session() as session:
        query = session.query(Violation)
        if violation_type:
            query = query.filter(Violation.violation_type == violation_type)
        rows = (
            query.order_by(Violation.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [_to_dict(r) for r in rows]


@router.get("/violations/type/{violation_type}", response_model=List[ViolationRecord])
def get_violations_by_type(violation_type: str):
    with db.Session() as session:
        rows = (
            session.query(Violation)
            .filter(Violation.violation_type == violation_type)
            .order_by(Violation.id.desc())
            .all()
        )
        return [_to_dict(r) for r in rows]


@router.get("/violations/id/{violation_id}", response_model=ViolationRecord)
def get_violation_by_row_id(violation_id: int):
    with db.Session() as session:
        row = session.get(Violation, violation_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Violation not found")
        return _to_dict(row)


@router.get("/violations/{vehicle_id}", response_model=ViolationRecord)
def get_violation_by_vehicle(vehicle_id: int):
    """Latest violation for a tracked vehicle ID."""
    with db.Session() as session:
        row = (
            session.query(Violation)
            .filter(Violation.vehicle_id == vehicle_id)
            .order_by(Violation.id.desc())
            .first()
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Violation not found")
        return _to_dict(row)


@router.delete("/violations/{vehicle_id}")
def delete_violation(vehicle_id: int):
    """Deletes the database records for this vehicle (screenshots stay on disk)."""
    with db.Session() as session:
        deleted = (
            session.query(Violation)
            .filter(Violation.vehicle_id == vehicle_id)
            .delete()
        )
        session.commit()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Violation not found")
    return {"message": f"{deleted} violation(s) for vehicle {vehicle_id} deleted"}


# ----- Cameras -----

@router.get("/cameras")
def get_all_cameras():
    return cameras_db


@router.get("/cameras/{camera_id}")
def get_camera(camera_id: int):
    for cam in cameras_db:
        if cam["camera_id"] == camera_id:
            return cam
    raise HTTPException(status_code=404, detail="Camera not found")


@router.post("/cameras")
def add_camera(camera: CameraConfig):
    cameras_db.append(camera.model_dump())
    return {"message": "Camera added", "camera": camera}


@router.delete("/cameras/{camera_id}")
def delete_camera(camera_id: int):
    for i, cam in enumerate(cameras_db):
        if cam["camera_id"] == camera_id:
            cameras_db.pop(i)
            return {"message": f"Camera {camera_id} deleted"}
    raise HTTPException(status_code=404, detail="Camera not found")


# ----- Stats -----

@router.get("/stats", response_model=DashboardStats)
def get_stats():
    with db.Session() as session:
        rows = (
            session.query(Violation.violation_type, func.count(Violation.id))
            .group_by(Violation.violation_type)
            .all()
        )

    by_type = {vtype: count for vtype, count in rows}

    return {
        "total_violations": sum(by_type.values()),
        "red_light_violations": by_type.get("red_light", 0),
        "speeding_violations": by_type.get("speeding", 0),
        "helmet_violations": by_type.get("no_helmet", 0),
        "by_type": by_type,
    }


# ----- Health check -----

@router.get("/health")
def health_check():
    return {"status": "ok", "message": "Traffic Violation API is running"}