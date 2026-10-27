# Handoff: {{TASK}}

Template use: adopt for a pause, resumption, or change of worker when live state cannot
be recovered cheaply from the task. Merge into the task when it can carry this receipt.
Omit when no state is changing hands. Replace every `{{MARKER}}` and remove this note.

- Record owner: {{SENDER}}
- Authority: a state and evidence receipt only. It never adds or transfers policy,
  scope, permission, Git or resource ownership, topology, review order, provider rules,
  or package, network, credential, deployment, release, or publication rights. The
  receiver re-reads the live repository authorities.
- Evidence boundary: inherited results remain conditional on the named inputs.
- Maintenance: refresh when an input or live authority changes.
- Revisit or retire: supersede after receiver refresh; remove when the live task alone
  is sufficient.

Created: {{TIMESTAMP}}
Live task: {{PATH_OR_LINK}}
Invalidated by: {{STATE_OR_INPUT_CHANGE}}

## State worth carrying

- Next unresolved outcome: {{OUTCOME}}
- Repository state that cannot be recovered from current files alone:
  {{CONCISE_STATE_OR_NONE}}
- Snapshot and exact input digests: {{IDENTITIES}}
- Changed paths and current holders: {{PATHS_AND_NAMES}}
- Authorship identities for changed decisions and bytes: {{AUTHORS}}
- Stopped or dead lane proved result, unproved remainder, and next holder already
  appointed by live authority (or `NOT APPLICABLE`): {{TRIAGE}}
- Concurrent staged, unstaged, untracked, ignored, generated or external inputs:
  {{INPUTS_OR_NONE}}
- Blockers and unknowns: {{ITEMS_OR_NONE}}
- Governing live sources: {{LINKS_ONLY}}

Keep this receipt concise and file-based. Link to live human-readable sources instead
of copying their rules or compressing policy, architecture or rationale into transcript
shorthand. If the repository already makes a fact recoverable, do not duplicate it here.

## Evidence freshness

| Claim | Receiver action | Evidence and result | Inputs and invalidation |
|---|---|---|---|
| {{CLAIM}} | `INHERITED / RERUN NOW / UNPROVED` | {{COMMAND_OR_OBSERVATION}} | {{DEPENDENCIES}} |

- Review decision: `REQUIRED | NOT REQUIRED` —
  {{LIVE_TASK_LINK_AND_SCOPE_RISK_REASON}}
- Independent review (if required): `NOT STARTED | CLEAN | FINDING | BLOCKED`

`NOT REQUIRED` carries the live task's justified decision; it is not a reviewer verdict
or a waiver of stricter target or user rules, and it is never available for a code
change. Candidate inventory and writer assessment remain mandatory for every code
change.

## Source routes

- Coordinator-attested candidate snapshot, source-set derivation and writer
  reconciliation: {{TASK_SECTION_LINK}}
- Complete assessment of every changed human-authored code file: {{TASK_SECTION_LINK}}
- Language-native file contracts and exact rationale or ADR anchors: {{LINKS}}
- Generated, vendored or pure re-export exceptions: {{PATH_REASON_OWNER_OR_NONE}}
- Risk-ranked untouched source-documentation debt and owner:
  {{PATH_PRIORITY_OWNER_OR_NONE}}

These links must let the receiver continue without a prior transcript or agent. Link
the rationale rather than copying it; this receipt does not replace durable local
source contracts.

## Receiver refresh

- Live snapshot and input differences: {{DIFFERENCES_OR_NONE}}
- Reclassified evidence and required actions: {{ACTIONS_AND_REASONS}}
- Next action under current live authority: {{ONE_ACTION_OR_STOP}}

If the receiver is explicitly replacing the actual active coordinator, Git holder, or
another scarce-singleton holder, stop and use the exceptional rotation route. A session
or provider change alone is routine handoff, not rotation. Fresh context does not erase
authorship. This handoff never appoints the next holder; live task or user authority
must already name that owner.
