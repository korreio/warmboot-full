# Behavioral invariants and ownership

> **EXAMPLE ONLY.** This project has no runtime state machine. This small living
> ledger exists because three behavioral contracts cross code, CLI, and
> documentation boundaries. It deliberately contains no invented transitions,
> retries, persistence, teardown, or migration bridge.

- Owner: `example-coordinator` while the example is maintained
- Last verified: local source/tests on 2026-07-31; Python 3.14.2 evidence recorded
  in [`TASK.md`](../TASK.md)
- Implementation authority: source and executable tests outrank this explanation

## Current invariants

| Boundary | Single owner/source | Invariant | Consumers / allowed direction | Failure behavior | Cheapest evidence | Update trigger |
|---|---|---|---|---|---|---|
| Comparison-key policy | `normalize_label` in [`core.py`](../src/label_normalizer/core.py) | NFKC compatibility normalization, Unicode-whitespace collapse to ASCII spaces, then case folding; result is destructive comparison text, never preserved display text | `__init__.py` exports and CLI import the core; callers depend inward on this function and retain display values themselves | Non-string input raises exactly `TypeError("value must be str")`; no I/O or partial side effect | `python3 -m unittest tests.test_core -v` | Semantics, type boundary, Unicode order, or owner moves |
| Command-line adapter | `main` in [`__main__.py`](../src/label_normalizer/__main__.py) | One output line is emitted for each input argument, in input order; the adapter never reimplements normalization | CLI depends on the core; core never imports CLI/process concerns | Argument errors belong to `argparse`; normalization failures propagate before that item is printed | `python3 -m unittest tests.test_cli -v` | Parsing, output cardinality/order, exit behavior, or dependency direction changes |
| Runtime/package boundary | [`pyproject.toml`](../pyproject.toml) plus imports under `src/` | Runtime dependency list stays empty; required acceptance runs from source without installation or network access | Optional console entry points compose the same CLI; packaging never becomes a second behavior owner | Missing interpreter is `BLOCKED`; missing optional build backend leaves install `UNPROVED`, not permission to download | full suite + metadata/import inspection | Runtime dependency, package manager, build backend, or required-install boundary changes |

## Composition and lifecycle

- Pure policy seam: `label_normalizer.core.normalize_label`.
- Public library port: `label_normalizer.normalize_label` re-exports the same owner.
- Process composition entry: `label_normalizer.__main__:main` constructs only the
  argument parser and calls the pure policy owner.
- Startup/teardown: `NOT APPLICABLE`; there is no long-lived resource, background
  task, subscription, connection, or mutable singleton.
- Persistence/offline/restart: no state is persisted; each call is independent and
  offline. Process restart changes nothing except the Python/Unicode runtime version.
- Alternate/default entry parity: module execution and optional console entry both
  reach `main`; module path is tested, installed entry execution is `UNPROVED`.
- Temporary bridge, dual owner, cutover, rollback: `NONE`; create a migration plan
  only after two real paths must coexist.

## Hazards and proof limits

| Hazard | Owned response | Evidence / limit |
|---|---|---|
| Caller overwrites original display text with the key | Caller must retain display text; README/ADR/function docs name the destructive boundary | Behavior tests prove transformation only; causal documentation correction is in [`BUGFIXES.md`](../BUGFIXES.md) |
| Interpreter/Unicode upgrade changes serialized keys | No cross-version stability promise; reopen ADR before treating keys as durable persisted identifiers | Only Python 3.14.2 ran; Python 3.11 and cross-version parity are `UNPROVED` |
| CLI drifts from library | Adapter imports one owner and CLI subprocess asserts cardinality/order/output | Optional installed console entry is `UNPROVED` |

## State-machine and regression-pin admission

Do not add a transition table while calls are independent and stateless. Add or
supersede this ledger only when a real state owner, event, retry, reset, offline
lifecycle, or teardown boundary appears.

Do not add a source/wiring pin while behavior tests observe the recurrence. A future
pin requires an observed red-before recurrence, named owner and signal, an explanation
of why behavior tests cannot see it, recurring cost, and a deletion condition. The
current disposition is `OMIT`, not an empty placeholder.
