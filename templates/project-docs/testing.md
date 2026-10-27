# Testing and evidence

Template use: merge into existing test documentation or engineering standards when
they already route native checks. Adopt when command choice or proof limits are unclear.
Omit a separate guide for a tiny project with one obvious test path. Commands must come
from current target source; never infer them from the language alone. Replace every
`{{MARKER}}` and delete this note.

- Test-contract owner: {{OWNER}}
- Authority: records approved local checks; grants no package, network, credential,
  device, deployment, release, publication, or shared-resource permission.
- Evidence boundary: each pass proves only the behavior its environment can observe.
- Maintenance: update when commands, tiers, fixtures, owners, or evidence meaning
  changes.
- Revisit or retire: merge when another guide owns these routes; remove tiers that no
  longer change a decision.

Applies to: {{PATHS_OR_COMPONENTS}}
Last verified against: {{SNAPSHOT_OR_DATE}}

## Canonical commands

| Intent | Canonical project wrapper | Raw runner equivalent / diagnostic use | What a pass proves | What it does not prove |
|---|---|---|---|---|
| Focused iteration | `{{FOCUSED_WRAPPER_COMMAND}}` | `{{RAW_FOCUSED_RUNNER_OR_NONE}}` | {{LOCAL_BEHAVIOR_OR_SHAPE}} | {{HIGHER_TIER_LIMIT}} |
| Changed-scope check | `{{CHANGED_SCOPE_WRAPPER_OR_NONE}}` | `{{RAW_CHANGED_SCOPE_RUNNER_OR_NONE}}` | {{SCOPED_SIGNAL}} | {{LIMIT}} |
| Ordinary closing suite | `{{ORDINARY_SUITE_WRAPPER}}` | `{{RAW_SUITE_RUNNER_OR_NONE}}` | {{REPOSITORY_EVIDENCE}} | {{EXTERNAL_LIMIT}} |
| Release/CI parity | `{{RELEASE_OR_CI_WRAPPER_OR_NONE}}` | `{{HOSTED_OR_RAW_EQUIVALENT_OR_NONE}}` | {{PARITY_SCOPE}} | {{PHYSICAL_OR_HOSTED_LIMIT}} |

Focused evidence diagnoses. It is not closing evidence unless the target's current
contract explicitly says so. Use the canonical wrapper for closing claims because it
owns target flags, setup, ordering, environment, and cleanup. A raw runner is allowed
for bounded diagnosis only; record the difference and return to the wrapper before
claiming closure.

## Changed boundary to closing set

| Changed boundary | Minimum focused set | Required closing set | Escalation trigger | Clean-rerun requirement |
|---|---|---|---|---|
| {{SOURCE_CONFIG_CONTRACT_OR_FLOW}} | `{{FOCUSED_TESTS_OR_CHECKS}}` | `{{CLOSING_WRAPPER_AND_SCOPE}}` | {{FAILURE_CROSS_OWNER_OR_PARITY_TRIGGER}} | {{FRESH_PROCESS_STATE_FIXTURE_OR_RESULT_PATH}} |

- A focused red belongs first to the changed boundary owner.
- A broad red remains owned by the broad-run holder until reproduced on the owning
  surface or classified as unrelated infrastructure/concurrent noise. Do not assign a
  product regression from one contaminated broad run.
- After a fix, rerun the failing focused check and the applicable closing set from the
  recorded clean process, fixture, cache, database, and result-path state. A pass that
  reused suspect mutable state is not closing evidence.

## Evidence tiers

| Hazard | Cheapest tier that can observe it | Escalate when | Singleton resource/holder |
|---|---|---|---|
| {{STATIC_OR_CONFIG_HAZARD}} | `{{STATIC_CHECK}}` | {{ESCALATION_TRIGGER}} | {{RESOURCE_OR_NONE}} |
| {{LOCAL_BEHAVIOR_HAZARD}} | `{{UNIT_COMPONENT_OR_INTEGRATION_CHECK}}` | {{ESCALATION_TRIGGER}} | {{RESOURCE_OR_NONE}} |
| {{RUNTIME_BOUNDARY_HAZARD}} | `{{RUNTIME_BROWSER_DB_DEVICE_CHECK}}` | {{ESCALATION_TRIGGER}} | {{RESOURCE_AND_HOLDER}} |
| {{EXTERNAL_OR_RELEASE_HAZARD}} | `{{AUTHORIZED_OBSERVATION}}` | Never infer from local evidence | {{CREDENTIAL_OR_ENVIRONMENT_HOLDER}} |

Keep unit, integration, consumer/provider contract, end-to-end, external, and human
evidence distinct. Name the tier each command actually reaches. A mock-backed unit test
does not prove a database, network service, platform, device, or human-comprehension
boundary, and a green count does not prove route usefulness.

