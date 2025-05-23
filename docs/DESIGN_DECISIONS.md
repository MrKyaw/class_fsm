# Design decisions

Each decision below is written as **context → decision → consequence**, the format used in architecture reviews.

## 1. Keep the original implementations

**Context:** The repository began as two focused exercise solutions.

**Decision:** Preserve them untouched and add a separate, general-purpose package (`fsm_kit`).

**Consequence:** Reviewers can see the original reasoning *and* the evolved engineering. Nothing is hidden by a rewrite, and the old suites keep running as regression tests.

## 2. Reject duplicate `(state, event)` edges

**Context:** Most hand-rolled FSMs silently overwrite transitions when states are registered twice.

**Decision:** `add_transition` raises `ValueError` on duplicates.

**Consequence:** Determinism is guaranteed. A modelling mistake is caught at startup, not in production.

## 3. Guards run before state mutation

**Context:** A common bug is mutating state and then checking whether the transition was allowed.

**Decision:** Evaluate the guard first; only mutate after the action succeeds.

**Consequence:** Failed guards and failing actions leave the machine untouched. This makes retries and compensation logic safe.

## 4. Actions are synchronous callables over an immutable record

**Context:** Side effects need the transition details but must not mutate the record.

**Decision:** Actions receive a frozen `TransitionRecord` containing source, event, target, and a copied context dict.

**Consequence:** Effects are easy to test and cannot corrupt audit data. Async orchestration can wrap actions without changing the core.

## 5. Bounded, immutable history

**Context:** Unbounded logs leak memory in long-running services.

**Decision:** `deque(maxlen=N)` with a configurable limit (default 100) and frozen records.

**Consequence:** Predictable memory, simple auditability, and records safe to hand to loggers or serializers.

## 6. Diagrams generated from the live model

**Context:** Hand-maintained state diagrams go stale immediately.

**Decision:** `export_mermaid` and `export_dot` iterate the actual transition table in sorted order.

**Consequence:** Documentation is always accurate and diffs are stable.

## 7. Zero runtime dependencies

**Context:** A utility package should not drag a dependency tree into every service.

**Decision:** Standard library only; pytest/coverage live in `[dev]`.

**Consequence:** Trivial installation and a small supply-chain surface. The trade-off is a hand-written DOT/Mermaid escaper, which is fully tested.

## 8. 100% branch coverage as a gate

**Context:** Coverage percentage alone is a weak signal, but a *gate* prevents silent regressions.

**Decision:** `fail_under = 100` for the new package.

**Consequence:** Every new branch needs a test. The original packages are measured separately so their historical gaps do not block the build.

## 9. CLI as a first-class surface

**Context:** Reviewers should be able to verify behaviour without writing code.

**Decision:** `python -m fsm_kit` supports direct input, stdin, Mermaid, DOT, and `--version`.

**Consequence:** Fast manual verification and a template for future packaging on PyPI.
