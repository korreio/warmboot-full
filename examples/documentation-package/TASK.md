# Current task — example record

> **EXAMPLE ONLY.** This populated record demonstrates what a fresh agent should
> leave. Its receipts, lane identities, dispositions and outputs are illustrative;
> they do not prove a historical agent team or current test results. The toolkit
> coordinator records actual reruns separately for the current candidate.

- Status: `COMPLETE`
- Objective: deliver a dependency-free Python package that converts human labels
  into stable comparison keys and demonstrates the adopted documentation package.
- Coordinator/synthesizer: `example-coordinator`
- Git holder: `example-coordinator`
- Bounded worker/reviewer local Git history inspection: `NOT REQUIRED`; no delegated
  decision in this example depends on repository history
- Mutable-resource holders: `example-coordinator` for package metadata and task
  record; none for external systems
- Publication/deployment/network mutation: `NOT AUTHORIZED`
- Current-SOTA claim: `NONE`

## Scope and constraints

- Owned: this example folder only.
- Runtime: Python standard library only.
- Preserve original display labels outside the normalizer.
- No database, service, dashboard, telemetry, design workflow, hosted CI, or
  provider adapter.
- Source-comprehension owner/form: `example-coordinator`; every human-authored code file
  uses an immediate module docstring, and consequential choices add local rationale plus
  exact deep link where useful. Generated/vendor/mechanical exceptions: `NONE`.
- Current quality-control loop: merged here and in final non-author review because this
  project is tiny; it covers architecture/ownership, source comprehension and tests,
  keeps the limited privacy boundary explicit, and uses no grade.
- `AGENTS.md` is canonical; `CLAUDE.md` is a thin real-file pointer, not a symlink.
- Mature portable roles are populated, while subtree overlay, runbook, services/
  deployments, runtime state/component migration, and source pins are explicitly
  omitted with evidence rather than represented by empty files.

## Seven-lane kickoff receipt

The initial agent remained orchestration-only. Six independent discovery owners
reported before synthesis; a seventh independent owner challenged the draft
after synthesis and before implementation authority was issued.

| Order | Named owner | Receipt |
|---|---|---|
| 1 | `context-owner` | Stable comparison keys are the sole outcome. Display preservation, slugging, transliteration, service operation, and persistence are out. |
| 2 | `language-owner` | Compared shell, Python, and JavaScript/TypeScript. Python's documented Unicode normalization and casefold operations directly express the rule; shell portability is weak for these semantics and the JS/TS runtime adds no accepted benefit here. Current evidence and limits are in the dated study. |
| 3 | `stack-portfolio-owner` | Considered a generic service reference shape, reference application baseline, and a small combination from the invented reference-shape comparison. Both full baselines are oversized for one pure CLI rule; a small Python-only boundary reuses known capability without inheriting service, UI, database, or multi-toolchain tax. |
| 4 | `tooling-owner` | Chose `unittest`, `argparse`, `compileall`, source execution, and editor-agnostic repository files. `pyproject.toml` owns metadata; editable installation is optional and authority-gated. |
| 5 | `architecture-risk-privacy-owner` | One pure behavior owner plus a thin CLI. Primary hazard: a destructive comparison key being mistaken for display text. Inputs are not retained, logged, or transmitted; there is no network or persistence boundary. |
| 6 | `testing-bootstrap-package-owner` | Required red/green full tests, compile check, CLI smoke, links, and metadata parse. The accepted bootstrap does not install packages. Package installation and package-index/network access remain separately gated. |
| 7 | `post-draft-challenger` | Reviewed the three individually hashed drafts in `EX-KICKOFF-DRAFT-1` under receipt `WB-EX-CHALLENGE-001` and returned `FINDING`: clarify display ownership, separate install/network authority, and bound prerequisite/reproducibility claims. |

The coordinator synthesized those receipts into the dated technology/options
study, ADR 0001, acceptance, and the implementation authorization below. It did
not silently merge language, stack/portfolio, or tooling into one lane. Full
target-owned lane evidence is routed from the kickoff-only
[`exploration index`](docs/exploration/README.md). Coordinator and challenge
records are routed through
[`docs/studies/2026-07-31-technology-options.md`](docs/studies/2026-07-31-technology-options.md),
[`docs/plans/kickoff-plan.md`](docs/plans/kickoff-plan.md), and
[`docs/reviews/kickoff-challenge.md`](docs/reviews/kickoff-challenge.md).

