# Warmboot Full engineering standards

Owner: warmboot maintainer coordinator. These are the repository-specific adoption of
the portable [`engineering-standards.md`](../templates/project-docs/engineering-standards.md)
role. The template teaches targets how to decide; this file governs Warmboot itself.

## Precedence and rule strength

`AGENTS.md`/`CLAUDE.md` discover `WARMBOOT.md`; explicit toolkit maintenance routes to
`MAINTAINING.md`; this file governs implementation quality; the current task/plan
governs authorized scope; accepted ADRs govern durable decisions. Frozen source
examples and populated consumer examples are precedent, never current authority.

- **Hard gate:** scope/authority, one Git/release mutator, the bounded worker-history
  allowlist and `git diff` prohibition,
  immutable selected evidence and scoped read-only source inspection, one holder
  per mutable resource, independent challenge/review where required, immutable release
  identity, no hidden proof promotion and separately authorized publication. An
  explicitly authorized cross-repository remediation exception additionally requires
  current-state preflight, coordinator-chosen evidence, exact repository/path scope, one writer, native proof,
  independent review and coordinator-only Git/publication; it never rewrites frozen
  provenance.
- **Review heuristic:** prefer one owner per component/decision, pure policy separated
  from I/O, explicit ports/dependencies, small files and the cheapest focused proof.
  Deviate when a named constraint makes the simpler shape safer, with reviewer evidence.
- **Convention:** naming, heading and internal layout that do not change ownership or
  behavior. Keep consistency, but never block hazard evidence over style.

An exception records rule class, exact boundary, reason, owner, compensating evidence,
expiry/revisit trigger and independent disposition. “The model knows better” is not
an exception.

## Ownership and topology

The top-level coordinator orchestrates only and alone owns every Git mutation,
checkpoint/stage/commit, ref/configuration change, Git-mediated worktree/worktree-
manager operation, remote/Git-network action, release tag, and repository credential.
When history changes a decision, a worker's initial assignment may attest one exact
local repository, frozen refs/objects and ancestry, pathspecs, and exact commands from
`routes/context.md`. No `git diff`, unlisted Git command, credential, remote,
mutation, or checkpoint authority follows. The coordinator independently refreshes
authoritative status/diff before mutation and does not claim a byte-mutating probe as
read-only. Every shared file, fixture, temporary checkout, source archive, acceptance
target, and report has one writer/holder at a time.

Use one writer by default and a distinct reviewer for every code change
and for other material risk. In ordinary Warmboot bootstrap/maintenance,
changes to architecture, instruction
discovery/precedence, bootstrap ownership, or release boundaries cover all six named
kickoff concerns through the smallest proportional set of at least two distinct
research owners, an orchestration-only coordinator, and a distinct non-author post-draft
challenger. Two research owners are a floor, not a target. Destructive or high-risk
work separates architecture/risk/privacy from testing/bootstrap/operability, or
records why merging is safe and assigns the challenger explicit coupled-hazard
cross-checks.

Routine delegation, pause, resume, or session/provider change may use a digest-bearing
handoff. It carries state and evidence by reference; a mismatch is `STALE`/`RERUN NOW`.
It grants or transfers no policy, scope, permission, Git/resource ownership, topology,
review order, provider process, edit, commit, install, publication, or other external
authority. Current user direction and live repository owners govern.

Exceptional coordinator rotation is only an explicitly named replacement of the
actual active coordinator, Git holder, or scarce-singleton holder. Only that event
requires quiescent freeze, `RELINQUISHED`, independent replacement preflight and
scoped `ACCEPTED`. Session/provider change and disjoint cross-provider work under the
same holder are routine, not rotation.

## Component and decision rigor

Each behavior has one discoverable owner. Keep provider-neutral policy in the core or
route, file-system mechanics in the helper, example behavior in the example, fixture
truth in the fixture, and release observation in the manifest. Dependencies point
toward policy; orchestration/composition owns lifecycle and teardown. Do not let a
template, source sample, manifest or test become a duplicate production rulebook.

The root `*.code-workspace` is target-owned human-and-agent truth, not a helper-managed
byte. Preserve existing workspace/`.vscode/` owners and keep only earned folders,
settings, tasks, launches, and extension recommendations. When a canonical setup,
test, lint, build, run/debug command or project folder changes, update or remove the
matching workspace entry in the same change and prove command/path parity. Never put
secrets, provider policy, inferred authority, package installation, deployment, data
mutation, or speculative commands in the workspace.

