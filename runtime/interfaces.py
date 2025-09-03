# runtime/interfaces.py
from __future__ import annotations

from typing import Any, Protocol, Literal, TypedDict, Optional, List, Dict, Tuple


# ---------- Shared lightweight types ----------

class Waypoint(TypedDict):
    lat: float
    lng: float

class ReportUpdate(TypedDict, total=False):
    status: Literal["running", "finished"]
    patrol_areas: List[str]
    altitude: Optional[float]

Telemetry = Dict[str, Any]           # result of Data.get_telemetry()
ComputeResults = List[Any]           # generic_result list from Data.get_compute_result()


# ---------- Control-plane (vehicle/control) ----------

class Ctrl(Protocol):
    """Abstract control-plane interface (vehicle commands, compute config)."""

    # Vehicle actions
    async def take_off(self) -> bool: ...
    async def land(self) -> bool: ...
    async def rth(self) -> bool: ...
    async def hover(self) -> bool: ...

    # Navigation / positioning
    async def set_gps_location(
        self,
        latitude: float,
        longitude: float,
        altitude: float,
        *,
        bearing: float = 0,
        altitude_mode: Literal["ABSOLUTE", "RELATIVE"] = "RELATIVE",
        heading_mode: Literal["TO_TARGET", "HEADING_START"] = "TO_TARGET",
        velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> bool: ...
    async def set_relative_position_enu(
        self, north: float, east: float, up: float, angle: float
    ) -> bool: ...
    async def set_relative_position_body(
        self, forward: float, right: float, up: float, angle: float
    ) -> bool: ...

    # Velocity control
    async def set_velocity_enu(
        self, north_vel: float, east_vel: float, up_vel: float, angle_vel: float
    ) -> bool: ...
    async def set_velocity_body(
        self, forward_vel: float, right_vel: float, up_vel: float, angle_vel: float
    ) -> bool: ...

    # Gimbal
    async def set_gimbal_pose(
        self,
        pitch: float,
        roll: float,
        yaw: float,
        *,
        mode: Literal["ABSOLUTE", "RELATIVE", "VELOCITY"] = "ABSOLUTE",
    ) -> bool: ...

    # Compute controls
    async def clear_compute_result(self, compute_type: str) -> bool: ...
    async def configure_compute(
        self,
        compute_model: str,
        hsv_lower_bound: Tuple[int, int, int],
        hsv_upper_bound: Tuple[int, int, int],
    ) -> bool: ...


# ---------- Data-plane (telemetry, perception, mission state) ----------

class Data(Protocol):
    """Abstract data-plane interface (telemetry, perception results, misc data)."""

    async def get_compute_result(self, compute_type: str) -> ComputeResults: ...
    async def get_telemetry(self) -> Optional[Telemetry]: ...
    async def update_current_task(self, current_task: str) -> None: ...
    async def get_waypoints(self, area_path: str) -> Optional[List[Waypoint]]: ...


# ---------- Reporting / mission UX channel ----------

class Report(Protocol):
    """Reporting/UX channel for mission lifecycle + map data."""

    async def send_notification(self, msg: Literal["start", "finish"]) -> Optional[ReportUpdate]: ...
    async def get_waypoints(self, area_path: str) -> Optional[List[Waypoint]]: ...