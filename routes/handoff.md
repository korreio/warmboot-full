# Route: routine freshness handoff

A handoff is a common, lightweight state and evidence receipt. Use the current task
artifact when it already carries this information; otherwise write a handoff receipt
with the Sender fields below. A session change, provider change, pause, resume, or
bounded delegation may need a handoff, but none of those events is a coordinator
rotation by itself.

The live user direction, repository instructions, standards, accepted decisions,
active plan, source, configuration, tests, and observed state govern. A handoff points
to those sources; it never replaces or restates them.

## Sender

Record only what the next agent cannot safely recover from the live repository alone:

- the current task and links to its governing live sources;
- the relevant snapshot or exact input digests;
- changed paths and their current holders, plus concurrent or generated state to
  preserve;
- evidence results and dependencies, classified `INHERITED`, `RERUN NOW` (an input
  moved, so re-execute before relying on it), or `UNPROVED`;
- the required review's state, or `NOT REQUIRED` with its scope/risk reason and
  governing task link; this receipt cannot waive stricter target or user rules;
- blockers, unknowns, and the next unresolved outcome.

Do not use a handoff to grant, revoke, or transfer policy, scope, permission, Git or
singleton ownership, topology, review sequence, external authority, or a
provider-specific process. Those come only from current user direction and the live
repository authorities.

## Durable comprehension route

Point the receiver to the changed code files, their language-native top-level
contracts, and exact linked rationale or ADR sections; never replace them with a
transcript summary. Record the writer's complete changed-source assessment and any
risk-ranked pre-existing debt. Do not carry source meaning only in this handoff or
assume the next agent can inspect a prior transcript; the durable source and
target-owned documentation must stand on their own.

## Receiver

1. Re-read the linked live instructions, task/plan, and changed owners.
2. Compare the relevant snapshot and concurrent inputs without absorbing or erasing
   unrelated state.
3. Reclassify only affected evidence. `INHERITED` means inputs still match, not that a
   command was rerun.
4. Continue the next unresolved outcome only within authority that is current outside
   the handoff. Record new blockers or unknowns in the existing task.

Freshness is dependency-based, not age-based. If this event would replace an actual
active top-level coordinator, Git holder, or other scarce-singleton holder, stop and
use the exceptional rotation route instead.
