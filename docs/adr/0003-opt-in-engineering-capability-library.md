# ADR 0003: Optional engineering capability library

Status: accepted design; current results come from rerunning the
[command inventory](../acceptance.md#deterministic-command-inventory).

## Context

Projects often need a reminder to assess testing, dependencies, operations or rights.
A large mandatory tool stack would add maintenance cost and compete with native owners.

## Decision

Keep twelve optional decision cards outside the helper payload. A target
inspects native tooling first and records `ADOPT`, `MERGE INTO EXISTING`,
`CITE ONLY` or `OMIT` using the
[disposition definitions](../documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit).
A card grants no live-action, package, Git, network, credential or publication
authority.

[Local design rationale](../capability-design.md) explains the current lessons; its
[catalog](../capability-sources.json) binds exact rationale bytes and inherited rights.
Synthetic restricted sources exercise rights refusal.

## Consequences and safeguards

A target owns adopted material, native commands, evidence, recurring cost and
revisit conditions. Strict duplicate-free JSON,
ordered source fields, card/catalog consistency, rights inheritance and
non-symlink repository containment remain required.

Deterministic tests prove only their local boundaries. Material inventory,
discovery, authority or rights changes also require the
[cold outsider gate](../acceptance.md#optional-capability-cold-outsider-gate).
Two CLEAN receipts bind identical final candidate, target and prompt digests.
The [testing contract](../testing.md) selects proof; the
[active backlog](../plans/warmboot-build-plan.md) routes current work.

Revisit the library when a card no longer improves a decision or when a new capability
or executable integration is proposed. Such expansion is an architecture decision.
