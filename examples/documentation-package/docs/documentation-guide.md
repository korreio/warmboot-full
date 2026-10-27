# Documentation guide

> **EXAMPLE ONLY.** This living guide owns document authority and lifecycle after
> bootstrap. [`ROLE-INDEX.md`](../ROLE-INDEX.md) is the completed one-time inventory;
> it does not become a second set of writing rules.

- Guide owner: `example-coordinator`
- Last verified: final local candidate on 2026-07-31

## Authority and precedence

1. User objective and explicit task authority define permitted outcomes/effects.
2. Current source, manifests, configuration, executable tests, and observed runtime
   state prove current behavior.
3. Root `AGENTS.md` is the provider-neutral startup/router; `CLAUDE.md` only points
   to it. There is no subtree overlay because no local distinction earns one.
4. Living owners—system map, invariants, standards, testing, this guide—explain
   current boundaries.
5. Accepted ADR and active `TASK.md`/plan preserve decision and execution state.
6. README, changelog, and causal defect ledger orient and communicate.
7. Dated studies, lane artifacts, receipts, snapshots, and reviews are frozen evidence;
   they never silently override current executable truth.

Correct stale living mirrors in the same change. Preserve accepted/frozen history and
supersede it explicitly; do not rewrite old evidence to look current.

Durable documentation uses complete human-readable prose; token-saving fragments and
agent transcripts are not project knowledge. Keep local why/assumption commentary near
source and route cross-cutting intent to the map, invariants or ADR. An editable source-
controlled diagram is added only when it makes a relationship, state or data flow clearer
than prose, with a useful text alternative, owner and update trigger. This project is
small enough that no diagram currently earns that cost.

## Current role map

| Path | Role/authority | Lifecycle and owner |
|---|---|---|
| `README.md` | human outcome, public semantics, offline start, routes | living; project coordinator |
| `AGENTS.md` / `CLAUDE.md` | neutral agent contract / provider discovery pointer | living; project coordinator; no duplicate policy |
| `TASK.md` | current scope, authority, evidence, review, next step | living while active; replace in place |
| `ROLE-INDEX.md` | completed adoption inventory and absent-role route | frozen with accepted architecture; reopen on genuine reset |
| `docs/system-map.md` | boundary, task, symptom, and owner routing | living; coordinator updates when boundary/owner/entry changes |
| `docs/invariants.md` | cross-surface behavioral contracts and proof limits | living; owner of changed semantic boundary |
| `docs/engineering-standards.md` | rule strengths, architecture/test/change gates | living; coordinator + independent reviewer |
| `docs/testing.md` | canonical commands, focused/closing sets, evidence/pin limits | living; test-contract owner |
| `docs/adoption-disposition.md` | illustrative precedent classification with summary reasons and revisit conditions | frozen with ADR 0001; re-evaluate only on named trigger |
| `docs/exploration/` | six target-owned kickoff inputs/receipts | frozen after coordinator intake |
| `docs/studies/` | dated decision study (synthetic in this example) | frozen; supersede when ADR trigger fires |
| `docs/adr/` | accepted load-bearing decisions | immutable reasoning; supersede with new numbered ADR |
| `docs/plans/` | multi-step mechanics, gates, build evidence | active then frozen on completion/abandonment |
| `docs/reviews/snapshots/` | exact pre-challenge bytes/digests | immutable historical evidence |
| `docs/reviews/work/` | reconciled pre-authorization bytes used by fresh resumer | frozen; accepted truth lives in final study/ADR/plan |
| `docs/reviews/*receipt.md` | handoff/freshness/authority decisions | immutable after receiver records decision |
| `docs/reviews/kickoff-challenge.md` | independent findings, dispositions, bounded verdicts | append a distinct round; substantive changes expire clean credit |
| `CHANGELOG.md` | user-visible behavior/release history only | append for public changes; no implied tag/publication |
| `BUGFIXES.md` | reproduced causal defect and recurrence ownership | retain while lesson changes diagnosis/prevention |
| `label-normalizer.code-workspace` | required target-owned human-and-agent entry mirroring current native commands | living; merge only into an explicitly user-accepted compatible replacement |

## Omitted roles are explicit architecture

No files exist for subtree instructions, operations/runbooks, external services,
deployment/release workflows, component migration, runtime state machines, or
source/wiring regression pins. The summary reasons and revisit conditions live in the
[`role index`](../ROLE-INDEX.md) and
[`adoption record`](adoption-disposition.md). Do not add placeholder headings/files
to make the package appear mature; maturity includes knowing which tax not to pay.

## Same-change triggers

| Change | Required living/frozen fallout |
|---|---|
| public comparison semantics/non-goals | source/tests, README, invariants, changelog; causal bug entry only for a reproduced defect |
| component/owner/dependency/entry path | system map, invariants/standards, affected tests |
| state/event/retry/reset/teardown appears | invariants; consider a real state-machine owner only if local source/tests are insufficient |
| native command, test tier, fixture, or proof meaning | testing, standards if gate strength changes, workspace task if mirrored |
| runtime/language/dependency/package manager | dated official study, disposition, superseding ADR, plan/task, README/testing |
| proven pattern adopted/merged/cited/omitted | adoption record and distinct challenger disposition |
| public release/migration | changelog; tag/version/deploy truth only when those systems exist |
| real defect fixed | BUGFIXES causal record; pin only if admitted under testing rules |
| operational/external procedure accepted | create smallest runbook with prerequisites, abort/recovery, owner, proof, and retirement |
| plan/authority/evidence/review changes | current task/plan/receipt; changed candidate expires old review verdict |

Documentation-only internal restructuring is not a changelog item. Review mechanics
belong in the task/plan/review record. Changelog and BUGFIXES never substitute for one
another: the first says what users see; the second says why a reproduced defect
happened and who prevents recurrence.

## Add, move, supersede, or delete

1. Search for an existing owner and extend it first.
2. Name the reader, decision value, owner, authority, update trigger, recurring cost,
   and retirement condition.
3. Add only content that changes navigation, implementation, proof, operation, or a
   durable decision. No empty template sections.
4. Update inbound routes and same-change owners.
5. Run the local link check and smallest affected native check; record exact result
   and limit in `TASK.md`.
6. Living docs update in place; no `-v2`, `-final`, or silent snapshot series.
7. Accepted ADRs/frozen evidence are superseded, not rewritten. Name the successor.
8. On deletion, preserve unique current facts in a successor or record why the role
   stopped changing a decision.

Use `NNNN-slug.md` for ADRs. Use a date in a study filename only when evidence
freshness changes its meaning. There is no mandatory YAML frontmatter, generated
catalog, documentation database, dashboard, scheduled sweep, or archive ceremony.

## Recurring tax and stop rule

| Surface | Tax paid | Delete/simplify when |
|---|---|---|
| system map / invariants | keep owner/routes synchronized | source/tests make the boundary recoverable without them |
| standards / testing | keep gates and commands truthful | merge if separate navigation adds no value |
| workspace | mirror only current useful commands | an explicitly user-accepted compatible human workspace owns equivalent navigation/command paths |
| changelog / bug ledger | classify public change vs causal defect | target explicitly stops versioning, or successor preserves causal knowledge |
| frozen kickoff evidence | storage/link integrity only; no scheduled refresh | decision no longer relies on it and successor retains necessary provenance |
| review receipt | new verdict after substantive change | freeze each round; never maintain a “still clean” dashboard |

Stop adding documentation when the reader can find the owner, decision, evidence,
authority, and next step without another file. A reproduced findability failure—not
template availability—is the gate for more structure.
