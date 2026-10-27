# ADR 0001 — Python standard-library core and thin CLI

> **EXAMPLE DECISION.** Accepted on 2026-07-31 for this teaching project. It is
> not a recommendation that Python or this packaging stack is current SOTA for
> an unrelated project. Lane identities, dates and receipts are invented teaching
> records, not evidence of historical orchestration or source retrieval.

- Status: `ACCEPTED`
- Decision owner: `example-coordinator`
- Accepted after evidence refresh: [`WB-EX-RESUME-001`](../reviews/kickoff-recovery-receipt.md)
- Pre-acceptance proposal: [`ADR-0001-RECONCILED-1`](../reviews/work/technology-architecture-adr.md)
- Proven-pattern classification: [`adoption-disposition.md`](../adoption-disposition.md)

## Context

The objective is one deterministic text transformation plus a command-line
adapter. The sample must be provider-neutral, easy to run offline, and free of
recurring runtime-dependency maintenance. It has no service, persistence,
concurrency, UI, or performance workload.

The scenario assigns six independent discovery owners to examine
[`context`](../exploration/context.md),
[`language`](../exploration/language.md),
[`stack/portfolio`](../exploration/stack-portfolio.md),
[`tooling`](../exploration/tooling.md),
[`architecture/risk/privacy`](../exploration/architecture-risk-privacy.md), and
[`testing/bootstrap/package`](../exploration/testing-bootstrap-package.md).
The coordinator traced receipts `CONTEXT-01`, `LANGUAGE-01`, `STACK-01`,
`TOOLING-01`, `ARCH-01`, and `TEST-01` into this decision. A seventh independent
owner challenged the synthesized draft before implementation authorization; all
three findings were disposed before the fresh-resumer recovery receipt and this
separate acceptance. See
the
[`dated technology/options study`](../studies/2026-07-31-technology-options.md),
[`kickoff plan`](../plans/kickoff-plan.md), and
[`challenge record`](../reviews/kickoff-challenge.md).

The study compares invented service and application reference shapes. Neither larger
boundary serves one pure CLI rule; combining them would add interfaces without an
accepted caller. The small Python boundary is an example decision.

## Options considered

### A. Shell pipeline

Smallest initial file count, but Unicode compatibility and case folding would be
platform- and utility-dependent and harder to test consistently.

### B. Python standard library with a pure owner and thin CLI — chosen

Python's official documentation covers `unicodedata.normalize` and
`str.casefold`, the exact semantic operations required. `unittest` provides
deterministic behavior checks. Package metadata exposes an optional console entry
point without adding a runtime dependency.

### C. JavaScript/TypeScript

A possible CLI language, but a Node/tooling boundary adds no benefit for the
accepted CLI-only outcome.

### D. Third-party normalization or CLI framework

Could offer more policies or richer help, but no accepted requirement needs
them. It adds installation, update, security, compatibility, and removal tax
before a real caller exists.

## Decision

- Require Python 3.11 or newer for this example.
- Keep normalization in one pure `normalize_label(str) -> str` owner.
- Keep CLI parsing/printing in a thin adapter.
- Keep runtime dependencies empty.
- Define the result as a comparison key, never preserved display text.
- Make no-install source execution the required bootstrap and acceptance path.
- Treat editable installation, package-index/network access, and publication as
  separate authority-gated actions.
- Preserve one neutral instruction authority, one pure policy owner, focused versus
  closing evidence, causal bug history, and a minimal workspace task entry.
- Do not import mobile/web/API/database/service/deployment boundaries merely because
  they are proven elsewhere. Unearned overlays, runbooks, runtime state machines,
  migration bridges, and source pins remain omitted until a real surface exists.

### Normalization order

Apply NFKC before whitespace collapse because compatibility normalization can change
characters that later participate in whitespace or case handling. Collapse whitespace
before case folding so spacing has one stable owner and case folding remains the last
text transformation. The local function docstring states this operative rule and links
here; this ADR supplies the cross-cutting decision rather than replacing source context.

## Consequences

- A clean checkout runs tests with the standard library.
- Packaging metadata can describe an optional console entry point, but this
  decision does not prove or authorize installation.
- Locale-specific collation, transliteration, slug generation, and display
  preservation are explicit non-goals.
- The project accepts Python's documented Unicode behavior for the tested
  interpreter rather than shipping its own tables.
- Python 3.11 support is declared but remains `UNPROVED` by this example's actual
  Python 3.14.2 run.
- The behavioral-invariant ledger is living; the one-time disposition record freezes
  with this decision instead of creating a permanent compliance review.

## Validation

- Red-first then green full unit suite and compile check.
- CLI subprocess test and direct CLI smoke.
- Markdown link resolution and TOML metadata parse.
- No install smoke: receipt `WB-EX-IMPL-001` authorized an isolated `--no-deps` local
  install but it was not run; network/package-index access remained unauthorized.
- Independent challenge focused on semantic overreach, portfolio fit, evidence
  limits, and authority ambiguity.

## Re-evaluation triggers

Write a superseding ADR when a real requirement needs locale-specific collation,
stable keys across Python/Unicode database upgrades, a non-Python runtime, bulk
throughput evidence, a third-party dependency, or installation as required
acceptance. Refresh only the decision-relevant official sources in the dated
study, state recurring solo-maintainer cost, and name deletion/migration
conditions.
