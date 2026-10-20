from pydantic import BaseModel
from typing import Optional


class ViolationRecord(BaseModel):
    id: Optional[int] = None
    vehicle_id: int
    violation_type: str
    plate_number: Optional[str] = "Unknown"
    speed: Optional[float] = None
    timestamp: str
    camera_id: Optional[str] = None
    frame_number: Optional[int] = None
    screenshot_path: Optional[str] = None
    screenshot_url: Optional[str] = None


class CameraConfig(BaseModel):
    camera_id: int
    name: str
    location: str
    video_source: str
    stop_line_y: int
    speed_limit: int
    status: str = "active"


class DashboardStats(BaseModel):
    total_violations: int
    red_light_violations: int
    speeding_violations: int
    helmet_violations: int
    by_type: dict