For consequential logic, choose the smallest useful combination of focused examples,
tables, property tests, metamorphic relations, and contract/integration checks. Derive
expected values from an independently reasoned oracle, hand calculation, standard, or
differently structured implementation where practical. Independence means different
derivation/provenance, not merely a different agent identity; fixtures produced by the
implementation under test are not independent expectations. Review assertions for
sensitivity to the defect, meaningful failure messages, boundary cases, and accidental
tautologies.

Coverage locates unobserved critical paths; percentages do not establish correctness.
Do not set or raise a percentage merely to create a gate. Use selective mutation testing
when it can cheaply reveal weak assertions in risk-bearing pure logic, and record its
scope and surviving limitations. For an escaped defect, reproduce the failure red before
the correction, then retain the smallest behavior regression test; add a special pin only
under the repository's observed-defect rule.

Every skipped, disabled, quarantined, conditional, or environment-gated test has a
reason, owner, consequence, and final-acceptance disposition. A required tier that did
not run remains `UNPROVED` or `BLOCKED`; zero unexplained skips is the acceptance rule,
not “all tests that happened to run were green.”

Source comprehension is a separate human evidence tier. Tests may demonstrate behavior
but cannot replace a file's immediate role or local rationale. For a code change, record
the coordinator-attested candidate source set, the writer's reconciled assessment and
exceptions for every changed human-authored code file, and the distinct reviewer who
repeated the reconciliation and read every file in full. Missing or stale source
contracts block the scoped closing claim even when every executable check passes.

## Entry-path parity

List alternate and default paths only when they are real product entry points.

| Behavior/owner | Default path | Alternate path | Shared invariant | Parity proof / unavailable boundary |
|---|---|---|---|---|
| {{BEHAVIOR_OR_COMPONENT}} | `{{DEFAULT_ENTRY_PATH}}` | `{{ALTERNATE_ENTRY_PATH}}` | {{SAME_OWNER_STATE_OR_OUTPUT}} | `{{PARITY_CHECK_OR_UNPROVED}}` — {{RESULT_AND_LIMIT}} |

A default-path pass cannot stand in for an alternate path whose wiring, platform,
configuration, or composition differs. Mark an unavailable required path `UNPROVED`
or `BLOCKED`; do not manufacture an alternate path to fill the table.

## Failure and freshness

- Record exact command, result, snapshot, relevant inputs, and configuration.
- A failed broad run becomes a regression claim only after the failure is reproduced
  on the owning surface and unrelated infrastructure noise is separated.
- A handed-off pass stays `INHERITED` until its snapshot and inputs are checked; rerun
  affected claims as `RERUN NOW`. Unknown required proof is `UNPROVED` or `BLOCKED`.
- Use unique result paths and one named holder for mutable reports, browsers, databases,
  ports, devices, or test services.

## Mutable result ownership

| Mutable output/resource | Holder | Unique path/namespace | Pre-run state | Cleanup or retention condition | Collision response |
|---|---|---|---|---|---|
| {{REPORT_CACHE_DATABASE_PORT_BROWSER_DEVICE_OR_SERVICE}} | {{NAMED_HOLDER}} | `{{PATH_NAMESPACE_OR_ID}}` | {{EMPTY_RESET_READ_ONLY_OR_EXISTING}} | {{WHEN_SAFE_TO_DELETE_OR_PRESERVE}} | {{BLOCK_SERIALIZE_OR_NEW_NAMESPACE}} |

Only the named holder creates, resets, cleans, or interprets that mutable result. A
reviewer receives an attested immutable snapshot or exact path, not shared write
authority.

## Automation and owner-eye evidence

| Claim | Automated evidence | Owner-eye/manual evidence | Which is required and why | Recording rule |
|---|---|---|---|---|
| {{CLAIM}} | `{{CHECK_OR_NONE}}` | {{OBSERVATION_PROCEDURE_OR_NONE}} | {{AUTOMATION_OWNER_EYE_BOTH_AND_HAZARD}} | {{SNAPSHOT_RESULT_AND_LIMIT}} |

Automate deterministic recurrence where the signal is stable and worth its tax. Use
owner-eye evidence for visual, physical, semantic, credentialed, or external behavior
that automation cannot validly observe. Neither form silently substitutes for the
other; a manual observation records who observed what, against which snapshot and
environment.

## Test ownership and gaps

| Behavior/boundary | Owning tests or observation | Current gap and consequence | Update trigger |
|---|---|---|---|
| {{BEHAVIOR}} | `{{TEST_PATH_OR_PROCEDURE}}` | {{GAP_OR_NONE}} | {{WHEN_THIS_ROW_CHANGES}} |

Do not add a speculative source pin. After a reproduced recurrence that behavior tests
cannot see, compare the proposed pin with the nearest behavior test against that same
recurrence under the adopted regression-admission rule. Record the pin owner,
recurrence class, reason, cost, red-before proof, and deletion condition beside the
owning regression suite or defect entry.
