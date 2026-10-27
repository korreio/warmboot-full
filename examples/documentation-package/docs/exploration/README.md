# Kickoff exploration artifacts

> **EXAMPLE ONLY.** Read this folder for a new-project kickoff, a technology
> re-evaluation, or an audit of the original decision. Ordinary feature work
> should use the matching row in [`../system-map.md`](../system-map.md) and does
> not need these frozen artifacts.

The scenario assigns each discovery question a read-only owner and an evidence
artifact before synthesis. These invented receipts demonstrate concern separation;
they do not establish that a historical six-agent team performed the work.

| Order | Target-owned artifact | Owner | Decision supplied |
|---|---|---|---|
| 1 | [`context.md`](context.md) | `context-owner` | objective, users, constraints, success, non-goals |
| 2 | [`language.md`](language.md) | `language-owner` | language alternatives and semantic fit |
| 3 | [`stack-portfolio.md`](stack-portfolio.md) | `stack-portfolio-owner` | invented reference-shape fit and recurring cost |
| 4 | [`tooling.md`](tooling.md) | `tooling-owner` | local tools, metadata, editor/workspace, maintenance |
| 5 | [`architecture-risk-privacy.md`](architecture-risk-privacy.md) | `architecture-risk-privacy-owner` | ownership, boundaries, hazards, data/privacy |
| 6 | [`testing-bootstrap-package.md`](testing-bootstrap-package.md) | `testing-bootstrap-package-owner` | prerequisites, evidence, bootstrap, install gates |

`example-coordinator` synthesized these six receipts in the
[`technology/options study`](../studies/2026-07-31-technology-options.md). The
separate `post-draft-challenger` then reviewed the exact frozen draft snapshot
linked from [`../reviews/kickoff-challenge.md`](../reviews/kickoff-challenge.md).
Immediately before that review, the coordinator recorded the three individual draft
digests in
[`WB-EX-PRECHALLENGE-001`](../reviews/kickoff-pre-challenge-receipt.md). After finding
disposition changed the working artifacts, distinct `example-fresh-resumer` marked the
old claims `STALE` and `RERUN NOW`, reloaded them, preserved the proposed/awaiting/false
authorization state, and recorded current digests in
[`WB-EX-RESUME-001`](../reviews/kickoff-recovery-receipt.md). Only after that evidence
refresh did the decision owner accept ADR 0001 and issue implementation/install receipt
`WB-EX-IMPL-001`.

These artifacts are frozen teaching inputs, not live evidence or living checklists. Refresh or replace
only the affected lane when a real ADR re-evaluation trigger fires.
