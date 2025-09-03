# runtime/context.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import logging

from runtime.interfaces import Ctrl, Data, Report

@dataclass
class RuntimeContext:
    ctrl: Ctrl
    data: Data
    report: Optional[Report] = None
    logger: logging.Logger = logging.getLogger("runtime")
    bag: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: str):
        if key == "ctrl": return self.ctrl
        if key == "data": return self.data
        if key == "report": return self.report
        if key == "logger": return self.logger
        if key == "bag": return self.bag
        raise KeyError(key)