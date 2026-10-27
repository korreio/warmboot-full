# Task: {{OUTCOME}}

Template use: adopt when no current issue, plan, or task records the live outcome and
authority. Merge into an existing artifact when it already owns the work. Omit this
file when that artifact is sufficient. Replace every `{{MARKER}}` and remove this note.

- Record owner: {{TASK_OWNER}}
- Authority: records granted scope; grants no Git, package, network, credential,
  deployment, release, or publication permission.
- Evidence boundary: only commands and observations recorded below count.
- Maintenance: update when scope, snapshot, ownership, blockers, or acceptance changes.
- Revisit or retire: close or archive when acceptance is met; merge if another live
  artifact becomes authoritative.

Status: `READY | ACTIVE | REVIEW | BLOCKED | DONE`
Snapshot: {{COMMIT_DIGEST_OR_DATED_STATE}}

## Outcome and boundary

- Outcome: {{CONCRETE_RESULT}}
- In scope: {{EXACT_PATHS_OR_DECISIONS}}
- Non-goals: {{EXPLICIT_NON_GOALS}}
- Authorized external effects: {{NONE_OR_EXACT_EFFECTS}}
- Acceptance and stop condition: {{OBSERVABLE_CONDITION}}
- Size and risk class and why: {{CLASS_AND_CONSEQUENCE}}
- Architecture kickoff decision (if the toolkit provides one):
  {{NOT_REQUIRED_OR_PLAN_LINK}}

## Ownership

- Coordinator and sole Git and remote operator (if Git is used): {{NAME}}
- Topology decision:
  `SINGLE-AGENT EXCEPTION | WRITER + INDEPENDENT REVIEWER | MULTIPLE INDEPENDENT LANES`
- Single-agent exception reason and exact low-risk, no-code boundary (if used):
  {{REASON_AND_BOUNDARY}}
- Orchestration-only protocol and any recorded hotspot exception (if any):
  {{NONE_OR_PROTOCOL_AND_EXCEPTION_BYTES_REASON_EVIDENCE}}
- Exact path or decision owners: {{OWNERS}}
- Lane outcomes, exact paths, and stop or renew events: {{LANE_CONTRACTS_OR_NONE}}
- Authorship identities and independent reviewers: {{AUTHORS_AND_REVIEWERS}}
- Other scarce or mutable resources and holders: {{RESOURCES_AND_HOLDERS}}
- Concurrent inputs to preserve: {{INPUTS_OR_NONE}}

A recorded coordinator name stays in force across sessions and providers; replacing an
active holder is rotation. Only when no coordinator is recorded here, or the recorded
one is demonstrably absent from this work, and the user's direction grants this agent
the work, does it append itself as coordinator, recording that absence and direction
without overwriting the prior name. A delegated lane never does, and no agent
overwrites another's recorded ownership. Naming an operator identifies who may act; it
does not create authority.

Per the core, the coordinator remains the sole Git mutator and sole checkpoint, remote,
and credential holder. A bounded worker or reviewer reads local history only through
the attested allowlist in `.agent-warmboot/routes/context.md`, fixed in that lane's
initial assignment, with every `git diff` form excluded. Every other scarce or mutable
resource has exactly one named holder.

## Context and hazards

- Governing instructions: {{PATHS}}
- Relevant inputs loaded: {{PATHS_OR_SNAPSHOTS}}
- Deliberate non-loads: {{ITEMS_AND_REASON}}
- Highest hazards: {{HAZARDS}}
- Cheapest valid evidence for each hazard: {{CHECKS_OR_OBSERVATIONS}}
- Documentation impact: {{RATIONALE_API_SYSTEM_MAP_DIAGRAM_OR_NONE_WITH_REASON}}
- Quality-control owner for material multi-component code, or small-project reason:
  {{PATH_AND_OWNER_OR_REASON}}

## Scope and assignment revisions

Record each material change to outcome, acceptance, hazard, assumption, architecture,
interface, digest, lane input, or owner direction here, never in a parallel plan.
Classify every lane and evidence dependency against it before work resumes.

