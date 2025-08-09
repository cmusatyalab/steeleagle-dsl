<<<<<<< HEAD

from pydantic import BaseModel, Field


task_registry = {}

def register_task(cls):
    task_registry[cls.__name__] = cls
    return cls

# Base class to enforce the execute interface
class ExecutableAction(BaseModel):
    async def execute(self, context):
        raise NotImplementedError
=======
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
>>>>>>> origin/grammar-loose-python
