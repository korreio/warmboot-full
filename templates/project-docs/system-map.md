# System map

Template use: merge into an existing architecture or ownership map when one exists.
Adopt when stable boundaries are hard to find from source. For a small coded project,
merge the proportional map into its root README rather than omitting the ownership
route or creating a separate document. List stable boundaries only. Replace every
`{{MARKER}}` and delete this note.

- Map owner: {{OWNER}}
- Authority: routes investigation; grants no mutation or external-effect permission.
- Evidence boundary: this map does not prove that current code matches it.
- Maintenance: update when a boundary, owner, dependency direction, lifecycle, or
  entry path changes.
- Revisit or retire: merge into a stronger architecture source or remove when source
  is the clearer map.

Last verified against: {{SNAPSHOT_OR_DATE}}

| System area / boundary | Single owner | Invariant | Authoritative source / public port | Allowed dependency direction | Cheapest valid check | Singleton resource |
|---|---|---|---|---|---|---|
| {{AREA_ONE}} | {{OWNER}} | {{INVARIANT}} | `{{SOURCE_AND_PORT_PATHS}}` | {{ALLOWED_DIRECTION}} | `{{COMMAND_OR_OBSERVATION}}` | {{RESOURCE_OR_NONE}} |
| {{AREA_TWO}} | {{OWNER}} | {{INVARIANT}} | `{{SOURCE_AND_PORT_PATHS}}` | {{ALLOWED_DIRECTION}} | `{{COMMAND_OR_OBSERVATION}}` | {{RESOURCE_OR_NONE}} |

## How to route a task

| Work/task shape | Living owner and minimum context | Cheapest first evidence | Authority/physical limit |
|---|---|---|---|
| {{TASK_SHAPE}} | `{{SOURCE_REFERENCE_AND_DECISION_PATHS}}` | `{{CHECK_OR_OBSERVATION}}` | {{LIMIT}} |

## Where to look first

| Symptom | First owner/path | Common boundary to check | Do not infer |
|---|---|---|---|
| {{SYMPTOM}} | `{{PATH_OR_COMPONENT}}` | {{EVENT_FLOW_OR_RESOURCE}} | {{UNPROVED_EXTERNAL_OR_HIGHER_TIER_CLAIM}} |

## Cross-boundary flows

- {{SOURCE}} → {{DESTINATION}}: {{DATA_OR_CONTROL}}, guarded by {{INVARIANT_AND_CHECK}}.

## Composition, startup, and teardown

- Composition root / construction owner: `{{PATH}}` — {{OWNER}}.
- Startup order: {{ORDER_AND_OBSERVABLE_READY_CONDITION}}.
- Teardown/cancellation order: {{ORDER_AND_OBSERVABLE_COMPLETE_CONDITION}}.
- Alternate/default entry paths: {{PATHS_THAT_MUST_REACH_THE_SAME_OWNER_OR_NOT_APPLICABLE}}.
- Temporary migration/compatibility bridge: `{{PATH_OR_NONE}}`; owner:
  {{OWNER_OR_NONE}}; cutover/rollback/deletion conditions:
  {{OBSERVABLE_CONDITIONS_OR_NOT_APPLICABLE}}.

## Evidence boundary

This map routes investigation; it does not prove that current code matches the map.
Verify the named source and run the applicable native check before relying on a
boundary. Update or remove a row when its owner, invariant, or source moves.

## Current quality-control loop

For a materially complex/multi-component codebase, record the owner and location of the
current assessment here or link its merged plan/quality owner. It periodically assembles
evidence for architecture/ownership, source comprehension, testing, and applicable
security/privacy/operations; unknowns stay explicit and every material weakness has an
owner plus next action/revisit trigger. A human or independent non-author challenges it.
Grades are optional views and never close their own findings. For a tiny project, state
where ordinary plan/review owns this loop instead of adding another file.

## Source-of-truth links

- Technology/architecture ADR: `{{ADR_PATH}}`
- Active plan/task: `{{PLAN_OR_TASK_PATH}}`
- Engineering/testing contract: `{{STANDARDS_AND_TESTING_PATHS}}`
- Stateful invariants: `{{INVARIANTS_PATH_OR_NONE}}`
- Proven-pattern dispositions/deviations: `{{ADOPTION_RECORD_OR_NONE}}`
- Operational procedures: `{{RUNBOOK_PATHS_OR_NONE}}`
