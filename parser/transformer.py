<<<<<<< HEAD
from lark import Transformer, v_args, Token
from validator import check_availability
from ir import MissionIR, ActionIR, EventIR
from typing import Dict, List, Tuple, Optional, Any



# --- Helpers ---
def _duration_to_seconds(tok: str) -> int:
    # "60s" | "60sec" | "5m" | "2min"
    tok = tok.strip()
    if tok.endswith(("s", "sec")):
        num = tok[:-1] if tok.endswith("s") else tok[:-3]
        return int(float(num))
    if tok.endswith(("m", "min")):
        num = tok[:-1] if tok.endswith("m") else tok[:-3]
        return int(float(num) * 60)
    # fallback: treat as seconds number
    return int(float(tok))

@v_args(inline=True)
class DroneDSLTransformer(Transformer):
    # Accumulators
    def __init__(self, *, implicit_done=True):
        super().__init__()
        self._actions: Dict[str, ActionIR] = {}
        self._events: Dict[str, EventIR] = {}
        self._start: Optional[str] = None
        self._during: Dict[str, Dict[str, str]] = {}   # state -> {event: next}
        self._implicit_done = implicit_done


    # ----- Actions -----
    def action_decl(self, type_name: Token, action_id: Token, attrs: Optional[List] = None):
        type_str = str(type_name)
        aid = str(action_id)
        attrs_dict = {} if attrs is None else dict(attrs)

        # 1) Ensure the type is registered (returns the class)
        action_cls = check_availability(type_str)

        # 2) (Optional but recommended) Pydantic validation of attributes
        #    Instantiate to validate schema, then discard the instance.
        try:
            action_cls(**attrs_dict)
        except Exception as e:
            raise ValueError(f"Action '{aid}' of type '{type_str}' has invalid attributes: {e}") from e

        # 3) Store IR (keep your existing IR shape; class is resolved already if you want to stash it)
        self._actions[aid] = ActionIR(
            type_name=type_str,
            action_id=aid,
            attributes=attrs_dict,
        )

    def action_body(self, *items):
        # children are (attr, attr, ...)
        return items

    # ----- Events -----
    def event_decl(self, type_name: Token, event_name: Token, attrs: Optional[List] = None):
        type_str = str(type_name)
        ename = str(event_name)
        attrs_dict = {} if attrs is None else dict(attrs)

        # 1) Ensure the event generator type is registered
        event_cls = check_availability(type_str)

        # 2) Pydantic validation for the event’s config
        try:
            event_cls(**attrs_dict)
        except Exception as e:
            raise ValueError(f"Event '{ename}' of type '{type_str}' has invalid attributes: {e}") from e

        # 3) Store IR
        self._events[ename] = EventIR(
            type_name=type_str,
            event_name=ename,
            attributes=attrs_dict,
        )

    def event_body(self, *items):
        return items

    # ----- Attributes -----
    def attr(self, k: Token, _colon, v):
        return (str(k), v)

    def value(self, v):
        # v can be Token(NAME/NUMBER/DURATION)
        if isinstance(v, Token):
            if v.type == "DURATION":
                return _duration_to_seconds(str(v))
            if v.type == "NUMBER":
                # int if whole, else float
                f = float(str(v))
                return int(f) if f.is_integer() else f
            if v.type == "NAME":
                return str(v)
        return v

    # ----- Mission -----
    def mission_start(self, _start_kw, action_id: Token, *_nl):
        self._start = str(action_id)

    def during_block(self, _during_kw, action_id: Token, _colon, *_rules):
        sid = str(action_id)
        # _rules contains 'transition_rule' outputs as tuples (event, next)
        # Filter only tuples:
        rules = [r for r in _rules if isinstance(r, tuple) and len(r) == 2]
        self._during.setdefault(sid, {})
        for ev, nxt in rules:
            self._during[sid][ev] = nxt

    def transition_rule(self, ev: Token, _arrow, nxt: Token, *_nl):
        return (str(ev), str(nxt))

    # ----- Top-level -----
    def start(self, _):
        # Implicit done -> land insertion
        transitions: Dict[Tuple[str, str], str] = {}
        # Determine default land action (unique Land)
        land_ids = [a.action_id for a in self._actions.values() if a.type_name.lower() == "land"]
        default_land: Optional[str] = None
        if self._implicit_done and len(land_ids) == 1:
            default_land = land_ids[0]

        for state, evmap in self._during.items():
            # copy explicit
            for ev, nxt in evmap.items():
                transitions[(state, ev)] = nxt
            # add implicit done if requested and not present
            if self._implicit_done and "done" not in evmap and default_land:
                transitions[(state, "done")] = default_land

        if self._start is None:
            raise ValueError("Mission: missing 'Start <action_id>'")

        # Basic validation
        if self._start not in self._actions:
            raise ValueError(f"Mission: Start references unknown action '{self._start}'")
        for (_state, _ev), nxt in transitions.items():
            if nxt not in self._actions:
                raise ValueError(f"Mission: transition target '{nxt}' is not a defined action")

        return MissionIR(
            actions=self._actions,
            events=self._events,
            start_action_id=self._start,
            transitions=transitions
        )
=======
from lark import Transformer
from tasks.base import task_registry
from compiler.ir import MissionIR, TransitionIR


class DroneDSLTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.task_definitions = {}
        self.transitions = []
        self.start_task = None

    def task_decl(self, items):
        task_type_name, task_name, attributes = items
        task_type_str = str(task_type_name)
        task_name_str = str(task_name)

        task_cls = task_registry.get(task_type_str)
        if task_cls is None:
            raise ValueError(f"Unregistered task type: {task_type_str}")

        kwargs = {k: v for k, v in attributes}
        kwargs['task_id'] = task_name_str

        instance = task_cls(**kwargs)
        self.task_definitions[task_name_str] = instance

    def attribute(self, items):
        key, value = items
        return str(key), value

    def paren_tuple(self, items):
        return tuple(float(x) for x in items)

    def attribute_expr(self, items):
        return items[0]

    def mission_start_decl(self, items):
        self.start_task = str(items[0])

    def mission_transition(self, items):
        cond, from_task, to_task = items
        self.transitions.append(TransitionIR(
            cond_id=cond['id'],
            cond_arg=cond.get('arg'),
            from_task=str(from_task),
            to_task=str(to_task)
        ))

    def cond(self, items):
        cond_id = str(items[0])
        if len(items) == 2:
            arg = items[1]
            return {'id': cond_id, 'arg': arg}
        return {'id': cond_id}

    def start(self, _):
        return MissionIR(
            tasks=self.task_definitions,
            transitions=self.transitions,
            start=self.start_task
        )

    # Simple terminals
    def ID(self, token):
        return str(token)

    def NUMBER(self, token):
        return float(token) if '.' in token else int(token)
>>>>>>> origin/grammar-loose-python
