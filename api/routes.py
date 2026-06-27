from fastapi import APIRouter, HTTPException
from api.models import ViolationRecord, CameraConfig, DashboardStats
from typing import List
import json
import os
import glob

router = APIRouter()

# In-memory store (replace with PostgreSQL later)
violations_db = []
cameras_db = [
    {
        "camera_id": 1,
        "name": "Silk Board Junction",
        "location": "Silk Board, Bangalore",
        "video_source": "data/raw/traffic.mp4",
        "stop_line_y": 300,
        "speed_limit": 50,
        "status": "active"
    },
    {
        "camera_id": 2,
        "name": "Hebbal Flyover",
        "location": "Hebbal, Bangalore",
        "video_source": "data/raw/traffic.mp4",
        "stop_line_y": 320,
        "speed_limit": 60,
        "status": "active"
    }
]

# ─── Violations ───────────────────────────────────────────

@router.get("/violations", response_model=List[ViolationRecord])
def get_all_violations():
    # Load from saved JSON reports
    reports = []
    report_files = glob.glob("output/reports/*.json")
    for f in report_files:
        with open(f, "r") as file:
            data = json.load(file)
            reports.append(data)
    return reports

@router.get("/violations/{vehicle_id}")
def get_violation_by_id(vehicle_id: int):
    report_files = glob.glob("output/reports/*.json")
    for f in report_files:
        with open(f, "r") as file:
            data = json.load(file)
            if data.get("vehicle_id") == vehicle_id:
                return data
    raise HTTPException(status_code=404, detail="Violation not found")

@router.get("/violations/type/{violation_type}")
def get_violations_by_type(violation_type: str):
    reports = []
    report_files = glob.glob("output/reports/*.json")
    for f in report_files:
        with open(f, "r") as file:
            data = json.load(file)
            if data.get("violation_type") == violation_type:
                reports.append(data)
    return reports

@router.delete("/violations/{vehicle_id}")
def delete_violation(vehicle_id: int):
    report_files = glob.glob("output/reports/*.json")
    for f in report_files:
        with open(f, "r") as file:
            data = json.load(file)
            if data.get("vehicle_id") == vehicle_id:
                os.remove(f)
                return {"message": f"Violation for vehicle {vehicle_id} deleted"}
    raise HTTPException(status_code=404, detail="Violation not found")

# ─── Cameras ───────────────────────────────────────────────

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
    cameras_db.append(camera.dict())
    return {"message": "Camera added", "camera": camera}

@router.delete("/cameras/{camera_id}")
def delete_camera(camera_id: int):
    for i, cam in enumerate(cameras_db):
        if cam["camera_id"] == camera_id:
            cameras_db.pop(i)
            return {"message": f"Camera {camera_id} deleted"}
    raise HTTPException(status_code=404, detail="Camera not found")

# ─── Stats ─────────────────────────────────────────────────

@router.get("/stats")
def get_stats():
    report_files = glob.glob("output/reports/*.json")
    total = len(report_files)
    red_light = 0
    speeding = 0
    helmet = 0

    for f in report_files:
        with open(f, "r") as file:
            data = json.load(file)
            vtype = data.get("violation_type", "")
            if vtype == "red_light":
                red_light += 1
            elif vtype == "speeding":
                speeding += 1
            elif vtype == "no_helmet":
                helmet += 1

    return {
        "total_violations": total,
        "red_light_violations": red_light,
        "speeding_violations": speeding,
        "helmet_violations": helmet
    }

# ─── Health check ──────────────────────────────────────────

@router.get("/health")
def health_check():
    return {"status": "ok", "message": "Traffic Violation API is running"}
