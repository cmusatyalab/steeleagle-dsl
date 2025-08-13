# tasks/events/combinators.py
from __future__ import annotations

import asyncio
from typing import List, Optional
from pydantic import Field, ConfigDict
from compiler.registry import register_event
from tasks.base import ExecutableEvent


# ========== basic boolean combinators ==========

@register_event
class AnyOf(ExecutableEvent):
    """Fires when ANY child event is true in a poll."""
    events: List[ExecutableEvent] = Field(..., min_items=1)

    async def check(self, context) -> bool:
        for ev in self.events:
            if await ev.check(context):
                return True
        return False


@register_event
class AllOf(ExecutableEvent):
    """Fires when ALL child events are true in the same poll."""
    events: List[ExecutableEvent] = Field(..., min_items=1)

    async def check(self, context) -> bool:
        for ev in self.events:
            if not await ev.check(context):
                return False
        return True


@register_event
class NotEvent(ExecutableEvent):
    """Fires when the child event is false (logical NOT)."""
    event: ExecutableEvent

    async def check(self, context) -> bool:
        return not (await self.event.check(context))


@register_event
class NOfM(ExecutableEvent):
    """Fires when at least N of M child events are true in a poll."""
    n: int = Field(..., gt=0)
    events: List[ExecutableEvent] = Field(..., min_items=1)

    async def check(self, context) -> bool:
        count = 0
        for ev in self.events:
            if await ev.check(context):
                count += 1
                if count >= self.n:
                    return True
        return False


# ========== time/state aware combinators ==========

@register_event
class Sustained(ExecutableEvent):
    """
    Fires when `event` stays true for at least `duration` seconds (consecutive).
    Resets when a poll returns false.
    """
    event: ExecutableEvent
    duration: float = Field(..., gt=0.0)

    # internal state
    _true_since: Optional[float] = None
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    async def check(self, context) -> bool:
        now = asyncio.get_event_loop().time()
        if await self.event.check(context):
            if self._true_since is None:
                self._true_since = now
            return (now - self._true_since) >= self.duration
        else:
            self._true_since = None
            return False


@register_event
class Debounced(ExecutableEvent):
    """
    Fires when `event` becomes true and remains true for `stable_true` seconds
    (classic debounce to filter noisy signals).
    """
    event: ExecutableEvent
    stable_true: float = Field(0.5, ge=0.0)

    _candidate_since: Optional[float] = None

    async def check(self, context) -> bool:
        now = asyncio.get_event_loop().time()
        if await self.event.check(context):
            if self._candidate_since is None:
                self._candidate_since = now
            return (now - self._candidate_since) >= self.stable_true
        else:
            self._candidate_since = None
            return False


@register_event
class RisingEdge(ExecutableEvent):
    """
    Fires precisely when `event` transitions False -> True (one-shot).
    Stays false until the next rising edge.
    """
    event: ExecutableEvent
    _prev: bool = False

    async def check(self, context) -> bool:
        cur = await self.event.check(context)
        fired = (not self._prev) and cur
        self._prev = cur
        return fired


@register_event
class FallingEdge(ExecutableEvent):
    """
    Fires when `event` transitions True -> False (one-shot).
    """
    event: ExecutableEvent
    _prev: bool = False

    async def check(self, context) -> bool:
        cur = await self.event.check(context)
        fired = self._prev and (not cur)
        self._prev = cur
        return fired


@register_event
class SequenceWithin(ExecutableEvent):
    """
    Fires when child events occur IN ORDER within `window` seconds overall.
    A child “occurs” when its `check()` is true on a poll; sequence state resets on timeout.
    Example: [AltitudeReached(20m), DetectionFound(person)] within 15s.
    """
    events: List[ExecutableEvent] = Field(..., min_items=1)
    window: float = Field(..., gt=0.0)

    _idx: int = 0
    _start: Optional[float] = None

    async def check(self, context) -> bool:
        now = asyncio.get_event_loop().time()

        if self._idx == 0 and self._start is None:
            self._start = now

        # window timeout
        if self._start is not None and (now - self._start) > self.window:
            # reset
            self._idx = 0
            self._start = now
            return False

        # check current required event
        cur_ev = self.events[self._idx]
        if await cur_ev.check(context):
            self._idx += 1
            if self._idx >= len(self.events):
                # success, reset for next time
                self._idx = 0
                self._start = None
                return True
        return False


@register_event
class Until(ExecutableEvent):
    """
    Fires when `event` becomes true BEFORE `until_event` becomes true.
    If `until_event` fires first, this event will not fire (locks out) until
    both are false again in the same poll (lock resets).
    """
    event: ExecutableEvent
    until_event: ExecutableEvent
    _locked_out: bool = False

    async def check(self, context) -> bool:
        until_hit = await self.until_event.check(context)
        if until_hit:
            self._locked_out = True
            return False
        if self._locked_out:
            # reset lock when both are false in the same poll
            ev_now = await self.event.check(context)
            if not ev_now and not until_hit:
                self._locked_out = False
            return False
        return await self.event.check(context)
