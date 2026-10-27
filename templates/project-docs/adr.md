# ADR {{NNNN}} — {{DECISION_TITLE}}

Template use: merge into the target's existing ADR location. Adopt only for a
load-bearing decision costly to rediscover; do not duplicate the same choice in the
lightweight decision log. Replace every `{{MARKER}}` and delete this note.

- Decision owner: {{DECISION_OWNER}}
- Authority: records the decision; acceptance grants no implementation, installation,
  Git, network, credential, deployment, release, or publication permission.
- Evidence boundary: the decision holds only for the dated evidence and receipts it
  cites.
- Maintenance: only the decision owner changes the status; supersede an accepted
  decision rather than silently rewriting it.
- Revisit or retire: apply the revisit and retirement triggers below.
- Status: `{{PROPOSED_FOR_AUTHORIZATION_PROPOSED_WITH_UNPROVED_BLOCKED_ACCEPTED_SUPERSEDED}}`
- Date: {{YYYY_MM_DD}}
- Supersedes: {{ADR_REFERENCE_OR_NONE}}
- Superseded by: {{ADR_REFERENCE_OR_NONE}}
- Evidence brief: `{{DATED_TECHNOLOGY_OR_OPTIONS_RESEARCH_BRIEF}}`
- Six attributed concern receipts: `{{TARGET_OWNED_RECEIPT_PATHS}}`
- Proportional research owners and merge rationale: `{{OWNER_COUNT_AT_LEAST_TWO_WHY_SUFFICIENT_ASSIGNMENTS_AND_SAFE_MERGE_REASON_OR_SEPARATION}}`
- Coordinator orchestration-only, no lane research or implementation: `{{CONFIRMED_OR_NOT_APPLICABLE}}`
- Post-draft challenge receipt: `{{TARGET_OWNED_CHALLENGE_PATH}}`
- Proven-pattern disposition/deviation record: `{{TARGET_OWNED_ADOPTION_RECORD}}`
- Decision mechanism: `{{HARD_GATE_REVIEW_HEURISTIC_CONVENTION}}`

## Context

{{OBSERVED_PROBLEM_CONSTRAINTS_AND_WHY_A_DURABLE_DECISION_IS_REQUIRED}}

## Options considered

| Option | Benefits | Costs/risks | Evidence |
|---|---|---|---|
| {{OPTION}} | {{BENEFITS}} | {{COSTS}} | {{SOURCE_COMMAND_OR_OBSERVATION}} |

## Decision

{{CHOSEN_OPTION_AND_SCOPE}}

For a kickoff technology ADR, state why the chosen language, stack, dependencies,
tooling, and package strategy best fit this objective. Treat the target's cited,
externally identified proven portfolio or small combination as preferred baselines
when they satisfy the need. Reuse is a strong default, not a mandate. Any new stack must justify its objective-specific
benefit against solo-developer diversity, maintenance, learning, dependency, licence,
privacy, security, and operational cost. “Newer” is not evidence.

Applicable portfolio patterns are presumed `ADOPT` or `MERGE INTO EXISTING`. For each
material `CITE ONLY`, `OMIT`, or novel replacement, link the concrete mismatch, dated
primary/official evidence, bounded comparison, recurring tax and failure/recovery
comparison, distinct challenger result, and reversal/revisit trigger. Missing
deviation proof leaves this ADR `PROPOSED_WITH_UNPROVED` or `BLOCKED`.

## Boundary and isolation decision

| Concern | Chosen owner/boundary | Dependency or port direction | Enforcement / proof | Escape or reversal |
|---|---|---|---|---|
| State/component ownership | {{SINGLE_OWNER_AND_SOURCE}} | {{ALLOWED_DIRECTION}} | `{{CHECK_OR_REVIEW}}` | {{WHEN_ISOLATION_IS_NOT_EARNED_OR_REOPENS}} |
| Composition and teardown | `{{COMPOSITION_PATH_AND_OWNER}}` | {{CONSTRUCTION_AND_DISPOSAL_DIRECTION}} | `{{CHECK_OR_OBSERVATION}}` | {{SAFE_RECOMPOSITION_CONDITION}} |
| Pure policy seam | `{{POLICY_PATH_OR_NOT_APPLICABLE}}` | {{INPUT_OUTPUT_BOUNDARY}} | `{{UNIT_OR_COMPONENT_CHECK}}` | {{WHY_OMISSION_IS_SAFE_OR_DELETION_TRIGGER}} |

## Invariants and enforcement

1. {{LOAD_BEARING_INVARIANT}} — owner: `{{SOURCE_OWNER}}`; cheapest check:
   `{{COMMAND_OR_OBSERVATION}}`.
2. {{LOAD_BEARING_INVARIANT}} — owner: `{{SOURCE_OWNER}}`; cheapest check:
   `{{COMMAND_OR_OBSERVATION}}`.

Unavailable external or physical proof: {{UNPROVED_OR_BLOCKED_BOUNDARY}}

## Consequences and recurring cost

- Accepted benefit: {{BENEFIT}}.
- Accepted cost: {{RECURRING_TAX_AND_OWNER}}.
- Compatibility/migration effect: {{EFFECT_OR_NONE}}.

## Cutover, rollback, and reversal

- Current and target owners: {{OLD_AND_NEW_BOUNDARY_OWNERS_OR_NOT_APPLICABLE}}.
- Temporary bridge and owner: `{{PATH_AND_OWNER_OR_NONE}}`.
- Cutover entry condition and parity proof: {{OBSERVABLE_CONDITION_AND_CHECK}}.
- Rollback or forward-recovery boundary: {{SAFE_PATH_AND_AUTHORITY}}.
- Irreversible/external boundary: {{SEPARATE_AUTHORITY_OR_NONE}}.
- Bridge/adapter deletion condition: {{OBSERVABLE_CONDITION_OR_NONE}}.

## Out of scope

- {{EXPLICIT_NON_GOAL}}

## Revisit and retirement triggers

- Revisit when {{OBSERVABLE_CHANGE}}.
- Delete any temporary guard/adapter/pin when {{DELETION_CONDITION}}.
- Re-run current research when {{ECOSYSTEM_SECURITY_MAINTENANCE_OR_OBJECTIVE_TRIGGER}};
  do not silently treat the dated brief as evergreen SOTA.

## Related

- Source/contract: `{{PATH}}`
- Plan/task: `{{PATH_OR_REFERENCE}}`
- Evidence/review: `{{PATH_OR_REFERENCE}}`

For a new project or genuine architecture reset, this ADR is not implementation-ready
until all six named concerns have attributed receipts from the smallest proportional
set of at least two distinct non-coordinator research owners, a distinct non-author
owner has challenged the draft research brief, ADR, and plan, every finding is disposed, and the
decision owner changes status to `ACCEPTED`. This full kickoff is not repeated for
ordinary steady-state work.

Before that decision-owner acceptance, use exactly `PROPOSED_FOR_AUTHORIZATION` when
the evidence package is ready for the authority request, `PROPOSED_WITH_UNPROVED` when
named evidence remains unproved, or `BLOCKED` when the decision cannot safely proceed.
A freshness receipt never changes this ADR's status or accepts it.
