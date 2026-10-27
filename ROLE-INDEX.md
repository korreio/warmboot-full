# Maintainer role index

This index routes work on Warmboot Full itself. It is not installed into consumer
projects. [`MAINTAINING.md`](MAINTAINING.md) is the maintainer entry point;
[`WARMBOOT.md`](WARMBOOT.md) remains the shared safety core.

| Question | Authority | Update trigger |
|---|---|---|
| Why does the toolkit exist? | [`WHY.md`](WHY.md) | Objective or non-goal changes |
| How is the toolkit improved? | [`MAINTAINING.md`](MAINTAINING.md) | Maintainer authority, topology, or proof changes |
| Where does a subsystem or document role live? | [`docs/maintainer-system-map.md`](docs/maintainer-system-map.md) | Owner, route, dependency, or lifecycle changes |
| What engineering rules govern this repository? | [`docs/engineering-standards.md`](docs/engineering-standards.md) | Architecture, ownership, evidence or maintenance rules change |
| What source-comprehension rule and current quality-control loop apply? | [`docs/engineering-standards.md`](docs/engineering-standards.md) and the named current task/[backlog](docs/plans/warmboot-build-plan.md) | Language-native source rule, complete changed-source review, quality evidence/unknown/action, or debt priority changes |
| What is the minimum and closing proof? | [`docs/testing.md`](docs/testing.md) | Changed boundary, test command, acceptance or proof limit changes |
| What is this repository called, and which identifiers are fixed? | [`docs/identity.md`](docs/identity.md) | Product, repository, checkout, workspace, compatibility or historical identity changes |
| What human workspace must bootstrap leave? | [`BOOTSTRAP.md`](BOOTSTRAP.md#5-leave-the-required-human-and-agent-workspace); Warmboot Full dogfoods [`warmboot-full.code-workspace`](warmboot-full.code-workspace) | Project folders, canonical commands, workspace ownership, or bootstrap completion changes |
| Which states must always hold? | [`docs/invariants.md`](docs/invariants.md) | Ownership, plane, release, source or provider boundary changes |
| How did Warmboot adopt its own document roles? | [`docs/adoption-disposition.md`](docs/adoption-disposition.md) | Root/template role is adopted, merged, cited, omitted or rehomed |
| What is active now? | [Active backlog](docs/plans/warmboot-build-plan.md) | Scope, gate, evidence or next action changes |
| Why was a durable choice made? | [`docs/decisions.md`](docs/decisions.md) and [`docs/adr/`](docs/adr/) | Material architecture or release choice; supersede, do not rewrite history |
| What user-visible toolkit capability changed? | [`CHANGELOG.md`](CHANGELOG.md) | Same change as an added, changed, deprecated, removed, fixed, or security-relevant capability |
| What reproduced defect must not recur? | [`BUGFIXES.md`](BUGFIXES.md) | Observed defect admitted or retired under the evidence rule |
| How is portfolio knowledge refreshed? | [`docs/source-refresh.md`](docs/source-refresh.md) | Source boundary or refresh evidence changes |
| How is an immutable consumer version frozen? | [`docs/release.md`](docs/release.md) and [`docs/releases/`](docs/releases/) | Release contract, manifest, evidence, or known limitation changes |
| How does an existing consumer evaluate a newer version? | [`UPGRADING.md`](UPGRADING.md), target adoption record, and both immutable release receipts | Upgrade identity, disposition, preservation, migration, rollback or proof changes |
| What evidence is deterministic? | [`docs/acceptance.md`](docs/acceptance.md) and `acceptance/` | Acceptance surface or honest limit changes |

Consumer templates, populated examples and local source catalogues
are inputs to decisions, not maintainer authority. A temporary study, plan, review or
handoff is deleted or archived when its decision has moved into the owning code,
standard, ADR, history or release record and no recovery path still needs it.
