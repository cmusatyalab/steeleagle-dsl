# runtime/fsm.py (minimal)
from __future__ import annotations
import asyncio
from typing import Dict, Tuple
from compiler.ir import MissionIR
from compiler.registry import get_action, get_event


class MissionFSM:
    def __init__(self, mission: MissionIR):
        self.mission = mission
        # (state, event) -> next_state
        self._transitions: Dict[Tuple[str, str], str] = mission.transitions

    async def run(self, context):
        state = self.mission.start_action_id

        while True:
            # --- build current action instance ---
            a_ir = self.mission.actions[state]
            a_cls = get_action(a_ir.type_name)
            if a_cls is None:
                raise RuntimeError(f"Unknown action type: {a_ir.type_name}")
            action = a_cls(**a_ir.attributes)

            # --- gather this state's events (by name) ---
            event_names = [ev for (s, ev) in self._transitions.keys() if s == state]

            # --- spawn event monitors ---
            event_tasks = []
            for ev_name in event_names:
                e_ir = self.mission.events.get(ev_name)
                if e_ir is None:
                    # allow synthetic events like "done" that are handled after action
                    continue
                e_cls = get_event(e_ir.type_name)
                if e_cls is None:
                    continue
                event = e_cls(**e_ir.attributes)
                event_tasks.append(asyncio.create_task(self._wait_event(event, ev_name)))

            # --- run action and events concurrently; first completion wins ---
            action_task = asyncio.create_task(action.execute(context))
            pending = set(event_tasks) | {action_task}

            # loop until either an event fires True or the action completes
            winner_name: str | None = None
            while pending:
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

                # did an event fire?
                for t in list(done):
                    if t is action_task:
                        # action finished; break out of inner loop
                        pending = set()  # stop waiting more
                        break
                    try:
                        ok, ev_name = t.result()
                    except Exception:
                        ok, ev_name = False, None
                    if ok:
                        winner_name = ev_name
                        pending = set()  # stop waiting more
                        break

            # cancel any leftover event tasks
            for t in event_tasks:
                if not t.done():
                    t.cancel()

            # --- decide next state ---
            if winner_name is not None:
                # event transition
                state = self._transitions[(a_ir.action_id, winner_name)]
            else:
                # action finished; try 'done' transition, else mission ends
                key = (a_ir.action_id, "done")
                if key in self._transitions:
                    state = self._transitions[key]
                else:
                    return  # terminal

            # if new state has no outgoing edges, run its action once and end on completion
            if not any(s == state for (s, _) in self._transitions.keys()):
                a_ir = self.mission.actions[state]
                a_cls = get_action(a_ir.type_name)
                if a_cls is None:
                    raise RuntimeError(f"Unknown action type: {a_ir.type_name}")
                action = a_cls(**a_ir.attributes)
                await action.execute(context)
                return

    async def _wait_event(self, event, ev_name: str):
        """
        Await the event. It should return True if it fires, False/None otherwise.
        We return (bool, name) to let the caller know which event fired.
        """
        try:
            ok = await event.execute(context=None)  # most events ignore extra args
        except TypeError:
            # If your event signature expects (context), pass it as needed.
            # The minimal version doesn't plumb context; adapt if your events need it:
            # ok = await event.execute(context)
            ok = False
        return bool(ok), ev_name
