# compiler/validator.py
from __future__ import annotations
from typing import Type, Dict, Tuple, Any, Literal
from pydantic import BaseModel, ValidationError

from compiler.registry import get_action, get_event

# ---- Robust auto-import of all task modules under tasks/ ----
import importlib, pkgutil, sys

def _eager_import_tasks_pkg():
    """
    Import tasks package and eagerly import all its submodules (tasks.actions, tasks.events, etc.)
    so that @register_action / @register_event decorators run and fill the registry.
    """
    # Import the root tasks package
    tasks_pkg = importlib.import_module("tasks")

    # Walk submodules and import each once
    for m in pkgutil.walk_packages(tasks_pkg.__path__, tasks_pkg.__name__ + "."):
        # m is a ModuleInfo(tuple): (module_finder, name, ispkg)
        name = m.name
        if name not in sys.modules:
            importlib.import_module(name)

# Call once on import
_eager_import_tasks_pkg()
# -------------------------------------------------------------

class DSLValidationError(ValueError):
    """Compact error used at the DSL surface (transformer raises with this message)."""

def _lookup(kind: Literal["action", "event"], type_name: str) -> Type[BaseModel]:
    cls = get_action(type_name) if kind == "action" else get_event(type_name)
    if cls is None:
        raise DSLValidationError(f"Unregistered {kind} type: {type_name}")
    return cls

def _instantiate(cls: Type[BaseModel], attrs: Dict[str, Any]) -> BaseModel:
    try:
        return cls(**attrs)
    except ValidationError as e:
        msgs = "; ".join(err["msg"] for err in e.errors())
        raise DSLValidationError(msgs) from e
    except Exception as e:
        raise DSLValidationError(str(e)) from e

def validate_action(type_name: str, attrs: Dict[str, Any]) -> Tuple[Type[BaseModel], Dict[str, Any]]:
    cls = _lookup("action", type_name)
    model = _instantiate(cls, attrs)
    return cls, model.model_dump()

def validate_event(type_name: str, attrs: Dict[str, Any]) -> Tuple[Type[BaseModel], Dict[str, Any]]:
    cls = _lookup("event", type_name)
    model = _instantiate(cls, attrs)
    return cls, model.model_dump()
