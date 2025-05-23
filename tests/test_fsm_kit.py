"""Test suite for fsm_kit — targets 100% line and branch coverage."""

from __future__ import annotations

import io

import pytest

from fsm_kit import (
    InvalidStateError,
    InvalidTransitionError,
    StateMachine,
    Transition,
    TransitionRecord,
    UnknownEventError,
)
from fsm_kit.__main__ import main
from fsm_kit.machines import LockMachine, ModThreeMachine, TrafficLightMachine


# --------------------------------------------------------------------- model
class TestStateMachineConstruction:
    def test_registers_initial_state(self) -> None:
        machine = StateMachine("idle")
        assert machine.state == "idle"
        assert machine.initial_state == "idle"
        assert machine.states == frozenset({"idle"})
        assert machine.events == frozenset()
        assert machine.history == ()
        assert machine.transitions == ()

    @pytest.mark.parametrize("initial", ["", "   ", None, 3])
    def test_rejects_invalid_initial_state(self, initial: object) -> None:
        with pytest.raises(InvalidStateError):
            StateMachine(initial)  # type: ignore[arg-type]

    @pytest.mark.parametrize("limit", [0, -1])
    def test_rejects_non_positive_history_limit(self, limit: int) -> None:
        with pytest.raises(ValueError):
            StateMachine("idle", history_limit=limit)

    @pytest.mark.parametrize("limit", ["10", 1.5, True, None])
    def test_rejects_non_integer_history_limit(self, limit: object) -> None:
        with pytest.raises(TypeError):
            StateMachine("idle", history_limit=limit)  # type: ignore[arg-type]

    def test_add_state(self) -> None:
        machine = StateMachine("a")
        machine.add_state("b")
        assert machine.states == frozenset({"a", "b"})

    @pytest.mark.parametrize("state", ["", " ", None])
    def test_add_state_rejects_invalid(self, state: object) -> None:
        with pytest.raises(InvalidStateError):
            StateMachine("a").add_state(state)  # type: ignore[arg-type]


class TestTransitionRegistration:
    def test_add_transition_registers_states_and_events(self) -> None:
        machine = StateMachine("a")
        assert machine.add_transition("a", "go", "b") == "b"
        assert machine.states == frozenset({"a", "b"})
        assert machine.events == frozenset({"go"})
        (transition,) = machine.transitions
        assert transition == Transition("a", "go", "b")

    def test_transition_ordering_is_deterministic(self) -> None:
        machine = StateMachine("a")
        machine.add_transition("b", "x", "a")
        machine.add_transition("a", "y", "b")
        assert [(t.source, t.event) for t in machine.transitions] == [
            ("a", "y"),
            ("b", "x"),
        ]

    @pytest.mark.parametrize(
        "source,event,target",
        [("", "go", "b"), ("a", "", "b"), ("a", "go", ""), (" ", "go", "b")],
    )
    def test_rejects_empty_transition_fields(
        self, source: str, event: str, target: str
    ) -> None:
        with pytest.raises(InvalidStateError):
            StateMachine("a").add_transition(source, event, target)

    def test_rejects_duplicate_state_event_pair(self) -> None:
        machine = StateMachine("a")
        machine.add_transition("a", "go", "b")
        with pytest.raises(ValueError, match="duplicate transition"):
            machine.add_transition("a", "go", "c")

    def test_rejects_non_callable_guard_and_action(self) -> None:
        machine = StateMachine("a")
        with pytest.raises(TypeError, match="guard"):
            machine.add_transition("a", "go", "b", guard="nope")  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="action"):
            machine.add_transition("a", "go", "b", action="nope")  # type: ignore[arg-type]

    def test_transition_dataclass_validation(self) -> None:
        with pytest.raises(InvalidStateError):
            Transition("a", "", "b")


