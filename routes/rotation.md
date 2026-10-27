# Route: exceptional coordinator rotation

Use this route only when an explicitly named replacement takes over from the actual
active top-level coordinator, Git holder, or another scarce-singleton holder in live
work. Ordinary handoff, session or provider change, context compaction, pause, token
level, elapsed time, or schedule is not rotation. Different providers may work on
disjoint concerns under the same named coordinator and singleton ownership.

## 1. Quiescent freeze

The outgoing holder:

1. stops new work and asks active lanes on the transferred scope to finish or stop at
   an explicit boundary;
2. waits until the transferred paths and singleton resources are quiescent;
3. records the live snapshot, concurrent dirt, owned changes, evidence freshness,
   blockers, and current resource holders;
4. names the proposed replacement and exact scope; and
5. records `RELINQUISHED` and stops coordinating or using the transferred resources.

Do not overlap outgoing and incoming control of the same singleton. `RELINQUISHED`
does not grant the replacement authority; current user and repository authority still
govern.

When the outgoing holder is demonstrably absent and cannot freeze, the coordinator
records the absence, the evidence for it, and the user's direction in place of this
step; the replacement then continues from section 2, the independent replacement
preflight. Nothing the absent holder left is discarded without inspection.

## 2. Independent replacement preflight

The replacement independently re-reads live instructions and verifies:

- no active lane still writes the transferred scope or resources;
- changed, untracked, generated, ignored, and concurrent inputs are accounted for;
- evidence is correctly `INHERITED`, `RERUN NOW`, or `UNPROVED`; and
- the scope, blockers, current authority, and next outcome are coherent.

The replacement records scoped `ACCEPTED`, `REJECTED` (the holder change does not
complete), or `BLOCKED`. Only `ACCEPTED` completes the exceptional holder change; it
does not expand scope or authorize any external effect. Routine later state transfer
uses the handoff route and no rotation ceremony.
