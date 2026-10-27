# Plan: {{OUTCOME}}

Template use: merge into an active plan or task when present. Adopt only when the work
needs a durable executable sequence beyond the current task. The status preamble must
tell a fresh agent where to resume without reading the whole history. Replace every
`{{MARKER}}` and delete this note.

- Plan owner: {{PLAN_OWNER}}
- Authority: sequences work inside granted scope; only the gate states below, set by
  the named authority owner, authorize implementation or package installation.
- Evidence boundary: a package result proves only its recorded evidence; plan prose
  is not proof.
- Maintenance: update the status preamble and affected packages when evidence, scope,
  or authority changes.
- Revisit or retire: supersede when another plan takes over; retire after final
  integration.

Treat this as a living empirical backlog, not waterfall phase authority. Inspect and
adapt: reorder, split, combine, or remove work when evidence changes the best next
step. A phase label neither grants permission nor creates a mandatory sequence. Only
scope/authority, privacy, destructive effects, Git collisions, production/HIL, and
required evidence boundaries are hard stops.

- Status: `{{AWAITING_IMPLEMENTATION_AUTHORIZATION_AWAITING_WITH_UNPROVED_BLOCKED_ACTIVE_REVIEW_COMPLETE_SUPERSEDED}}`
- Snapshot / last reconciled input: {{COMMIT_DIGEST_OR_DATE}}
- Type: {{IMPLEMENTATION_MIGRATION_CORRECTION_RESEARCH}}
- Supersedes / related plan: {{REFERENCE_OR_NONE}}
- New-project/architecture-reset kickoff: `{{REQUIRED_OR_NOT_REQUIRED}}`
- Kickoff applicability evidence: {{NEW_PROJECT_RESET_OR_ACCEPTED_ARCHITECTURE_REFERENCE}}
- Proven-pattern disposition/deviation record: `{{TARGET_OWNED_RECORD_OR_SECTION}}`
- Current stop / next authorized action: {{EXPLICIT_BOUNDARY}}

## Outcome, scope, and non-goals

- Outcome: {{USER_OWNED_RESULT}}
- In scope: {{EXACT_SCOPE}}
- Non-goals: {{EXPLICIT_EXCLUSIONS}}
- External effects authorized: {{NONE_OR_EXACT_EFFECTS}}
- Completion condition: {{OBSERVABLE_ACCEPTANCE_AND_STOP}}
- Source-comprehension rule/owner/community form and exceptions: {{TARGET_RULE_OWNER_BASIS_EXCEPTIONS}}
- Quality-control owner/location or merged-small-project disposition: {{QUALITY_LOOP_OWNER_LOCATION_OR_MERGE}}

## Kickoff applicability and implementation authorization

Set the kickoff field to `REQUIRED` only for a new project or genuine architecture
reset. In that path, exploration and challenge remain
pre-authorization: the ADR is `PROPOSED_FOR_AUTHORIZATION`,
`PROPOSED_WITH_UNPROVED`, or `BLOCKED`; this plan is
`AWAITING_IMPLEMENTATION_AUTHORIZATION`, `AWAITING_WITH_UNPROVED`, or `BLOCKED`; and
both authorization flags are false. Refreshing a stale receipt changes evidence, not
authority. Implementation and package installation remain blocked until all are true:

- all six named exploration concerns have attributed artifacts and receipts from the
  smallest proportional set of at least two distinct non-coordinator research owners,
  and a distinct non-author owner challenged the draft research brief, ADR, and plan
  afterward plus any separately stored disposition rows they reference, and returned
  its own receipt;
- two research owners are a floor, not a target; destructive or high-risk work
  separates architecture/risk/privacy from testing/bootstrap/operability; lower-risk work
  may merge them only when the plan records why merging is safe and the challenger
  explicitly cross-checks the coupled hazards;
- the coordinator only synthesized those inputs and performed no lane research or
  implementation;
- `{{TECHNOLOGY_RESEARCH_BRIEF}}` records dated primary/official evidence and honest
  `UNPROVED`/`BLOCKED` limits;
- `{{TECHNOLOGY_ARCHITECTURE_ADR}}` is accepted by `{{DECISION_OWNER}}`;
- this plan names prerequisites, exact installation/bootstrap steps, native checks,
  ownership, singleton resources, and authorized external effects.
