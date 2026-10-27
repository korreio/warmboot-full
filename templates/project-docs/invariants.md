# Invariants and state ownership

Template use: merge into existing subsystem or state references when present. This
role is optional: adopt it only when cross-owner lifecycle/state behavior is hard to
recover from local source and tests. Do not duplicate implementation detail or create
a field catalogue. Replace every `{{MARKER}}` and delete this note.

- Ledger owner: {{INVARIANT_LEDGER_OWNER}}
- Authority: records invariants; grants no mutation or external-effect permission.
- Evidence boundary: a row proves nothing beyond its named evidence check.
- Maintenance: update when a state owner, transition, consumer, or reset behavior
  changes.
- Revisit or retire: merge into owning subsystem references, or remove rows that local
  source and tests now make clear.

Last verified against: {{SNAPSHOT_OR_DATE}}

## Reading rules

- Read every affected row when work crosses events, owners, retries, resets, offline
  behavior, or teardown.
- Owning source and executable tests remain the implementation authority.
- Update a row in the same change only when its owner or semantics move.
- Measurements or external observations carry an as-of date and evidence reference.

## Current invariants

| Boundary/state machine | Single state owner and source | Inputs/events | Allowed transitions or invariant | Consumers / output ports | Reset/teardown/failure behavior | Evidence owner and check | Update trigger |
|---|---|---|---|---|---|---|---|
| {{BOUNDARY_ONE}} | {{OWNER}} — `{{AUTHORITATIVE_STATE_PATH}}` | {{INPUTS_OR_EVENTS}} | {{LOAD_BEARING_BEHAVIOR}} | `{{CONSUMER_OR_PORT_PATHS}}` | {{RESET_RETRY_OR_TEARDOWN}} | {{EVIDENCE_OWNER}} — `{{TEST_OR_OBSERVATION}}` | {{SEMANTIC_CHANGE}} |
| {{BOUNDARY_TWO}} | {{OWNER}} — `{{AUTHORITATIVE_STATE_PATH}}` | {{INPUTS_OR_EVENTS}} | {{LOAD_BEARING_BEHAVIOR}} | `{{CONSUMER_OR_PORT_PATHS}}` | {{RESET_RETRY_OR_TEARDOWN}} | {{EVIDENCE_OWNER}} — `{{TEST_OR_OBSERVATION}}` | {{SEMANTIC_CHANGE}} |

## Transition and intent validity

| From | Event / guard | To | Side effect owner | Re-check before apply | Rejection / recovery |
|---|---|---|---|---|---|
| {{STATE_OR_ANY}} | {{EVENT_AND_GUARD}} | {{NEXT_STATE_OR_UNCHANGED}} | {{OWNER_OR_NONE}} | {{CURRENT_INTENT_VALIDITY_CHECK}} | {{NO_OP_RETRY_RESET_OR_ERROR}} |

State is written by one named owner. Other components observe through named outputs or
ports. Capture intent before asynchronous work and re-check it at success, retry,
error, and apply boundaries when stale completion can violate current state.

## Cross-owner hazards

- {{HAZARD}}: capture validity at {{INTENT_BOUNDARY}}, re-check at
  {{SUCCESS_CATCH_RETRY_OR_APPLY_PATHS}}, and prove with `{{CHECK}}`.

## Composition and lifecycle

- Creation/wiring owner: `{{COMPOSITION_ROOT_OR_FACTORY_PATH}}` — {{OWNER}}.
- Startup ordering invariant: {{ORDER_AND_PROOF}}.
- Teardown/cancellation ordering invariant: {{ORDER_AND_PROOF}}.
- Persistence/offline/restart boundary: {{BEHAVIOR_OR_NOT_APPLICABLE_WITH_REASON}}.
- Temporary dual-path or migration bridge: {{PATH_OWNER_CUTOVER_ROLLBACK_AND_DELETION_OR_NONE}}.

## Known gaps and retirement

- `{{UNPROVED_OR_BLOCKED_GAP}}` — owner: {{OWNER}}; consequence: {{CONSEQUENCE}};
  evidence needed: {{EVIDENCE}}.
- Delete or merge this ledger when {{SOURCE_AND_TESTS_BECOME_ADEQUATE_CONDITION}}.
