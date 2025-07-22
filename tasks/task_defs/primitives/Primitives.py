from pydantic import BaseModel, Field
import asyncio
from typing import Optional

# Base class to enforce the execute interface
class ExecutableAction(BaseModel):
    async def execute(self, context):
        raise NotImplementedError


# ===== Low-Level Actions =====

class TakeOff(ExecutableAction):
    async def execute(self, context):
        return await context['ctrl'].take_off()


class Land(ExecutableAction):
    async def execute(self, context):
        return await context['ctrl'].land()


class ReturnToHome(ExecutableAction):
    async def execute(self, context):
        return await context['ctrl'].rth()


class Hover(ExecutableAction):
    async def execute(self, context):
        return await context['ctrl'].hover()


class SetGPSLocation(ExecutableAction):
    lat: float
    lng: float
    alt: float
    bearing: Optional[float] = 0.0

    async def execute(self, context):
        return await context['ctrl'].set_gps_location(self.lat, self.lng, self.alt, self.bearing)


class SetRelativePositionENU(ExecutableAction):
    north: float
    east: float
    up: float
    angle: float

    async def execute(self, context):
        return await context['ctrl'].set_relative_position_enu(self.north, self.east, self.up, self.angle)


class SetRelativePositionBody(ExecutableAction):
    forward: float
    right: float
    up: float
    angle: float

    async def execute(self, context):
        return await context['ctrl'].set_relative_position_body(self.forward, self.right, self.up, self.angle)


class SetVelocityENU(ExecutableAction):
    north_vel: float
    east_vel: float
    up_vel: float
    angle_vel: float

    async def execute(self, context):
        return await context['ctrl'].set_velocity_enu(self.north_vel, self.east_vel, self.up_vel, self.angle_vel)


class SetVelocityBody(ExecutableAction):
    forward_vel: float
    right_vel: float
    up_vel: float
    angle_vel: float

    async def execute(self, context):
        return await context['ctrl'].set_velocity_body(self.forward_vel, self.right_vel, self.up_vel, self.angle_vel)


class SetGimbalPose(ExecutableAction):
    pitch: float
    roll: float = 0.0
    yaw: float = 0.0

    async def execute(self, context):
        return await context['ctrl'].set_gimbal_pose(self.pitch, self.roll, self.yaw)


class ClearComputeResult(ExecutableAction):
    compute_type: str

    async def execute(self, context):
        return await context['ctrl'].clear_compute_result(self.compute_type)


class ConfigureCompute(ExecutableAction):
    model: str
    lower_bound: tuple[int, int, int]
    upper_bound: tuple[int, int, int]

    async def execute(self, context):
        return await context['ctrl'].configure_compute(self.model, self.lower_bound, self.upper_bound)
