# tasks/actions/procedures.py
import asyncio
from typing import Optional
from pydantic import Field
from compiler.registry import register_action
from tasks.base import ExecutableAction  # your BaseModel+async base
from tasks.actions.primitives import SetGimbalPose, SetGPSLocation, SetVelocityBody


@register_action
class ElevateToAltitude(ExecutableAction):
    target_altitude: float = Field(..., description="meters AGL/relative")
    tolerance: float = Field(0.2, ge=0.0, description="stop when within this of target")
    poll_period: float = Field(0.5, gt=0.0, description="seconds between telemetry polls")
    climb_speed: float = Field(1.0, description="m/s (adjust sign for your FCU if needed)")
    max_duration: Optional[float] = Field(60.0, gt=0.0, description="seconds; None = no limit")
    set_vel : SetVelocityBody

    async def execute(self, context):
        start = asyncio.get_event_loop().time()
        while True:
            tel = await context['data'].get_telemetry()
            rel_alt = tel['global_position']['relative_altitude']

            if rel_alt + self.tolerance >= self.target_altitude:
                break

            await self.set_vel.execute(0.0, 0.0, self.climb_speed, 0.0)

            if self.max_duration is not None:
                if asyncio.get_event_loop().time() - start > self.max_duration:
                    raise TimeoutError(
                        f"ElevateToAltitude timed out after {self.max_duration}s "
                        f"(current={rel_alt}, target={self.target_altitude})"
                    )
            await asyncio.sleep(self.poll_period)


@register_action
class PrePatrolSequence(ExecutableAction):
    elevate: ElevateToAltitude
    gimbal: SetGimbalPose

    async def execute(self, context):
        await self.elevate.execute(context)
        await self.gimbal.execute(context)


@register_action
class PatrolArea(ExecutableAction):
    area_path: str = Field(..., min_length=1, description="dot-path into waypoint map")
    hover_time: float = Field(1.0, ge=0.0, description="seconds to hover after each move")
    alt: Optional[float] = Field(default=None, description="altitude to use for each waypoint")
    goto: SetGPSLocation

    async def execute(self, context):
        # Resolve waypoints at runtime (keeps DSL clean)
        points = await context['data'].get_waypoints(self.area_path)
        if not points:
            raise RuntimeError(f"No waypoints found for '{self.area_path}'")

        for p in points:
            # Build a SetGPSLocation action instance for each point and execute it.
            await self.goto.execute(lat=float(p['lat']), lon=float(p['lng']), alt=self.alt)

            if self.hover_time > 0:
                await asyncio.sleep(self.hover_time)
