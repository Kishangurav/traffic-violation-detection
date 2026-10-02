from collections import defaultdict, deque
from typing import Dict, Optional, Tuple


class TemporalVerifier:
    """Confirms events using multiple consecutive frames instead of one detection."""

    def __init__(self, min_frames: int = 3, cooldown_frames: int = 30):
        self.min_frames = min_frames
        self.cooldown_frames = cooldown_frames
        self.frame_index = 0
        self.candidates = defaultdict(int)
        self.last_confirmed = {}

    def update(self):
        self.frame_index += 1

    def confirm(self, vehicle_id: int, condition: bool) -> bool:
        if not condition:
            self.candidates[vehicle_id] = 0
            return False

        self.candidates[vehicle_id] += 1
        last = self.last_confirmed.get(vehicle_id, -10**9)

        if (
            self.candidates[vehicle_id] >= self.min_frames
            and self.frame_index - last >= self.cooldown_frames
        ):
            self.last_confirmed[vehicle_id] = self.frame_index
            self.candidates[vehicle_id] = 0
            return True

        return False

    def reset(self, vehicle_id: int):
        self.candidates.pop(vehicle_id, None)
        self.last_confirmed.pop(vehicle_id, None)


__all__ = ["TemporalVerifier"]