## Pre-authorization recovery sequence

1. Immediately before challenge, the coordinator recorded
   [`WB-EX-PRECHALLENGE-001`](docs/reviews/kickoff-pre-challenge-receipt.md) with exact
   individual SHA-256 digests for the draft brief, ADR, and plan. The ADR was
   `PROPOSED_FOR_AUTHORIZATION`, the plan was
   `AWAITING_IMPLEMENTATION_AUTHORIZATION`, and both authorization flags were `false`.
2. `post-draft-challenger` challenged those exact files. The coordinator accepted all
   three findings and reconciled the working artifacts without accepting the ADR or
   changing either false flag.
3. Distinct `example-fresh-resumer` received the old receipt, recomputed the changed
   working-artifact digests, marked every inherited claim `STALE` and `RERUN NOW`,
   reloaded the reconciled artifacts, and emitted
   [`WB-EX-RESUME-001`](docs/reviews/kickoff-recovery-receipt.md) with current digests.
4. Only afterward did decision owner `example-coordinator` separately accept ADR 0001
   and issue the explicit implementation and installation gates below.

## Challenge disposition and implementation authorization

- `F1 ACCEPTED`: define the output as a comparison key everywhere, preserve
  display text outside the package, test Unicode compatibility/casefold cases,
  and list semantic non-goals.
- `F2 ACCEPTED`: distinguish repository-write authority from package
  installation and package-index/network authority.
- `F3 ACCEPTED`: make source execution the required bootstrap; record the actual
  interpreter and keep Python 3.11 plus editable-install reproducibility
  `UNPROVED` until separately run.

Authorization receipt `WB-EX-IMPL-001`, issued after challenge disposition,
`WB-EX-RESUME-001`, and separate ADR acceptance:

| Field | Receipt |
|---|---|
| issuer | `example-coordinator` |
| writer | `example-writer` |
| granted scope | create/update source, tests, metadata, and documentation only inside this example folder; run local Python, link, and metadata checks |
| implementation purpose | build the comparison-key example exactly to accepted ADR 0001 and the acceptance below |
| implementation gate / flag | `AUTHORIZED`; `implementation_authorized=true` |
| package-installation gate / flag | `AUTHORIZED` for an isolated local environment and `--no-deps` install from this checkout; `install_authorized=true`; `NOT RUN` |
| package-index or other network access | `NOT AUTHORIZED` |
| Git, remote, publication, deployment, destructive cleanup | `NOT AUTHORIZED` |
| stop condition | stop on missing prerequisite, path overlap, or need for any excluded effect; report `BLOCKED` or `UNPROVED` |

After the receipt, topology shrank to one writer and one independent read-only
reviewer. The seven-lane kickoff did not become recurring ceremony.

## Acceptance

- A clean checkout with supported Python can run the test suite with one
  standard-library command and no package install.
- `normalize_label("  Warm   BOOT  ") == "warm boot"`.
- Unicode compatibility and case-fold behavior are tested.
- The CLI prints one normalized comparison key per input.
- All local Markdown links resolve.
- The role index and disposition record classify precedent as `ADOPT`, `MERGE INTO
  EXISTING`, `CITE ONLY`, or `OMIT`; each `CITE ONLY` or `OMIT` deviation carries a
  summary reason and revisit condition.
- Standards/testing demonstrate rule strength, one pure owner, focused/closing sets,
  the no-wrapper/raw-runner boundary, pin admission, and honest `UNPROVED`.
- Workspace JSON parses and its tasks mirror the canonical no-install commands.
- Independent challenge is addressed; the current changed-source boundary received a
  bounded non-author `CLEAN` verdict on the frozen pre-closure snapshot.
- The final non-author reviewer reads all three human-authored code files under
  `src/label_normalizer/` in full; tests or the ADR do not substitute. Missing/stale/
  decorative/remote-only explanation is a blocking finding. Untouched source debt:
  `NONE FOUND` in this three-file example.