A material boundary change needs options, constraints, selected owner, failure and
recovery behavior, migration/cutover, reversal, evidence and deletion/re-evaluation
condition. Record durable decisions as ADRs. During phased isolation, keep one active
owner per behavior, explicit old/new paths, a cutover gate and a rollback condition;
delete the obsolete path after closing proof.

Plans are living empirical backlogs for inspect-and-adapt work, not waterfall phase
authority. Reorder, split, combine, or remove work when evidence changes the best next
step, and keep the current stop/next action visible. Hard stops remain hard only where
scope/authority, privacy, destructive effects, Git collisions, production/HIL, or a
required evidence boundary demands them; do not turn an illustrative phase order into
permission or ceremony.

## Maintainability and human inspectability

This repository treats documentation as part of collaborative engineering, not an
agent-only resumption aid. Names, types, and tests remain essential, but they do not by
themselves preserve the reason, invariant, assumption, trade-off, or safe-use boundary
that a human owner must challenge as systems grow.

- Every human-authored code file gives an immediate language-native orientation. One
  accurate sentence is enough for a simple file. Generated, vendored and purely
  mechanical forwarding/re-export files use recorded provenance/exception rather than
  decorative prose. Warmboot's Python files use module docstrings; its synthetic Java
  fixtures use Javadoc/file comments only to demonstrate a bounded target-native form.
- Consequential algorithms and boundaries carry adjacent operative rationale for units,
  coordinate/projection assumptions, numerical limits, interval/set behavior,
  concurrency, caching, idempotency, retries/circuits, persistence, privacy and
  failure/recovery behavior. Cross-cutting intent may route to an exact ADR/invariant
  section only after source states its local role and contract. Tests, remote ADRs,
  transcripts and agent memory do not substitute.
- Comments and API documentation explain why, constraints, and safe use. Prose that
  restates code, generated filler, stale commentary, and comment/Javadoc count targets
  are review defects, not maintainability evidence.
- Living docs use clear prose, hierarchy, owners and update triggers so a human can
  locate and challenge intent without replaying transcripts. Cryptic token-saving prose
  is rejected. An editable source-controlled diagram format is used only when it
  materially clarifies a relationship, state machine, or data flow, with a text
  alternative, owner and update trigger.
- Small cohesive files and architecture boundaries control context cost. Locally
  calibrated SLOC/file-size/complexity/dependency pressure may trigger review or
  refactoring with a reasoned exception; it is never a universal cap, a quality score,
  or a proxy for comments and tests.
- Formatting, lint, static analysis and architecture checks are selected from the
  actual language, hazards and native project owners. Tool presence or a green count is
  not evidence of usefulness.

