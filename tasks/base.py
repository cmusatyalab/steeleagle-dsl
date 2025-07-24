# tasks/base.py

from typing import Dict, Type
from pydantic import BaseModel

# Base class that all tasks should inherit
class TaskIR(BaseModel):
    async def execute(self, context):
        raise NotImplementedError()

# Central registry
task_registry: Dict[str, Type[TaskIR]] = {}

# Decorator to register a task
def register_task(name: str):
    def wrapper(cls: Type[TaskIR]):
        task_registry[name] = cls
        return cls
    return wrapper
