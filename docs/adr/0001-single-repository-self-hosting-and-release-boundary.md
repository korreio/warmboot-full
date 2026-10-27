# ADR 0001: Single-repository self-hosting with immutable consumer releases

- Status: `ACCEPTED`
- Date: 2026-07-31
- Decision owner: user
- Implementation owner: warmboot maintainer coordinator
- Re-evaluate when: one-repository isolation cannot reproduce a defect safely, Git
  identity cannot bind a consumer kit without ambiguity, or a proved provider harness
  difference cannot fit the neutral authority

## Scope

This decision governs Warmboot Full's own maintenance. Warmboot Light is a separately
maintained edition with its own evidence, not a copied documentation tree of this
repository; [current decisions](../decisions.md) records how the two are aligned.

## Context

Warmboot Full needs to improve from its own rules and accumulated history while a
project that adopted an earlier warm path needs a stable basis. A permanent improver
repository or a second copied documentation tree would make two authorities, invite
drift and impose a recurring synchronization/release tax.
Using only moving `main` would make consumer evidence change underneath existing
projects.

## Options

1. **Separate permanent improver repository.** Strong filesystem isolation, but
   duplicates instructions, history, reviews and release ownership.
2. **Parallel maintainer and frozen folders in one repository.** One Git history, but
   duplicates most bytes and requires continuous internal synchronization.
3. **One evolving repository plus temporary clean isolation and immutable releases.**
   Maintain once; use exact temporary checkouts for comparisons; freeze consumers by
   one annotated release tag plus digest manifest, with its resolved full commit as
   the immutable pin.
4. **Let consumers follow `main`.** Lowest release effort, but no reproducible basis or
   honest before/after comparison.

## Decision

Adopt option 3. Expose three routed planes without copying policy: root maintainer
authority, selectively adopted consumer kit, and one annotated release tag plus digest
manifest for each usable release, with the tag's resolved full commit available as the
consumer pin. Use separate temporary clean baseline/candidate checkouts for proof. One
coordinator owns Git/releases. Remote publication remains a separate explicit
authorization.

Architecture, loader, bootstrap and release-boundary changes cover the six named
concerns with the smallest proportional set of at least two distinct non-coordinator
research owners, an orchestration-only coordinator, and a distinct non-author challenger.
Two is a floor, not a target. Destructive or high-risk work separates
architecture/risk/privacy from testing/bootstrap/operability, or records why merging
is safe and assigns explicit challenger cross-checks. Smaller corrections use
proportional topology. Structural dry runs stop before mutation and never masquerade
as live provider proof.

## Consequences

- A fresh maintainer can resume from root authority, ADR/history, current task and
  release evidence without this conversation.
- `main` can evolve while adopted releases remain reproducible.
- Temporary clean checkouts have an owner and cleanup cost, but no permanent second
  truth.
- Each released consumer version pays the bounded cost of a digest manifest, clean
  reproduction and historical retention.
- A release manifest cannot digest itself. The manifest declares the annotated tag;
  the tag resolves the commit containing it, and the release receipt binds tag,
  resolved commit and manifest digest.
- Cross-provider behavior remains `UNPROVED`; self-hosting design alone proves no
  parity. Any current external/provider state is routed through
  `docs/plans/warmboot-build-plan.md` to its owning artifact. Historical handoffs are
  evidence only, never current dependencies or authority.

## Reversal

If reproduced evidence shows temporary checkout isolation is insufficient, first add
the smallest owned isolation mechanism inside this repository. Create a second
repository only after an ADR demonstrates why one authority cannot work, how truths
remain synchronized, who pays the recurring tax, how consumers migrate, and how the
duplicate is later removed.
