from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ViolationRecord(BaseModel):
    id: Optional[int] = None
    vehicle_id: int
    violation_type: str
    plate_number: Optional[str] = "Unknown"
    speed: Optional[float] = None
    timestamp: str
    screenshot_path: Optional[str] = None
    confidence: Optional[float] = None

class CameraConfig(BaseModel):
    camera_id: int
    name: str
    location: str
    video_source: str
    stop_line_y: int
    speed_limit: int
    status: str = "active"

class DashboardStats(BaseModel):
    total_vehicles: int
    total_violations: int
    red_light_violations: int
    speeding_violations: int
    helmet_violations: int
    signal_state: str
    fps: float