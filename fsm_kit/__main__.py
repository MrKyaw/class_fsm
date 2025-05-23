"""Command-line interface for :mod:`fsm_kit`.

Examples:
    python -m fsm_kit 1101
    python -m fsm_kit --mermaid
    echo 1010 | python -m fsm_kit -
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from . import __version__
from .machines import ModThreeMachine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fsm_kit",
        description="Compute a binary number modulo 3 with a finite state machine.",
    )
    parser.add_argument(
        "bits",
        nargs="?",
        help="binary string (use '-' to read from stdin)",
    )
    parser.add_argument("--mermaid", action="store_true", help="print the Mermaid diagram")
    parser.add_argument("--dot", action="store_true", help="print the Graphviz DOT diagram")
    parser.add_argument("--version", action="version", version=f"fsm_kit {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    machine = ModThreeMachine()

    if args.mermaid:
        print(machine.export_mermaid(title="Modulo-3 automaton"))
        return 0
    if args.dot:
        print(machine.export_dot(title="Modulo-3 automaton"))
        return 0

    bits = args.bits
    if bits == "-":
        bits = sys.stdin.read().strip()
    if bits is None:
        print("error: provide a binary string, --mermaid or --dot", file=sys.stderr)
        return 2

    try:
        remainder = machine.calculate_remainder(bits)
    except (TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(remainder)
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised via subprocess in tests
    raise SystemExit(main())
