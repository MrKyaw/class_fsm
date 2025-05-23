"""Deterministic finite-state-machine engine with guards, actions and exports.

Design goals
------------
* **Fail fast** — malformed machines raise at construction/registration time.
* **Deterministic** — one transition per (state, event); duplicates rejected.
* **Observable** — every successful trigger produces an immutable record.
* **Portable** — no third-party runtime dependencies (Python 3.10+).
* **Diagrammable** — Mermaid and Graphviz DOT are emitted from the live model.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Deque, Iterable, Mapping

State = str
Event = str

Guard = Callable[[Mapping[str, Any]], bool]
Action = Callable[["TransitionRecord"], None]


class FSMError(Exception):
    """Base class for all ``fsm_kit`` errors."""


class InvalidStateError(FSMError, ValueError):
    """Raised when a state is unknown or a definition is malformed."""


class UnknownEventError(FSMError, ValueError):
    """Raised when an event is not part of the machine's alphabet."""


class InvalidTransitionError(FSMError, RuntimeError):
    """Raised when no transition is defined for the current state/event pair."""


@dataclass(frozen=True)
class Transition:
    """An immutable edge in the state graph."""

    source: State
    event: Event
    target: State
    guard: Guard | None = None
    action: Action | None = None

    def __post_init__(self) -> None:
        for name in ("source", "event", "target"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise InvalidStateError(f"{name} must be a non-empty string")


@dataclass(frozen=True)
class TransitionRecord:
    """Audit record emitted for each successful transition."""

    source: State
    event: Event
    target: State
    context: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "event": self.event,
            "target": self.target,
            "context": dict(self.context),
        }


