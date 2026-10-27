# Context lane evidence

- Owner: `context-owner`
- Scope: define the user outcome, constraints, acceptance boundary, and
  non-goals; make no language, stack, or tooling choice.
- Status: `REPORTED / FROZEN` on 2026-07-31.

## Input snapshot

Snapshot `EX-CONTEXT-INPUT-1` captured the example brief before implementation:

- demonstrate an agent-owned documentation package through useful runnable code;
- normalize human-entered labels into deterministic comparison keys;
- remain harmless, offline-capable, provider-neutral, and maintainable by one
  resource-constrained developer;
- do not add a service, database, UI, dashboard, telemetry, design pipeline, or
  deployment; and
- keep original presentation text outside any destructive normalization result.

## Evidence

| Question | Evidence from the brief | Decision use |
|---|---|---|
| Who uses it? | a developer or local tool comparing human labels | require a callable function and simple CLI, not an operated product |
| What outcome matters? | equal-looking compatibility/case/whitespace variants need one stable comparison representation | define one comparison-key behavior owner |
| What must remain distinct? | original labels carry presentation value | comparison output must never be described as preserved display text |
| What proves useful completion? | clean-checkout test/run path plus populated operating documentation | acceptance must cover behavior and agent navigation |
| What is out? | locale collation, transliteration, slugging, persistence, services, UI, telemetry, publication | prevent semantic and operational scope creep |

No external research was needed: this lane owns user intent, and an external
source cannot replace it.

## Receipt

`CONTEXT-01 — ACCEPTED INPUT`: Build only a comparison-key library and thin CLI.
Success is deterministic behavior plus a no-install local run and navigable
project documentation. Preserve display labels elsewhere. The identity of a
future production caller is `UNPROVED` and unnecessary for this example.
