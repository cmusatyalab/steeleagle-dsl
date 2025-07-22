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



class TransitionSetup(BaseModel):
    transition_attributes: dict  # e.g., {"object_detection": {"target": "car"}, "timeout": {"seconds": 10}}
    task_id: str
    trans_active: list
    trans_active_lock: asyncio.Lock
    trigger_event_queue: asyncio.Queue

    async def execute(self, context):
        transition_context = TransitionContext(
            task_id=self.task_id,
            trans_active=self.trans_active,
            trans_active_lock=self.trans_active_lock,
            trigger_event_queue=self.trigger_event_queue,
        )

        context["transitions"] = []  # Store running transitions here

        for name, args in self.transition_attributes.items():
            cls = TRANSITION_REGISTRY.get(name)
            if not cls:
                raise ValueError(f"Unknown transition type: {name}")

            transition = cls(context=transition_context, **args)
            await transition.start()
            context["transitions"].append(transition)