- every material proven pattern is disposed `ADOPT`, `MERGE INTO EXISTING`, `CITE
  ONLY`, or `OMIT`; every non-`ADOPT`/non-`MERGE INTO EXISTING` result has complete
  deviation proof and a disposed distinct challenge.

Set the kickoff field to `NOT REQUIRED` for ordinary implementation, migration,
correction, or research against a currently accepted architecture, including toolkit
adoption that does not reset that architecture. Cite the accepted decision/current
authority above; do not generate six exploration receipts, synthesis drafts, a kickoff
or challenge merely to populate this template.
`NOT REQUIRED` does not authorize work: retain exact task authority and use proportional
steady-state topology, hazard-first evidence, and independent review.

Implementation gate state: `{{BLOCKED_OR_AUTHORIZED_OR_NOT_REQUIRED}}`

Package-installation gate state: `{{BLOCKED_OR_AUTHORIZED_OR_NOT_REQUIRED}}`

Implementation authorized: `{{FALSE_TRUE}}`

Package installation authorized: `{{FALSE_TRUE}}`

For every `REQUIRED` pre-authorization plan status above, both gate states are
`BLOCKED` and both authorization flags are `false`. Only the named decision/authority
owner may later change an applicable gate to `AUTHORIZED` and its matching flag to
`true`; accepting or refreshing a handoff does neither. In a `NOT REQUIRED` plan, set an
out-of-scope gate to `NOT REQUIRED` with its flag `false`; otherwise record the actual
`BLOCKED` or `AUTHORIZED` task authority rather than inferring it from the accepted
architecture.

Incomplete source inspection, target mismatch, current primary evidence, bounded
comparison, recurring tax/failure analysis, challenger disposition, or reversal
trigger for a material deviation also keeps the applicable implementation/install
gate `BLOCKED`.

## Prerequisites and environment

| Requirement | Version/source of truth | Availability check | Owner |
|---|---|---|---|
| {{RUNTIME_OR_SYSTEM_DEPENDENCY}} | `{{VERSION_AND_MANIFEST_PATH}}` | `{{CHECK_COMMAND}}` | {{OWNER}} |

- Package manager/version: `{{PACKAGE_MANAGER_AND_VERSION}}`
- Lockfile path and policy: `{{LOCKFILE_PATH_AND_UPDATE_RULE}}`
- Secrets/private inputs: {{REQUIRED_AND_FORBIDDEN_DATA}}
- Supported local environments: {{OPERATING_SYSTEM_RUNTIME_OR_CONTAINER_BOUNDARY}}

## Install and bootstrap

Run only after the package-installation gate above is `AUTHORIZED`:

```sh
{{EXACT_INSTALL_COMMANDS}}
{{EXACT_BOOTSTRAP_COMMANDS}}
```

If package installation is outside this plan, set that gate to `NOT REQUIRED`, keep its
flag `false`, replace the commands with `NOT APPLICABLE`, and do not install anything.

| Step | Expected result | Verification | Mutation/network effect |
|---|---|---|---|
| {{INSTALL_OR_BOOTSTRAP_STEP}} | {{EXPECTED_RESULT}} | `{{CHECK}}` | {{EFFECT_AND_AUTHORITY}} |

## Cutover, rollback, and recovery

Use this section only when ownership, state, data, entry paths, or external integration
moves. Otherwise record `NOT APPLICABLE` with the inspected reason.

| Boundary | Current owner/path | Target owner/path | Isolation/bridge owner | Cutover entry and parity proof | Abort/rollback or forward recovery | Irreversible authority | Bridge deletion condition |
|---|---|---|---|---|---|---|---|
| {{BOUNDARY}} | `{{CURRENT_PATH}}` — {{OWNER}} | `{{TARGET_PATH}}` — {{OWNER}} | `{{BRIDGE_PATH_OR_NONE}}` — {{OWNER_OR_NONE}} | {{OBSERVABLE_CONDITION_AND_CHECK}} | {{SAFE_PATH_AND_STOP}} | {{SEPARATE_AUTHORITY_OR_NONE}} | {{OBSERVABLE_CONDITION_OR_NONE}} |

During phased isolation, old and new paths do not both own the same state. Name the
single source at every phase and serialize cutover/rollback mutations through its
holder.

## Required context and precedence