For every code change, the coordinator freezes and attests the candidate source set:
every added, renamed or modified human-authored code file, plus recorded generated,
vendored and pure re-export exceptions
([`routes/context.md`](../routes/context.md#candidate-source-set-attestation)).
Every implementation owner assesses every changed human-authored code file and
reconciles that assessment against the attestation before handoff. The independent
non-author reviewer repeats the reconciliation, reads every resulting file in full
([`routes/review.md`](../routes/review.md#source-comprehension-release-gate))
and returns `FINDING` for an omitted file or for missing, stale, decorative or
remote-only explanation regardless of green tests. Existing untouched debt is inventoried and prioritized by consequence;
the change does not silently bless it or require a comment-count retrofit.

The active backlog owns Warmboot Full's current quality-control loop. At material
milestones it assembles evidence for architecture/ownership, source comprehension,
testing and applicable security/privacy/operations, preserves unknowns, and assigns an
owner plus next action/revisit trigger. A human owner or independent non-author
challenges it. Scores/grades are optional views and cannot close their own findings;
automation may gather facts or regression flags, never semantic adequacy.

Existing-consumer upgrade planning uses one agent-owned compact Markdown record. Keep
only the eleven safety-receipt keys, applicable material dispositions and the migration/
rollback/proof/recovery decisions a fresh resumer needs. Immutable release receipts
already bind exact bytes; do not repeat them per row or disposition irrelevant
teaching material. The parser may enforce only that bounded semantic surface and its
fail-closed canaries—never prose layout or an exhaustive schema recreated in Markdown.

## Optional capability admission

The capability-library maintainer owns `templates/capabilities/` and its
manifest. The target's native command and decision owner outrank a card. The
library stays outside the managed helper payload and contains exactly twelve
decision cards, an index and its manifest. Adding a card, executable integration,
auto-selection rule, helper integration, package or live operation is an
architecture change.

Inspect native tooling before adoption. Use the
[disposition definitions](documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit)
for relevant cards. Adoption requires a target owner and native command,
explicit authority, hazard-appropriate evidence, bounded recurring tax and a
deletion or revisit condition. A card grants no Git, package, hosted-CI, scan,
network/API, database, deployment, credential, device, LLM, user-data or
publication authority.

Ordinary use is selective. Exhaustive twelve-card coverage belongs to the
explicit acceptance audit, whose dispositions are reported recommendations.
Never invent a command or broaden authority to make a card fit. Use a
non-writing native mode when the evidence boundary forbids generated output.
Unavailable live proof remains `UNPROVED`. Scanned Python and `bin/warmboot`
never enable `shell` or call `os.system` or `os.popen` directly.

`docs/capability-sources.json` owns local design and inherited-rights evidence.
It binds `docs/capability-design.md` by digest. Validation preserves recursive
duplicate-key rejection, ordered unique card source fields, rights inheritance
and containment beneath one attested non-symlink root. Synthetic restricted
inputs remain rejected. A source reference grants no publication authority.

## Evidence and tests

Map each changed boundary to the focused and closing sets in [`testing.md`](testing.md).
Prove the highest relevant hazard with the cheapest valid evidence. Lower-tier or
inherited evidence never stands in for unavailable native, cold-agent, provider,
privacy, remote or release proof; label the boundary `UNPROVED` or `BLOCKED`.

Regression pins require a reproduced defect, causal owner/recurrence signal,
red-before evidence, explanation of why behavior checks were insufficient, bounded
tax and retirement condition. `BUGFIXES.md` owns the causal history; tests own the
executable recurrence signal. Apply the relationship-sensitive admission rule in
[`routes/evidence.md`](../routes/evidence.md#regression-pins).

Independent review ends in `CLEAN`, `FINDING` or `BLOCKED`. A change after `CLEAN`
expires that verdict for the changed scope. Stop when accepted evidence and review are
met; do not extend work to manufacture certainty or ceremony.

For a substantial code package, one already-required review round uses another model
family than the writer and, when applicable, the preceding reviewer where reachable;
this selects a reviewer, not another round or stop. A natural lane failure falls back
to a fresh-context non-author and is recorded honestly. Rules and contracts assign
duties by role, not platform mechanics; another-platform coordinator rereads each
changed shared semantic unit before completion.

For changed source, `CLEAN` additionally requires the reviewer identity, the complete
changed authored-file inventory, recorded exceptions, and direct source-contract read.

## Proven precedent and novelty

Use `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT`. Applicable inspected precedent and existing Warmboot behavior defaults to adoption/merge. Deviation or a
new stack needs exact source inspection, concrete constraint mismatch, dated primary
or official research, a bounded comparison where possible, solo-maintainer tax and
failure/recovery comparison, distinct challenge, and reversal trigger. Do not force a
mobile, web, hosted or analytics choice where target constraints differ.

## Documentation and release fallout

In the same change, update every authority made inaccurate: root/template standard,
system/invariant map, test contract, ADR/plan, README, changelog, bug ledger, examples,
acceptance, capability manifest/catalog, source lineage and release manifest.
`docs/adoption-disposition.md` decides whether a root lesson is also portable; do not
copy Warmboot-specific paths into the generic template by habit.

Only the coordinator chooses exact reviewed paths for a coherent local checkpoint.
Its message preserves the cause or decision, directly or by a durable reference, and
one useful sentence explains why the evidence and review support that change.
Commit is not push; push is not release; release is not deployment or provider parity.
Follow `docs/release.md` and require explicit remote authority. A commit-contained release
manifest stays `CANDIDATE` and binds one independently frozen include/exclude policy,
one complete regular-file aggregate and exact lineage/privacy receipt bytes. It never
stores a circular resolved commit or claims tag, signature or remote authenticity;
the post-commit external receipt owns those facts.

## One authoritative home per fact

Every operational fact has one owner. Other surfaces link to it, derive from it or
carry an explicit consistency check. Prefer removing duplicate homes to adding more
pins. When duplication is unavoidable, change all dependent surfaces together or
leave the change unaccepted. A stale copy can mislead a new agent even when tests pass.

When evidence cannot choose between safe policies, use a bounded comparison only if
its outcome can change a real decision. Record constraints, cost, failure/recovery,
owner and revisit condition; do not impose an arbitrary universal policy.
