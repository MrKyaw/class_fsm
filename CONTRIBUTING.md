# Contributing

Thanks for taking the time to improve `class_fsm`.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
pytest --cov=fsm_kit --cov-report=term-missing
```

## Quality bar

- All tests pass on Python 3.10–3.12.
- Coverage for `fsm_kit` stays at **100%** (line and branch).
- Public functions have type hints and docstrings.
- New behaviour ships with tests and, when user-visible, a README update.
- No new runtime dependencies without a written rationale.

## Pull requests

1. Fork and branch from `main`.
2. Keep commits focused; explain *why* in the message.
3. Run `make check` before pushing.
4. Describe the behaviour change, the tests added, and any trade-offs.

## Reporting issues

Include the Python version, the machine definition, the event/context sequence, and the expected vs actual state.