1. `{{AGENT_OR_PROJECT_CONTRACT}}`
2. `{{LIVING_OWNER_OR_SYSTEM_MAP_ROWS}}`
3. `{{APPLICABLE_STANDARDS_TESTING_INVARIANTS}}`
4. `{{DECISIONS_OR_PRIOR_EVIDENCE_NEEDED}}`

Current source and executable evidence outrank stale plan prose. Read only the
applicable deeper sections after the status preamble.

## Locked decisions, open decisions, and non-goals

| ID | State | Decision/question | Owner | Evidence or revisit trigger |
|---|---|---|---|---|
| D1 | `LOCKED` | {{DECISION}} | {{OWNER}} | {{EVIDENCE_OR_TRIGGER}} |
| O1 | `OPEN` | {{QUESTION}} | {{OWNER}} | {{INPUT_NEEDED}} |

## Work packages

### {{WP_ID}} — {{BOUNDED_RESULT}}

- State: `{{TODO_ACTIVE_REVIEW_BLOCKED_COMPLETE}}`
- Owner: {{WRITER_OR_COORDINATOR}}
- Depends on: {{PREREQUISITE_OR_NONE}}
- Owned paths/decisions: `{{EXACT_PATHS_OR_DECISIONS}}`
- Read-only/concurrent paths: `{{PATHS_TO_PRESERVE}}`
- Singleton resources and holders: {{RESOURCES_OR_NONE}}
- Hazards: {{HIGHEST_RELEVANT_HAZARDS}}
- Focused evidence: `{{COMMAND_OR_OBSERVATION}}`
- Closing gate: `{{COMMAND_OR_REVIEW}}`
- Required clean rerun state: {{PROCESS_FIXTURE_CACHE_DATABASE_AND_RESULT_PATH_STATE}}
- Success: {{OBSERVABLE_RESULT}}
- Changed-code definition of done: assess every changed human-authored code file and
  reconcile that assessment against the attested candidate source set; ensure immediate
  language-native orientation and applicable local rationale; record exceptions and
  nearby untouched debt before handoff.
- Rollback/recovery: {{SAFE_REVERSAL_OR_STOP}}
- Deletion/cleanup condition: {{CONDITION_OR_NONE}}

## Execution record

| Date/snapshot | Package | Actual result | Evidence and limits | Review verdict | Next stop |
|---|---|---|---|---|---|
| {{DATE_OR_SNAPSHOT}} | {{WP_ID}} | {{RESULT}} | {{EXACT_EVIDENCE_AND_UNPROVED_BOUNDARY}} | `{{CLEAN_FINDING_BLOCKED}}` | {{NEXT_ACTION}} |

Record current results beside their owning package. Do not create a second evidence
database or turn historical command output into current proof.

## Routine handoff / resume receipt

Use the current task or `{{TARGET_OWNED_HANDOFF_OR_FRESHNESS_RECEIPT_PATH}}` for a
substantial pause, delegation, resume, or session/provider change: snapshot and
relevant input identities; changed versus concurrent paths and current holders;
evidence as `INHERITED`, `RERUN NOW`, or `UNPROVED`; blockers/unknowns; invalidation
triggers; next unresolved outcome; and links to current governing sources. It does not
add or transfer policy, scope, permission, ownership, topology, review sequence,
external authority, or provider process. Only an explicitly named replacement of the
actual active coordinator or scarce-singleton holder uses the exceptional rotation
protocol.

The intensive proportional kickoff is mandatory only for a new project or genuine architecture
reset. Toolkit adoption into a currently accepted architecture and ordinary
implementation/migration/correction/research record it `NOT REQUIRED`. Once any
required ADR and applicable plan gates are satisfied, steady-state work uses the
project's proportional topology and does not regenerate kickoff receipts. Independent
review remains proportional to risk on both paths.

## Final integration and retirement

1. Reconcile all owners and preserve unrelated work.
2. Run focused and closing evidence on the final candidate.
3. Obtain the required independent review; candidate/evidence changes reset credit.
   For code changes the non-author reads every changed human-authored code file in full;
   missing, stale, decorative or remote-only explanation is a blocking finding despite
   green tests.
4. Update changelog, defect, map, invariant, standards, decision, and README owners
   only where their contracts changed.
5. Create an exact-path local recovery point only through the named Git holder.
6. Keep publication and external effects separately authorized.
7. Remove temporary artifacts only after their recorded condition is observed.