| Revision | Affected lane, evidence, or decision | Action | Kept receipt or remainder | Next holder |
|---|---|---|---|---|
| {{CHANGE}} | {{DEPENDENCY}} | `UNAFFECTED / RENEW / RERUN / STOP` | {{DIGEST_PATH_OR_REMAINDER}} | {{NAME}} |

A stopped or dead lane does not transfer ownership through its handoff. Preserve proved
digest-bound work, reassign the unproved remainder explicitly, and distinguish lane
renewal from coordinator or singleton rotation.

## Work and evidence

| Item | Owner | State | Evidence and limit |
|---|---|---|---|
| {{BOUNDED_ITEM}} | {{NAME}} | `TODO` | {{COMMAND_OBSERVATION_OR_UNPROVED}} |

- Changed paths: {{PATHS_OR_NONE}}
- Evidence run or freshness-checked: {{EXACT_COMMANDS_AND_RESULTS_OR_NONE}}
- Evidence skipped or unavailable: {{SKIPPED_PART_FALLBACK_AND_CONSEQUENCE_OR_NONE}}
- Test quality: {{ORACLE_AND_FIXTURE_INDEPENDENCE_PROPERTIES_SKIPS_AND_TIERS}}
- Digest-bound materialized review target: {{EXACT_REVIEWED_BYTES_AND_DIGEST_OR_NONE}}
- Coordinator-verified delegated or reviewer-supplied claims, each `CONFIRMED`,
  `REFUTED` or `DOWNGRADED` with evidence: {{CLAIMS_OR_NONE}}
- Review decision: `REQUIRED | NOT REQUIRED` — {{REASON_AND_STRICTER_RULE_CHECK}}
- Independent review (if required): `NOT STARTED | CLEAN | FINDING | BLOCKED`
- Review record, one line per round (reviewers by role and model family, claims raised
  and confirmed, what was run, verdict): {{ROUNDS_OR_NONE}}

Review convergence: predeclare the target-native `CLEAN` threshold; freeze candidate and
evidence identity; record the finding author; a separate fix writer addresses accepted
findings; rerun affected evidence; obtain a fresh non-author rereview. Repeat on
`FINDING` until no actionable finding remains or the review is `BLOCKED`. Any
relevant decision, byte, or evidence change expires `CLEAN`; do not add reviewers merely
to fish for agreement.

## Changed-source comprehension

- Adopted language or community convention and owner: {{RULE_SOURCE_FORM_AND_OWNER}}
- Coordinator-attested frozen candidate snapshot, derivation and source set:
  {{COMMAND_OR_OBSERVATION_SNAPSHOT_PATHS_AND_EXCEPTIONS}}
- Writer reconciliation against the candidate set: {{MATCH_OR_MISSING_AND_EXTRA_PATHS}}
- Writer assessment by path: {{SIMPLE_OR_CONSEQUENTIAL_RESULT_AND_LINKED_RATIONALE}}
- Generated, vendored or pure re-export exceptions: {{PATH_REASON_OWNER_OR_NONE}}
- Risk-ranked untouched source-documentation debt: {{PATH_PRIORITY_OWNER_OR_NONE}}
- Reviewer-independent candidate reconciliation (if required):
  {{MATCH_OR_FINDING_OR_NOT_REQUIRED_WITH_TASK_REASON}}
- Non-author source review (if required): `NOT STARTED | CLEAN | FINDING | BLOCKED`

A plan, test pass or comment count is not this assessment. The assessment covers
every human-authored code file in the candidate set; the attestation and writer
assessment are mandatory for every code change. The reviewer reads every resulting
path: missing, stale, decorative or remote-only orientation or rationale is `FINDING`
even when tests pass. `NOT REQUIRED` is a justified task state, not a reviewer verdict
or a waiver of stricter target or user rules, and it is never available for a code
change. Record each reviewer's identity separately from every source author. Final
acceptance stays blocked until the writer inventory matches the attested set, every
changed human-authored code file has a result, and any required independent
reconciliation matches and source review is `CLEAN`.

## Finish

- Remaining hazards or blockers: {{ITEMS_OR_NONE}}
- Recovery point (local only unless publication is separately authorized):
  {{IDENTITY_OR_NONE}}
- Next authorized action: {{ONE_ACTION_OR_STOP}}
