from pydantic import BaseModel, ConfigDict

class Executable(BaseModel):
    # Strict validation; allow non-pydantic objects in fields if needed
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

    async def execute(self, context):
        raise NotImplementedError

class ExecutableAction(Executable):
    """Marker base for actions (things you execute)."""
    pass

class ExecutableEvent(Executable):
    """Marker base for events (things you wait/observe)."""
    pass