class TestRuntime:
    def test_trigger_updates_state_and_records_history(self) -> None:
        machine = StateMachine("a")
        machine.add_transition("a", "go", "b")
        record = machine.trigger("go", {"user": "ada"})

        assert record == TransitionRecord("a", "go", "b", {"user": "ada"})
        assert record.as_dict() == {
            "source": "a",
            "event": "go",
            "target": "b",
            "context": {"user": "ada"},
        }
        assert machine.state == "b"
        assert machine.history == (record,)

    def test_trigger_without_context_records_empty_mapping(self) -> None:
        machine = StateMachine("a")
        machine.add_transition("a", "go", "b")
        assert machine.trigger("go").context == {}

    def test_can_trigger(self) -> None:
        machine = StateMachine("a")
        machine.add_transition("a", "go", "b", guard=lambda ctx: ctx.get("ok") is True)
        assert machine.can_trigger("go", {"ok": True}) is True
        assert machine.can_trigger("go", {"ok": False}) is False
        assert machine.can_trigger("missing") is False

    def test_unknown_event(self) -> None:
        with pytest.raises(UnknownEventError, match="unknown event"):
            StateMachine("a").trigger("nope")

    def test_invalid_transition_for_known_event(self) -> None:
        machine = StateMachine("c")
        machine.add_transition("a", "go", "b")
        with pytest.raises(InvalidTransitionError, match="no transition"):
            machine.trigger("go")

    def test_guard_rejection_leaves_state_untouched(self) -> None:
        machine = StateMachine("locked")
        machine.add_transition(
            "locked", "unlock", "open", guard=lambda ctx: ctx.get("pin") == "1"
        )
        with pytest.raises(InvalidTransitionError, match="guard rejected"):
            machine.trigger("unlock", {"pin": "0"})
        assert machine.state == "locked"
        assert machine.history == ()

    def test_action_runs_before_state_mutation_and_can_fail(self) -> None:
        observed: list[tuple[str, str]] = []
        machine = StateMachine("a")

        def action(record: TransitionRecord) -> None:
            observed.append((record.source, machine.state))

        machine.add_transition("a", "go", "b", action=action)
        machine.trigger("go")
        assert observed == [("a", "a")]
        assert machine.state == "b"

        def explode(record: TransitionRecord) -> None:
            raise RuntimeError("boom")

        failing = StateMachine("a")
        failing.add_transition("a", "go", "b", action=explode)
        with pytest.raises(RuntimeError, match="boom"):
            failing.trigger("go")
        assert failing.state == "a"
        assert failing.history == ()

    def test_reset_preserves_history(self) -> None:
        machine = StateMachine("a")
        machine.add_transition("a", "go", "b")
        machine.trigger("go")
        machine.reset()
        assert machine.state == "a"
        assert len(machine.history) == 1

    def test_history_is_bounded(self) -> None:
        machine = StateMachine("a", history_limit=2)
        machine.add_transition("a", "loop", "a")
        for _ in range(5):
            machine.trigger("loop")
        assert len(machine.history) == 2

    def test_replay(self) -> None:
        machine = StateMachine("a")
        machine.add_transition("a", "go", "b")
        machine.add_transition("b", "back", "a")
        records = machine.replay(["go", "back"])
        assert [r.target for r in records] == ["b", "a"]
        assert machine.state == "a"


class TestExports:
    def build(self) -> StateMachine:
        machine = StateMachine("red light")
        machine.add_transition("red light", "go", "green:light", guard=lambda ctx: True)
        machine.add_transition("green:light", "stop", "red light", action=lambda r: None)
        machine.add_state("off")
        return machine

    def test_mermaid_without_title(self) -> None:
        diagram = self.build().export_mermaid()
        assert diagram.startswith("stateDiagram-v2")
        assert "[*] --> red_light" in diagram
        assert "red_light --> green_light: go [guard]" in diagram
        assert "green_light --> red_light: stop / action" in diagram

    def test_mermaid_with_title_escaping(self) -> None:
        diagram = StateMachine("a").export_mermaid(title="My: machine\nv2")
        assert "title: My - machine v2" in diagram

    def test_mermaid_state_id_fallback(self) -> None:
        diagram = StateMachine("!").export_mermaid()
        assert "[*] --> _" in diagram

    def test_dot_without_title(self) -> None:
        dot = self.build().export_dot()
        assert dot.startswith("digraph fsm {")
        assert '"red light" -> "green:light" [label="go [guard]"];' in dot
        assert '"green:light" -> "red light" [label="stop / action"];' in dot
        assert dot.rstrip().endswith("}")

    def test_dot_with_title_and_escaping(self) -> None:
        dot = StateMachine("a").export_dot(title='A "quoted" \\ title\nline')
        assert 'label="A \\"quoted\\" \\\\ title\\nline";' in dot

    def test_dot_escapes_transition_labels(self) -> None:
        machine = StateMachine("a")
        machine.add_transition("a", 'say "hi"\\\n', "b")
        assert '[label="say \\"hi\\"\\\\\\n"]' in machine.export_dot()


