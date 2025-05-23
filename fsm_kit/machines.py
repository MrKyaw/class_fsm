"""Reference machines built on :class:`fsm_kit.core.StateMachine`."""

from __future__ import annotations

from .core import InvalidStateError, StateMachine


class ModThreeMachine(StateMachine):
    """Compute ``binary_number mod 3`` with the classic three-state automaton.

    State ``rN`` means "the bits consumed so far, interpreted as a binary
    number, have remainder N modulo 3". The machine therefore runs in O(n)
    time and O(1) space for an n-bit input — no big integers are ever built.

    Example:
        >>> fsm = ModThreeMachine()
        >>> fsm.feed_bits("1101")
        1
        >>> fsm.remainder
        1
    """

    _STATE_FOR_REMAINDER = {0: "r0", 1: "r1", 2: "r2"}

    def __init__(self) -> None:
        super().__init__("r0")
        for remainder, state in self._STATE_FOR_REMAINDER.items():
            # appending a 0 doubles the value: 2r mod 3
            self.add_transition(state, "0", self._STATE_FOR_REMAINDER[(2 * remainder) % 3])
            # appending a 1 doubles and adds one: (2r + 1) mod 3
            self.add_transition(
                state, "1", self._STATE_FOR_REMAINDER[(2 * remainder + 1) % 3]
            )

    def feed_bit(self, bit: str) -> int:
        """Consume one bit and return the updated remainder."""
        if bit not in ("0", "1"):
            raise ValueError("bit must be '0' or '1'")
        self.trigger(bit)
        return self.remainder

    def feed_bits(self, bits: str) -> int:
        """Consume a binary string and return its remainder modulo 3."""
        if not isinstance(bits, str):
            raise TypeError("bits must be a string")
        if not bits:
            raise ValueError("bits must not be empty")
        if any(bit not in ("0", "1") for bit in bits):
            raise ValueError("bits must contain only '0' and '1'")
        for bit in bits:
            self.trigger(bit)
        return self.remainder

    def calculate_remainder(self, bits: str) -> int:
        """Stateless convenience API: reset, consume ``bits``, return remainder."""
        self.reset()
        return self.feed_bits(bits)

    @property
    def remainder(self) -> int:
        """Remainder represented by the current state."""
        return int(self.state[1])


class TrafficLightMachine(StateMachine):
    """A safety-first traffic-light controller with an emergency pre-emption.

    The normal cycle is ``red -> green -> yellow -> red``. The ``emergency``
    event is accepted from any state and always transitions to ``red``; this
    is the kind of invariant that is easier to prove on a small state machine
    than in ad-hoc branching code.
    """

    def __init__(self) -> None:
        super().__init__("red")
        self.add_transition("red", "next", "green")
        self.add_transition("green", "next", "yellow")
        self.add_transition("yellow", "next", "red")
        for state in ("red", "green", "yellow"):
            self.add_transition(state, "emergency", "red")

    def advance(self) -> str:
        """Advance the normal cycle and return the new state."""
        return self.trigger("next").target

    def emergency_stop(self) -> str:
        """Immediately return to red."""
        return self.trigger("emergency").target


class LockMachine(StateMachine):
    """A guarded example: the lock opens only with the correct PIN.

    Guards read from the trigger context. Wrong PINs leave the state
    unchanged because the guard runs before any mutation.
    """

    def __init__(self, pin: str = "2468") -> None:
        if not pin:
            raise InvalidStateError("pin must not be empty")
        self._pin = pin
        super().__init__("locked")
        self.add_transition(
            "locked",
            "unlock",
            "open",
            guard=lambda ctx: ctx.get("pin") == self._pin,
        )
        self.add_transition("open", "lock", "locked")
        self.add_transition("open", "unlock", "open")
