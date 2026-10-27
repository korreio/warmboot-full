# Label Normalizer — adopted documentation example

> **EXAMPLE ONLY.** This is a harmless, fully populated example of a project
> after adopting Warmboot Full. Copy its document shapes, not its technology
> choice or recorded evidence. Receipts and agent-team records are synthetic
> teaching inputs, not proof of historical live orchestration or current checks.

`label-normalizer` turns human-entered text into a stable comparison key. It
normalizes Unicode compatibility forms, collapses whitespace, and applies
Unicode-aware case folding. The output is intentionally destructive and must not
replace the original display label.

## Quick start

Prerequisite: Python 3.11 or newer.

Run from the project root without installing anything:

```sh
python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m label_normalizer "  Warm   BOOT  "
```

Optional isolated editable install:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --no-deps -e .
label-normalize "  Warm   BOOT  "
```

The expected CLI output is `warm boot`. Editable installation uses the declared
`setuptools>=68` build backend. If it is not already available, `pip` may require
authorized package-index access; the no-install path above remains the required
offline bootstrap. An agent never silently installs global prerequisites.

## Documentation routes

| Need | Start here |
|---|---|
| agent operating rules | [`AGENTS.md`](AGENTS.md) |
| current objective and evidence | [`TASK.md`](TASK.md) |
| retained and deliberately absent documentation roles | [`ROLE-INDEX.md`](ROLE-INDEX.md) |
| ownership or symptom routing | [`docs/system-map.md`](docs/system-map.md) |
| behavioral invariants and single owners | [`docs/invariants.md`](docs/invariants.md) |
| engineering rules and review judgment | [`docs/engineering-standards.md`](docs/engineering-standards.md) |
| test commands and confidence limits | [`docs/testing.md`](docs/testing.md) |
| document taxonomy and lifecycle | [`docs/documentation-guide.md`](docs/documentation-guide.md) |
| proven-pattern adoption/deviation evidence | [`docs/adoption-disposition.md`](docs/adoption-disposition.md) |
| kickoff-only discovery owner artifacts | [`docs/exploration/README.md`](docs/exploration/README.md) |
| dated technology/options evidence | [`docs/studies/2026-07-31-technology-options.md`](docs/studies/2026-07-31-technology-options.md) |
| technology decision | [`docs/adr/0001-python-standard-library-core.md`](docs/adr/0001-python-standard-library-core.md) |
| kickoff exploration and build record | [`docs/plans/kickoff-plan.md`](docs/plans/kickoff-plan.md) |
| independent challenge | [`docs/reviews/kickoff-challenge.md`](docs/reviews/kickoff-challenge.md) |
| pre-challenge and fresh-resumer recovery receipts | [`docs/reviews/kickoff-pre-challenge-receipt.md`](docs/reviews/kickoff-pre-challenge-receipt.md), [`docs/reviews/kickoff-recovery-receipt.md`](docs/reviews/kickoff-recovery-receipt.md) |
| release history | [`CHANGELOG.md`](CHANGELOG.md) |
| resolved defects and corrections | [`BUGFIXES.md`](BUGFIXES.md) |

## Architecture

- `src/label_normalizer/core.py` owns the pure normalization rule.
- `src/label_normalizer/__main__.py` is a thin command-line adapter.
- `tests/` proves behavior and the command-line wiring.
- `pyproject.toml` owns package metadata and the console entry point.
- `label-normalizer.code-workspace` offers Visual Studio Code the same no-install
  closing and compile commands; it creates no new build authority.

Open any human-authored code file to learn its role from the first module docstring.
The consequential normalization function explains its transformation order locally and
links the exact ADR section for deeper rationale; tests do not replace that source entry.

There is no database, network, background lifecycle, mutable global state, or
third-party runtime dependency. A small
[`behavioral-invariant ledger`](docs/invariants.md) records only cross-surface
comparison-key, adapter, and package boundaries. It explicitly omits runtime state
transitions, component migration, rollback, and source pins because no real surface
earns them.

The teaching scenario assigns six discovery owners and a separate challenger after
coordinator synthesis. Its stack comparison uses illustrative service/application
shapes. Real targets should consider proven patterns when applicable; reuse must fit
the objective and justify its upkeep.
The dated study demonstrates that decision process without claiming a live team.

In the scenario, immediately before challenge the coordinator freezes separate SHA-256 identities
for the draft brief, ADR, and plan. Challenge reconciliation invalidated the old
receipt; a distinct fresh resumer marked each claim `STALE` and `RERUN NOW`, reloaded
the changed artifacts, and recorded current digests while the ADR remained proposed,
the plan awaited authorization, and both flags remained false. ADR acceptance and the
explicit implementation/installation gates happened only afterward.

## Scope

The package produces comparison keys only. It does not transliterate languages,
strip punctuation, generate URL slugs, preserve display typography, or promise
locale-specific collation.

The kickoff also rejected empty subtree instructions, operational runbooks,
external-service/telemetry/deployment documents, state-machine/migration machinery,
and speculative source pins. These are evidence-backed omissions in the role index
and adoption record, not missing template work.