# ------------------------------------------------------------------- machines
class TestModThree:
    @pytest.mark.parametrize("value", range(0, 512))
    def test_matches_python_modulo(self, value: int) -> None:
        bits = bin(value)[2:]
        assert ModThreeMachine().calculate_remainder(bits) == value % 3

    def test_feed_bit_and_remainder(self) -> None:
        machine = ModThreeMachine()
        assert machine.feed_bit("1") == 1
        assert machine.feed_bit("1") == 0
        assert machine.remainder == 0

    @pytest.mark.parametrize("bit", ["2", "", "ab"])
    def test_feed_bit_rejects_invalid(self, bit: str) -> None:
        with pytest.raises(ValueError, match="bit must be"):
            ModThreeMachine().feed_bit(bit)

    @pytest.mark.parametrize("bits", ["", "102", "abc", " ", "0b1"])
    def test_feed_bits_rejects_invalid(self, bits: str) -> None:
        with pytest.raises(ValueError):
            ModThreeMachine().feed_bits(bits)

    def test_feed_bits_rejects_non_string(self) -> None:
        with pytest.raises(TypeError):
            ModThreeMachine().feed_bits(101)  # type: ignore[arg-type]

    def test_leading_zeros(self) -> None:
        assert ModThreeMachine().calculate_remainder("0000") == 0
        assert ModThreeMachine().calculate_remainder("001") == 1

    def test_large_input_is_streamed(self) -> None:
        bits = "1" + "0" * 500
        assert ModThreeMachine().calculate_remainder(bits) == pow(2, 500, 3)


class TestTrafficLight:
    def test_normal_cycle(self) -> None:
        machine = TrafficLightMachine()
        assert [machine.advance() for _ in range(4)] == [
            "green",
            "yellow",
            "red",
            "green",
        ]

    @pytest.mark.parametrize("start", ["red", "green", "yellow"])
    def test_emergency_from_every_state(self, start: str) -> None:
        machine = TrafficLightMachine()
        while machine.state != start:
            machine.advance()
        assert machine.emergency_stop() == "red"
        assert machine.state == "red"


class TestLock:
    def test_unlock_requires_correct_pin(self) -> None:
        machine = LockMachine("2468")
        assert machine.can_trigger("unlock", {"pin": "0000"}) is False
        assert machine.can_trigger("unlock", {"pin": "2468"}) is True
        machine.trigger("unlock", {"pin": "2468"})
        assert machine.state == "open"
        machine.trigger("unlock", {"pin": "2468"})
        assert machine.state == "open"
        machine.trigger("lock")
        assert machine.state == "locked"

    def test_empty_pin_rejected(self) -> None:
        with pytest.raises(InvalidStateError):
            LockMachine("")


# ------------------------------------------------------------------------ CLI
class TestCli:
    def test_prints_remainder(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert main(["1101"]) == 0
        assert capsys.readouterr().out == "1\n"

    def test_reads_stdin(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        monkeypatch.setattr("sys.stdin", io.StringIO("1010\n"))
        assert main(["-"]) == 0
        assert capsys.readouterr().out == "1\n"

    def test_mermaid(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert main(["--mermaid"]) == 0
        assert "stateDiagram-v2" in capsys.readouterr().out

    def test_dot(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert main(["--dot"]) == 0
        assert "digraph fsm" in capsys.readouterr().out

    def test_missing_argument(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert main([]) == 2
        assert "error:" in capsys.readouterr().err

    def test_invalid_input(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert main(["102"]) == 2
        assert "error:" in capsys.readouterr().err

    def test_version(self, capsys: pytest.CaptureFixture[str]) -> None:
        with pytest.raises(SystemExit) as exc:
            main(["--version"])
        assert exc.value.code == 0
        assert "fsm_kit" in capsys.readouterr().out
