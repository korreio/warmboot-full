# Proposed ADR draft — `ADR-0001-DRAFT-1`

- Status: `PROPOSED_FOR_AUTHORIZATION`
- Decision owner: `example-coordinator`
- Evidence brief: `technology-options-draft-1.md`

## Context and proposed decision

The package needs one deterministic normalization rule and CLI. It has no service,
database, concurrency, UI, or production workload. Portfolio review found the complete
reference service and reference application baselines disproportionate.

Propose Python 3.11 or newer, one pure `normalize_label(str) -> str` owner, a thin
argument/printing adapter, no runtime dependencies, and an optional console entry point
through `pyproject.toml`.

## Proposed validation and consequences

Use unit tests, a CLI subprocess test, compile check, direct CLI smoke, local link
resolution, TOML parsing, and an isolated editable-install smoke. A clean checkout
should run the core path with the standard library. Locale collation, transliteration,
and slug generation are out of scope.

Re-evaluate for a non-Python runtime, persisted cross-version keys, locale collation,
throughput evidence, or a required third-party dependency. This draft is not accepted
and grants no implementation or installation authority.
