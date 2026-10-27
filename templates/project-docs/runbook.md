# Runbook: {{REPEATABLE_OPERATION}}

Template use: merge into an existing runbook when present. This role is optional:
adopt it only for a real repeatable operational or external procedure whose ordering,
authority, abort, or recovery behavior is costly to rediscover. Omit it for ordinary
development commands already owned by README or testing guidance. Replace every
`{{MARKER}}` and delete this note.

- Procedure owner: {{RUNBOOK_OWNER}}
- Authority: describes the procedure; grants no external effect beyond the exact
  authorized effects recorded below.
- Evidence boundary: each step proves only its recorded observation.
- Maintenance: update when a step, holder, prerequisite, abort condition, or recovery
  path changes.
- Revisit or retire: set the status to `RETIRED` when the procedure is no longer
  performed.
- Status: `{{DRAFT_ACTIVE_BLOCKED_RETIRED}}`
- Applies to: {{SYSTEM_ENVIRONMENT_OR_SCOPE}}
- Last verified snapshot/date: {{SNAPSHOT_OR_DATE}}
- Prerequisites and entry condition: {{REQUIRED_STATE_TOOLS_DATA_AND_PROOF}}
- Singleton and external authority: {{NAMED_HOLDERS_CREDENTIAL_BOUNDARY_AND_EXACT_AUTHORIZED_EFFECTS}}
- Sensitive data boundary: {{FORBIDDEN_VALUES_AND_SAFE_RECORDING_RULE}}

## Ordered procedure and proof

Commands and observations come from current target source. A successful local or dry
run does not prove an unavailable hosted, credentialed, production, or physical step.

| Step | Action | Expected observation / proof | Mutation or external effect | Abort condition | Holder |
|---|---|---|---|---|---|
| {{STEP_NUMBER}} | `{{COMMAND_OR_MANUAL_ACTION}}` | {{EXPECTED_RESULT_AND_EVIDENCE_PATH}} | {{LOCAL_REMOTE_DATA_OR_NONE}} | {{STOP_WITHOUT_GUESSING_WHEN}} | {{RESOURCE_HOLDER}} |

## Abort, rollback, and recovery

- Safe abort point: {{LAST_POINT_WITH_NO_IRREVERSIBLE_EFFECT}}.
- Partial-state detection: `{{CHECK_OR_OBSERVATION}}`.
- Rollback or forward-recovery owner: {{OWNER}}.
- Recovery procedure: {{ORDERED_RECOVERY_OR_NO_SAFE_AUTOMATIC_ROLLBACK}}.
- Irreversible or separately authorized boundary: {{BOUNDARY_AND_AUTHORITY_SOURCE}}.
- Escalate / stop when: {{MISSING_AUTHORITY_CREDENTIAL_INPUT_OR_UNEXPECTED_STATE}}.

Never improvise deletion, overwrite, deployment, publication, credential rotation, or
data mutation beyond the recorded authority. Preserve partial evidence when cleanup
would hide the failure.

## Unavailable proof and sign-off

| Required proof | Result | Why unavailable or insufficient | Consequence / next owner |
|---|---|---|---|
| {{PROOF}} | `{{PASS_FAIL_UNPROVED_BLOCKED}}` | {{LIMIT_OR_NONE}} | {{SAFE_STOP_AND_NEXT_EVIDENCE_OWNER}} |

- Final state observed: {{OBSERVED_STATE_NOT_INTENT}}.
- Procedure result: `{{COMPLETE_PARTIAL_BLOCKED_ABORTED}}`.
- Sign-off owner and evidence: {{OWNER_DATE_SNAPSHOT_AND_REFERENCE}}.
- Follow-up / retirement trigger: {{OWNED_ACTION_OR_WHEN_OPERATION_DISAPPEARS}}.
