from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Tuple, Type

# --- IR models ---

class ActionIR(BaseModel):
    type_name: str
    action_id: str
    attributes: Dict[str, Any]

class EventIR(BaseModel):
    type_name: str
    event_name: str          # the event identifier used in Mission
    attributes: Dict[str, Any]

class MissionIR(BaseModel):
    actions: Dict[str, ActionIR]                    # action_id -> ActionIR
    events: Dict[str, EventIR]                      # event_name -> EventIR
    start_action_id: str
    transitions: Dict[Tuple[str, str], str]         # (current_action_id, event_name) -> next_action_id