- Unrun external/provider/platform claims remain explicit.

## Current correction boundary

- Materially changed authored production source:
  `src/label_normalizer/core.py` (module orientation plus normalization rationale and
  the exact `docs/adr/0001-python-standard-library-core.md#normalization-order`
  anchor).
- Related changed operating evidence: this task record, the engineering/testing/system
  map, example README, ADR 0001, and the three routed precedent records.
- Changed-source assessment: the writer inspected `core.py` in full against the adopted
  target rule; the module states its role locally and the consequential operation order
  states the compatibility/casefold/whitespace rationale locally.
- Historical verdict: `example-final-reviewer`'s earlier `CLEAN` remains an accurate
  record for its frozen older bytes, but expired when `core.py` materially changed. It
  is not attributed to this correction.
- Illustrative verdict: `CLEAN` on the example pre-closure snapshot; current changed bytes require fresh review. Reviewer lane
  `example-source-reviewer` read the complete changed-source set;
  raw candidate aggregate
  `3ab633a2d0802b81027554e14edab99609a236f70847f1db9b6b31e27ace9c77`
  over base commit `SYNTHETIC_INPUT`. Green commands did
  not substitute for that semantic review; the reviewer also found the recorded
  deterministic evidence and explicit limitations consistent with the reviewed
  boundary. Durable checkpoint rule: closure bytes are eligible for checkpoint only
  when accompanied by a same-reviewer freshness receipt; the coordinator records and
  attests that external receipt in the checkpoint without editing this file.

## Evidence

| Phase | Command | Result |
|---|---|---|
| before | `python3 -m unittest discover -s tests -v` | `ILLUSTRATIVE: expected red; 2 discovered, 1 failure + 1 import error because owner/entry point were absent` |
| current after | `python3 -m unittest discover -s tests -v` | `ILLUSTRATIVE: 9 passed on Python 3.14.2` |
| current syntax | `python3 -m compileall -q src tests` | `ILLUSTRATIVE: exit 0` |
| current CLI | `PYTHONPATH=src python3 -m label_normalizer "  Warm   BOOT  "` | `ILLUSTRATIVE: exit 0; warm boot` |
| current docs | local Markdown target resolver | `ILLUSTRATIVE: 190 example-local link occurrences resolved` |
| metadata/workspace | `tomllib` + JSON parse and command parity inspection | `ILLUSTRATIVE: pyproject TOML and workspace JSON parsed; closing/compile tasks match canonical commands` |
| install | none | `AUTHORIZED / NOT RUN / UNPROVED`; optional isolated local tier only; no network/index authority |

## Review and limits

- Review verdict: kickoff challenge `FINDING` then reconciled `CLEAN`; distinct
  `example-final-reviewer` returned post-implementation `CLEAN` for an older frozen
  boundary. That verdict is historical and expired for the current material source
  correction. Current pre-closure verdict:
  `example-source-reviewer` `CLEAN` on aggregate
  `3ab633a2d0802b81027554e14edab99609a236f70847f1db9b6b31e27ace9c77`;
  closure-byte checkpoint eligibility is governed by the external-attestation rule
  above.
- Python 3.11 execution: `UNPROVED` (declared floor; actual run used 3.14.2)
- Claude-native replay: `UNPROVED`
- Windows execution: `UNPROVED`
- Editable install/build-backend availability: `UNPROVED`
- Editable local installation: `AUTHORIZED / NOT RUN / UNPROVED`
- Package-index/build-backend download: `NOT AUTHORIZED / NOT RUN`
- No benchmark or general “best language/stack” claim was made.
- Checkpoint rule: the coordinator may checkpoint these closure bytes only with an
  accompanying same-reviewer freshness receipt and must attest that external receipt
  in the checkpoint; no implementation expansion or follow-up file edit is authorized.

## Populated-package closeout

The current source-comprehension correction changes explanation, not source
behavior or dependencies. Independent semantic review is `CLEAN` on the identified
pre-closure snapshot and cannot be replaced by the refreshed command evidence.
