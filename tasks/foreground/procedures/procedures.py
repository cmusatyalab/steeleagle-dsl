from pydantic import BaseModel
from typing import List
from actions import ExecutableAction, SetGimbalPose, SetGPSLocation
import asyncio


class ElevateToAltitude(ExecutableAction):
    target_altitude: float

    async def execute(self, context):
        while True:
            tel = await context['data'].get_telemetry()
            if tel['global_position']['relative_altitude'] > self.target_altitude:
                break
            await context['ctrl'].set_velocity_body(0.0, 0.0, 1.0, 0.0)
            await asyncio.sleep(1)


class PrePatrolSequence(ExecutableAction):
    gimbal: SetGimbalPose
    elevate: ElevateToAltitude

    async def execute(self, context):
        await self.elevate.execute(context)
        await self.gimbal.execute(context)


class PatrolArea(ExecutableAction):
    waypoints: List[SetGPSLocation]
    hover_time: float = 1.0

    async def execute(self, context):
        for wp in self.waypoints:
            await wp.execute(context)
            await asyncio.sleep(self.hover_time)