class StateMachine:
    """A deterministic finite state machine.

    Args:
        initial: Starting state. Registered automatically.
        history_limit: Maximum number of transition records retained.

    Example:
        >>> machine = StateMachine("idle")
        >>> machine.add_transition("idle", "start", "running")
        'running'
        >>> machine.trigger("start")
        TransitionRecord(source='idle', event='start', target='running', context={})
        >>> machine.state
        'running'
    """

    def __init__(self, initial: State, *, history_limit: int = 100) -> None:
        if not isinstance(initial, str) or not initial.strip():
            raise InvalidStateError("initial state must be a non-empty string")
        if not isinstance(history_limit, int) or isinstance(history_limit, bool):
            raise TypeError("history_limit must be an integer")
        if history_limit < 1:
            raise ValueError("history_limit must be >= 1")

        self._initial = initial
        self._state = initial
        self._states: set[State] = {initial}
        self._events: set[Event] = set()
        self._transitions: dict[tuple[State, Event], Transition] = {}
        self._history: Deque[TransitionRecord] = deque(maxlen=history_limit)
        self._history_limit = history_limit

    # ------------------------------------------------------------------ model
    @property
    def state(self) -> State:
        """Current state."""
        return self._state

    @property
    def initial_state(self) -> State:
        """State used by :meth:`reset`."""
        return self._initial

    @property
    def states(self) -> frozenset[State]:
        return frozenset(self._states)

    @property
    def events(self) -> frozenset[Event]:
        return frozenset(self._events)

    @property
    def history(self) -> tuple[TransitionRecord, ...]:
        """Immutable snapshot of the most recent transitions (oldest first)."""
        return tuple(self._history)

    @property
    def transitions(self) -> tuple[Transition, ...]:
        """Transitions in deterministic display order."""
        return tuple(
            self._transitions[key] for key in sorted(self._transitions)
        )

    def add_state(self, state: State) -> None:
        """Register an isolated state (useful for terminal/error states)."""
        if not isinstance(state, str) or not state.strip():
            raise InvalidStateError("state must be a non-empty string")
        self._states.add(state)

    def add_transition(
        self,
        source: State,
        event: Event,
        target: State,
        *,
        guard: Guard | None = None,
        action: Action | None = None,
    ) -> State:
        """Register a transition and return the target state.

        Raises:
            InvalidStateError: source/target empty or event empty.
            ValueError: a transition already exists for ``(source, event)``.
            TypeError: guard/action are not callable.
        """
        transition = Transition(source, event, target, guard, action)
        if guard is not None and not callable(guard):
            raise TypeError("guard must be callable or None")
        if action is not None and not callable(action):
            raise TypeError("action must be callable or None")

        key = (source, event)
        if key in self._transitions:
            raise ValueError(
                f"duplicate transition for state={source!r}, event={event!r}"
            )

        self._states.update((source, target))
        self._events.add(event)
        self._transitions[key] = transition
        return target

    # --------------------------------------------------------------- runtime
    def can_trigger(self, event: Event, context: Mapping[str, Any] | None = None) -> bool:
        """Return ``True`` when ``event`` is valid here and its guard passes."""
        transition = self._transitions.get((self._state, event))
        if transition is None:
            return False
        return self._guard_passes(transition, context or {})

    def trigger(
        self, event: Event, context: Mapping[str, Any] | None = None
    ) -> TransitionRecord:
        """Execute ``event`` and return an immutable audit record.

        The machine state is only mutated after the guard passes and the
        action completes successfully, so a failing action cannot leave the
        machine in a half-transitioned state.
        """
        if event not in self._events:
            raise UnknownEventError(f"unknown event: {event!r}")

        transition = self._transitions.get((self._state, event))
        if transition is None:
            raise InvalidTransitionError(
                f"no transition from {self._state!r} on event {event!r}"
            )

        payload: dict[str, Any] = dict(context or {})
        if not self._guard_passes(transition, payload):
            raise InvalidTransitionError(
                f"guard rejected event {event!r} in state {self._state!r}"
            )

        record = TransitionRecord(
            source=self._state,
            event=event,
            target=transition.target,
            context=payload,
        )
        if transition.action is not None:
            transition.action(record)

        self._state = transition.target
        self._history.append(record)
        return record

    def reset(self) -> None:
        """Return to the initial state. History is intentionally preserved."""
        self._state = self._initial

    def replay(self, events: Iterable[Event]) -> tuple[TransitionRecord, ...]:
        """Trigger a sequence of events and return the records they produced.

        The machine is **not** reset first; call :meth:`reset` explicitly when
        replaying from the initial state.
        """
        return tuple(self.trigger(event) for event in events)

    # --------------------------------------------------------------- exports
    def export_mermaid(self, *, title: str | None = None) -> str:
        """Render the state graph as a Mermaid ``stateDiagram-v2``."""
        lines: list[str] = []
        if title:
            lines.extend(["---", f"title: {self._escape_mermaid(title)}", "---"])
        lines.append("stateDiagram-v2")
        lines.append(f"    [*] --> {self._mermaid_id(self._initial)}")
        for transition in self.transitions:
            label = transition.event
            if transition.guard is not None:
                label += " [guard]"
            suffix = ""
            if transition.action is not None:
                suffix = " / action"
            lines.append(
                f"    {self._mermaid_id(transition.source)} --> "
                f"{self._mermaid_id(transition.target)}: {label}{suffix}"
            )
        return "\n".join(lines)

    def export_dot(self, *, title: str | None = None) -> str:
        """Render the state graph as Graphviz DOT."""
        lines = ["digraph fsm {"]
        if title:
            lines.append(f'    label="{self._dot_escape(title)}";')
        lines.append("    rankdir=LR;")
        lines.append('    "__start__" [shape=point];')
        lines.append(f'    "__start__" -> "{self._dot_escape(self._initial)}";')
        for transition in self.transitions:
            label = self._dot_escape(transition.event)
            if transition.guard is not None:
                label += " [guard]"
            if transition.action is not None:
                label += " / action"
            lines.append(
                f'    "{self._dot_escape(transition.source)}" -> '
                f'"{self._dot_escape(transition.target)}" [label="{label}"];'
            )
        lines.append("}")
        return "\n".join(lines)

    # --------------------------------------------------------------- helpers
    @staticmethod
    def _guard_passes(transition: Transition, context: Mapping[str, Any]) -> bool:
        if transition.guard is None:
            return True
        return bool(transition.guard(context))

    @staticmethod
    def _mermaid_id(state: State) -> str:
        safe = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in state)
        return safe or "state"

    @staticmethod
    def _escape_mermaid(value: str) -> str:
        return value.replace("\n", " ").replace(":", " -")

    @staticmethod
    def _dot_escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
