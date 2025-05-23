"""fsm_kit — a small, typed, dependency-free finite-state-machine toolkit.

The package is intentionally strict: every transition is validated at build
time, every trigger is observable, and diagrams are generated from the same
declarative definition that executes at runtime.
"""

from .core import (
    Action,
    Guard,
    InvalidStateError,
    InvalidTransitionError,
    StateMachine,
    Transition,
    TransitionRecord,
    UnknownEventError,
)
from .machines import ModThreeMachine, TrafficLightMachine

__all__ = [
    "Action",
    "Guard",
    "InvalidStateError",
    "InvalidTransitionError",
    "StateMachine",
    "Transition",
    "TransitionRecord",
    "UnknownEventError",
    "ModThreeMachine",
    "TrafficLightMachine",
]

__version__ = "1.0.0"
