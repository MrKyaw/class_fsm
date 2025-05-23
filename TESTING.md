# Testing

## TL;DR

```bash
python -m pip install -e ".[dev]"
pytest --cov=fsm_kit --cov-report=term-missing
```

**Verified on Python 3.12.8**

```text
588 passed, 17 subtests passed in 0.62s

Name                  Stmts   Miss Branch BrPart  Cover
-------------------------------------------------------
fsm_kit/__init__.py       4      0      0      0   100%
fsm_kit/__main__.py      35      0      8      0   100%
fsm_kit/core.py         152      0     46      0   100%
fsm_kit/machines.py      51      0     16      0   100%
-------------------------------------------------------
TOTAL                   242      0     70      0   100%
```

The `fail_under = 100` setting in `pyproject.toml` turns any coverage regression into a test failure.

## What is covered

### Engine (`tests/test_fsm_kit.py`)

- Construction: invalid initial state, non-integer/non-positive history limits.
- Registration: empty names, duplicate `(state, event)` pairs, non-callable guards/actions, deterministic transition ordering.
- Runtime: unknown events, missing edges, guard rejection, action side effects, action failure atomicity, bounded history, reset, replay.
- Exports: Mermaid/DOT with and without titles, guard/action annotations, escaping of quotes, slashes, newlines, and unusual state names.
- Records: `TransitionRecord` equality, context capture, `as_dict()` JSON shape.

### Bundled machines

| Machine | Tests |
|---|---|
| `ModThreeMachine` | Every integer 0–511 compared with `% 3`; leading zeros; 500-bit streaming input; invalid bits/types. |
| `TrafficLightMachine` | Normal four-step cycle; emergency pre-emption from red, green, and yellow. |
| `LockMachine` | Correct/incorrect PIN, idempotent unlock, relock, empty PIN rejection. |

### CLI

`python -m fsm_kit` — positional input, stdin via `-`, `--mermaid`, `--dot`, missing argument, invalid input, `--version`.

### Original implementations

The pre-existing suites run in the same session:

- `binary_classification_threshold/tests/test_threshold_optimizer.py`
- `finite_state_machine/tests/test_mod_three_fsm.py`

That is why the total test count includes both old and new code.

## Running subsets

```bash
pytest tests/                                  # new engine only
pytest binary_classification_threshold/        # original threshold optimiser
pytest finite_state_machine/                   # original modulo-3 FSM
pytest -k "ModThree"                           # by keyword
```

## CI

`.github/workflows/ci.yml` runs on every push and pull request:

1. Matrix: Python 3.10, 3.11, 3.12.
2. Install package + dev extras.
3. `pytest --cov=fsm_kit --cov-report=xml --cov-report=term-missing`.
4. Upload coverage artifact on Python 3.12.

## Manual verification

```bash
python -m fsm_kit 1101
# 1

python -m fsm_kit --mermaid
# stateDiagram-v2
#     [*] --> r0
#     r0 --> r0: 0
#     ...

python -m fsm_kit 102
# error: bits must contain only '0' and '1'
# exit code 2
```
