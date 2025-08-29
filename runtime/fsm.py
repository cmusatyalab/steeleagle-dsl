# runtime/fsm.py (minimal-plus)
from __future__ import annotations
import asyncio
import contextlib
from typing import Dict, Tuple
from compiler.ir import MissionIR
from compiler.registry import get_action, get_event



class MissionFSM:
    def __init__(self, mission: MissionIR):
        self.mission = mission
        self.transition = mission.transitions
        print("self.transition:" + str(self.transition))
    async def run(self):
        pass
