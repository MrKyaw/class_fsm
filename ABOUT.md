# About class_fsm

**Tagline:** A production-grade finite-state-machine toolkit that turns implicit control flow into validated, observable, diagrammable models.

## The problem

Business rules are often written as nested conditionals. The result works until someone adds a state, an approval path, or a retry — then nobody can answer basic questions:

- Which transitions are legal from here?
- Can an action fail halfway through a transition?
- What actually happened in production?
- Is the diagram still accurate?

## The approach

`class_fsm` treats a state machine as a small, testable domain model:

1. **Declare** states and labelled transitions.
2. **Guard** transitions with predicates over a context mapping.
3. **Observe** every successful transition through an immutable audit record.
4. **Generate** Mermaid/DOT documentation from the same model.
5. **Prove** behaviour with exhaustive and edge-case tests.

The repository retains two original implementations — a modulo-3 FSM and a classification-threshold optimiser — and adds `fsm_kit`, a general engine that demonstrates how those ideas scale.

## What a reviewer should notice

- Guards execute **before** state mutation, so failed guards/actions leave the machine untouched.
- Duplicate `(state, event)` edges are rejected at registration time.
- History is bounded, immutable, and inspectable.
- Diagrams are derived from the runtime model, not hand-written.
- The modulo-3 machine is checked against Python's `%` for every value in `[0, 512)`.

## Keywords / tags

`finite-state-machine` · `fsm` · `automata` · `deterministic-systems` · `python` · `pytest` · `test-coverage` · `clean-architecture` · `developer-tools` · `mermaid` · `graphviz` · `modulo-3` · `state-management` · `workflow-engine` · `guard-clauses` · `audit-trail` · `cli` · `ci-cd`

## Author

Kyaw Kyaw Oo — [github.com/MrKyaw](https://github.com/MrKyaw) — kyaw.tech@gmail.com
