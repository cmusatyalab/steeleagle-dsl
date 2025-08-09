
from pydantic import BaseModel, Field


task_registry = {}

def register_task(cls):
    task_registry[cls.__name__] = cls
    return cls

# Base class to enforce the execute interface
class ExecutableAction(BaseModel):
    async def execute(self, context):
        raise NotImplementedError