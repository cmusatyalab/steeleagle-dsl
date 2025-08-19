from __future__ import annotations

import re
from typing import Dict, List, Tuple, Optional, Any, Iterable
from lark import Transformer, Tree, v_args, Token

from compiler.validator import validate_mission_ir
from compiler.ir import MissionIR, ActionIR, EventIR
from compiler.resolver import resolve_symbols
from compiler.loader import load_all

# ---------- Helpers ----------
def _duration_to_seconds(tok: str) -> int:
    tok = tok.strip()
    if tok.endswith(("s", "sec")):
        num = tok[:-1] if tok.endswith("s") else tok[:-3]
        return int(float(num))
    if tok.endswith(("m", "min")):
        num = tok[:-1] if tok.endswith("m") else tok[:-3]
        return int(float(num) * 60)
    return int(float(tok))

_IMPLICIT_EVENT_ALLOWLIST = re.compile(r"^(?:done|.*_done|.*_cleared)$")

def _pairs_to_dict(attrs: Optional[Iterable[Any]]) -> Dict[str, Any]:
    if attrs is None:
        return {}
    if isinstance(attrs, dict):
        return dict(attrs)
    pairs = []
    for it in attrs:
        if isinstance(it, tuple) and len(it) == 2 and isinstance(it[0], str):
            pairs.append(it)
    return dict(pairs)

@v_args(inline=True)
class DroneDSLTransformer(Transformer):
    """Parses DSL -> validates via validator.py -> builds IR. Supports implicit 'done' transitions."""
    def __init__(self, *, implicit_done: bool = True, validate_events: bool = True):
        super().__init__()
        self._actions: Dict[str, ActionIR] = {}
        self._events: Dict[str, EventIR] = {}
        self._start: Optional[str] = None
        self._during: Dict[str, Dict[str, str]] = {}
        self._implicit_done = implicit_done
        self._validate_events = validate_events

    # ----- Actions -----
    def action_decl(self, type_name: Token, action_id: Token, attrs: Optional[List] = None):
        type_str = str(type_name)
        aid = str(action_id)
        attrs_dict = _pairs_to_dict(attrs)
        # Defer validation: store raw attrs
        self._actions[aid] = ActionIR(type_name=type_str, action_id=aid, attributes=attrs_dict)

    def action_body(self, *items):
        return [it for it in items if isinstance(it, tuple) and len(it) == 2]

    # ----- Events -----
    def event_decl(self, type_name: Token, event_name: Token, attrs: Optional[List] = None):
        type_str = str(type_name)
        ename = str(event_name)
        attrs_dict = _pairs_to_dict(attrs)
        # Defer validation: store raw attrs
        self._events[ename] = EventIR(type_name=type_str, event_name=ename, attributes=attrs_dict)


    def event_body(self, *items):
        return [it for it in items if isinstance(it, tuple) and len(it) == 2]

    # ----- Attributes -----
    def attr(self, k: Token, _colon, v):
        return (str(k), v)
    
    def array(self, *items):
        # Keep only already-transformed VALUES; drop punctuation tokens
        return [it for it in items if not isinstance(it, Token)]

    def value(self, v):
        # (keep your existing logic)
        if isinstance(v, Tree):
            if v.data == 'array':
                # also filter tokens here, belt-and-suspenders
                return [self.value(child) for child in v.children if not isinstance(child, Token)]
            return v
        if isinstance(v, Token):
            t = v.type
            s = str(v)
            if t == "DURATION":
                return _duration_to_seconds(s)
            if t == "NUMBER":
                f = float(s); return int(f) if f.is_integer() else f
            if t == "STRING":
                return s[1:-1] if s and s[0]==s[-1] and s[0] in ("'", '"') else s
            if t == "NAME":
                return s
        return v

    # ----- Mission -----
    def mission_start(self, action_id: Token):
        self._start = str(action_id)

    def transition_body(self, *items):
        return [it for it in items if isinstance(it, tuple) and len(it) == 2]

    def transition_rule(self, ev: Token, _arrow, nxt: Token, *_nl):
        return (str(ev), str(nxt))

    # children: NAME, _NL, [(ev, nxt), ...]
    def during_block(self, action_id: Token, _nl, rules_list):
        sid = str(action_id)
        self._during.setdefault(sid, {})
        for ev, nxt in rules_list:
            self._during[sid][ev] = nxt

    def mission_block(self, *_children):
        return None

    # ----- Top-level -----
    def start(self, *children):
        transitions: Dict[Tuple[str, str], str] = {}

        land_ids = [a.action_id for a in self._actions.values() if a.type_name.lower() == "land"]
        default_land: Optional[str] = land_ids[0] if (self._implicit_done and len(land_ids) == 1) else None

        for state, evmap in self._during.items():
            for ev, nxt in evmap.items():
                transitions[(state, ev)] = nxt
            if self._implicit_done and "done" not in evmap and default_land:
                transitions[(state, "done")] = default_land

        if self._start is None:
            raise ValueError("Mission: missing 'Start <action_id>'")
        if self._start not in self._actions:
            raise ValueError(f"Mission: Start references unknown action '{self._start}'")

        for (_state, _ev), nxt in transitions.items():
            if nxt not in self._actions:
                raise ValueError(f"Mission: transition target '{nxt}' is not a defined action")

        if self._validate_events:
            referenced_events = {ev for (_st, ev) in transitions.keys()}
            missing = sorted(
                ev for ev in referenced_events
                if ev not in self._events and not _IMPLICIT_EVENT_ALLOWLIST.match(ev)
            )
            if missing:
                raise ValueError(f"Mission: referenced event(s) not declared: {', '.join(missing)}")

        mir = MissionIR(
            actions=self._actions,
            events=self._events,
            start_action_id=self._start,
            transitions=transitions
        )

        load_all()  # Ensure all actions/events are loaded before validation

        mir = resolve_symbols(mir)  # Resolve string references (IDs) into nested dicts
        print("Resolved symbols in mission IR:", mir)
        
        mir = validate_mission_ir(mir) # Validate & normalize via Pydantic (centralized in validator.py)
        return mir
