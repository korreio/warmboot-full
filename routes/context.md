# Route: context and topology

Use this route to decide what to load and who may mutate what. Never copy the whole
repository into a prompt or create standing agent roles.

## Select context

Load, in order, only what changes the decision:

1. the Warmboot core and current task artifact;
2. local instructions governing the exact paths in scope;
3. the smallest source, test, configuration, and history slices that establish current
   behavior;
4. external or provider-specific material only when the task crosses that boundary.

Record deliberate non-loads that could look accidental. Treat summaries as navigation,
not proof. Verify unstable claims against the named snapshot or current authoritative
source.

For implementation or review, load each changed human-authored code file in full and
the target-owned source-comprehension rule. Use local orientation, rationale, and exact
linked ADR sections as navigation; never assume a transcript, prior agent, test name,
or repository-wide ADR supplies a file's missing contract.

## Bounded local Git history inspection

The coordinator is the sole Git mutator and sole holder of checkpoints, refs, config,
Git-mediated worktrees, remotes, and credentials. A bounded worker or reviewer may read
local history only when it changes their assigned decision and their **initial lane
assignment** already fixes the exact absolute local repository, frozen ref/object
identities and allowed ancestry, exact pathspecs, and the exact invocations below.
Never add a relay to supply it. Missing or mismatched attestation is `BLOCKED`; infer
nothing beyond it. It grants no credential, mutation, checkpoint, remote, or
publication authority.

Every invocation sets `GIT_OPTIONAL_LOCKS=0` or `git --no-optional-locks`, plus
`--no-pager`/`--no-ext-diff` where they apply, over attested refs, objects, and
pathspecs only. The current bounded allowlist is:

- `git rev-parse --verify`;
- `git status --short --untracked-files=all`;
- `git --no-pager log`, including `git --no-pager log --follow`;
- `git --no-pager show --no-ext-diff`;
- `git --no-pager blame`.

Record every exact command and result; a similar-looking command is not allowed.
**Every form of `git diff` is excluded**, including `git diff --no-ext-diff`, because
it can rewrite index stat-cache bytes even with optional locks disabled. Compare named
commit and parent blobs with `git show` instead.

No unlisted Git command is allowed. Excluded: config or `-c` override, fetch/pull,
push, remote/network, credential, worktree administration, branch, add, commit, or any
other index/ref/worktree mutation. Preserve unknown dirt; stop on unclear scope, new
locks, or any Git-observable byte change. This standard never admits a new command. A
claim that an allowed invocation leaves bytes unchanged needs that exact invocation
proved against a disposable byte-identical canary or a complete external before/after
`.git`-and-worktree manifest; command names alone are not proof.

Before any authorized mutation the coordinator independently refreshes authoritative
repository state; no `git diff` or byte-mutating probe is byte-preserving evidence. A
worker's result informs the decision, never selects a checkpoint, and never replaces
that refresh.

## Choose topology

Apply the target's stronger native rule first. Identify coupled invariants, mutable
resources, and required evidence, then use the least coordination that preserves safety
and independent review.

- **Single agent:** only for a tiny, mechanical, reversible, low-risk one-hotspot task
  that changes no code. Record why separation adds no decision value and, when
  independent review is omitted, why it is `NOT REQUIRED`. Self-checking is not
  independent review.
- **Writer + independent reviewer:** required for every code change, however small,
  and the default for material work owned by one coupled boundary. Materiality follows
  consequence (cross-component or architecture effects, public APIs, state,
  concurrency, persistence, security, privacy, migration, release, operations, or
  comparable risk), not line count. The coordinator may write unless target policy or
  the selected protocol makes it orchestration-only; a writer never approves its own
  work.
- **Multiple lanes:** only when at least two genuinely independent owner, research, or
  evidence lanes improve coverage, elapsed work, or independence. Use the fewest lanes,
  give each exact scope, allowed operations, expected artifact, proof, and stop
  condition, and keep one writer per coupled invariant or hotspot. If lanes converge,
  stop them and appoint one writer.

Every implementation lane's definition of done includes the target's
source-comprehension rule: assess every changed human-authored code file before handoff
and route the complete set to a non-author reviewer. A lane is not done merely because
its plan and tests are complete.

A bounded lane, reviewers included, delivers its proved results and unfinished items
before its limit. A lane that stops without a report is recovered as a dead lane
(below); none of its work counts until that recovery proves it.

When an orchestration-only coordinator is selected, that protocol persists until the
task changes it: the coordinator assigns, reconciles, decides, and handles unavoidable
integration hotspots, Git, and task state, but performs no owned research,
implementation, experiment, or review, and never quietly takes over such a lane when it
stops. An integration-hotspot exception records why it is unavoidable, the exact bytes,
affected evidence, and independent review before the coordinator edits.

Serialize work that shares a hotspot or scarce resource. Name one holder for each
mutable shared file, Git repository, database, port or service, browser session,
device, credential, and generated output. Read-only lanes may run concurrently. Hidden
parallel work never satisfies a requirement for visible coordination.

## Scope and lane continuity

Put each owner addendum or material scope, acceptance, hazard, assumption,
architecture, interface, or input change into the current task. Compare it against every
lane, evidence dependency, and digest, and classify each `unaffected`, `renew`,
`rerun`, or `stop` before resuming. Preserve matching digest-bound receipts, invalidate
affected proof and review, resolve ownership overlaps, and renew only affected or
uncertain work. A new worker is not an independent reviewer if it inherits or authored
the reviewed judgment or bytes.

A stopped or dead lane records its proved result, unproved remaining outcome, and next
holder; its handoff never transfers ownership or authorship. A dead, timed-out, or
context-exhausted lane is never presumed complete: inspect its materialized residue and
last evidence, preserve proved work, and reassign only the unproved remainder.

At natural milestones, or when the current context can no longer hold the active
decision safely, compact repository state into the task and concise file-based receipts
or a handoff, then continue with a fresh worker or session under the same recorded
ownership. Context or provider change is not rotation. Rotate an owner only through the
rotation route; renew a lane when the same owner receives revised work. Use this
observable condition, not token, time, turn, or fixed-staffing quotas, and resume from
source-linked evidence, not transcript summaries.

## Candidate source-set attestation

Before every source-change handoff, the coordinator freezes the candidate snapshot and
attests the candidate source set: every added, renamed, or modified human-authored code
file, plus recorded generated, vendored, and pure re-export exceptions. Use
target-native status or change evidence; when Git defines the repository, only the
coordinator runs the required Git derivation and records the command, snapshot, and
result.

The writer reconciles its path-by-path assessment against that attestation before
handoff. The non-author reviewer independently reconciles it again and inspects every
resulting path; any mismatch is `FINDING`. A plan or writer-declared list cannot attest
its own completeness.

## Task record

The current task artifact answers, without a second plan:

- What outcome and non-goals are in force?
- Which snapshot and concurrent inputs define current state?
- Who coordinates, who holds Git, and who holds each other scarce resource?
- Who owns each exact path or decision, and where are overlaps serialized?
- Which topology mode is selected, and what event renews or retires each lane?
- What evidence and justified review decision or required independent verdict end the
  task?
- Which external effects are authorized separately?

Split only while that reduces elapsed work or improves independence more than it adds
handoff and merge risk; collapse lanes when it stops being true.
