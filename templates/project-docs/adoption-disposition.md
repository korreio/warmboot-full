# Proven-pattern adoption and deviation record

Template use: merge the tables into the active research brief or plan when that
already owns the decision. Adopt during a new-project kickoff, architecture reset, or
material portfolio migration. It is not a permanent compliance register. Replace every
`{{MARKER}}` and delete this note.

- Record owner: {{ADOPTION_RECORD_OWNER}}
- Authority: records dispositions; grants no implementation, installation, Git,
  network, credential, deployment, release, or publication permission.
- Evidence boundary: a disposition holds only for the source identities and evidence
  it cites.
- Maintenance: update when a source identity, disposition, deviation proof, or
  challenge result changes.
- Revisit or retire: freeze or retire the record after the architecture decision;
  reopen a row only on its reversal trigger.
- Target snapshot and constraints: {{TARGET_PATH_COMMIT_OR_STATE_AND_CONSTRAINTS}}
- Proven source identities: {{SOURCE_REPOSITORIES_COMMITS_OR_DIGESTS}}
- Related research / ADR / plan: `{{TARGET_OWNED_PATHS}}`

## Warmboot release receipt

- Evaluation state: `{{RELEASED_ADOPTION_NON_RELEASE_EVALUATION_BLOCKED}}`
- Warmboot annotated release tag/resolved commit/consumer pin:
  `{{ANNOTATED_RELEASE_TAG_OR_UNPROVED_NON_RELEASE}}` /
  `{{FULL_COMMIT_OR_UNPROVED}}` / `{{UNCHANGED_TAG_OR_RESOLVED_COMMIT_PIN}}`
- Release manifest path/SHA-256: `{{PATH_OR_NONE}}` / `{{SHA256_OR_UNPROVED_NON_RELEASE}}`
- Manifest payload aggregate/completeness/source-evidence validation:
  `{{PAYLOAD_SHA256_OR_UNPROVED}}` /
  `{{PROVED_OR_UNPROVED_NOT_EVALUATED}}` / `{{PROVED_OR_UNPROVED_WITH_REASON}}`
- Release state/release-note SHA-256: `{{STATE_OR_NON_RELEASE}}` / `{{SHA256_OR_UNPROVED}}`
- Frozen target identity: `{{COMMIT_TREE_OR_STATE_DIGEST_AND_DIRT_BOUNDARY}}`
- Helper manifest path/SHA-256: `{{PATH_OR_NOT_USED}}` / `{{SHA256_OR_NOT_USED}}`
  (`LOCAL_SELF_DECLARED_EVIDENCE` when present; never release authority)
- Upgrade eligibility: `{{ELIGIBLE_OR_BLOCKED_WITH_REASON}}`
- Git holder/checkpoint/publication:
  `{{TARGET_GIT_HOLDER}}` / `{{CHECKPOINT_STATE}}` / `{{PUBLICATION_STATE}}`

## Disposition matrix

Inspect the exact source before classifying it. An applicable pattern proved in the
portfolio is presumed `ADOPT` or `MERGE INTO EXISTING`. `CITE ONLY`, `OMIT`, or a new
alternative is allowed when the target differs materially, but its deviation ID must
have complete evidence in the next table.

| ID | Source pattern and exact snapshot/path | Target applicability and concrete constraint | Disposition | Target destination / surviving owner | Native proof and result | Recurring cost / deletion or revisit trigger | Deviation ID |
|---|---|---|---|---|---|---|---|
| {{PATTERN_ID}} | `{{SOURCE_IDENTITY_PATH_SECTION_OR_DIGEST}}` | {{APPLICABLE_MISMATCH_OR_NOT_APPLICABLE_AND_WHY}} | `{{ADOPT_MERGE_INTO_EXISTING_CITE_ONLY_OMIT}}` | `{{TARGET_PATH_OR_NONE}}` — {{OWNER_OR_NONE}} | `{{COMMAND_SPIKE_OBSERVATION_OR_UNPROVED}}` — {{RESULT_AND_LIMIT}} | {{MAINTENANCE_TAX_AND_REVERSAL_TRIGGER}} | {{DEVIATION_ID_OR_NONE}} |

`MERGE INTO EXISTING` names the one target authority that survives; no template copy
remains. `CITE ONLY` preserves decision-relevant provenance without pretending source
evidence proves target behavior. `OMIT` must not erase a target hazard merely to avoid
the recurring cost.

## Deviation proof

Complete one row for every `CITE ONLY`, `OMIT`, or materially novel alternative. Use
dated primary/official evidence for current ecosystem claims and a bounded comparative
spike or test when the difference is locally observable. If a valid spike cannot run,
state the unavailable proof and its consequence rather than inventing a result.

| Deviation ID | Concrete source-to-target mismatch | Current primary/official evidence | Bounded comparison or spike | Recurring tax, migration, and failure/recovery comparison | Distinct challenger result | Reversal evidence and revisit trigger |
|---|---|---|---|---|---|---|
| {{DEVIATION_ID}} | {{OBJECTIVE_RUNTIME_RISK_SCALE_PRIVACY_LICENCE_OR_OPERABILITY_MISMATCH}} | [{{SOURCE_TITLE}}]({{HTTPS_URL}}), updated {{SOURCE_DATE_OR_NOT_STATED}}, accessed {{YYYY_MM_DD}} — {{CLAIM_AND_LIMIT}} | `{{COMMAND_PROCEDURE_OR_UNAVAILABLE}}` — {{RESULT_OR_UNPROVED_CONSEQUENCE}} | {{PROVEN_PATTERN_VS_ALTERNATIVE_COST_FAILURE_MODE_RECOVERY_AND_OWNER}} | `{{CLEAN_FINDING_BLOCKED}}` — {{CHALLENGER_RECEIPT_AND_DISPOSITION}} | {{OBSERVATION_THAT_SUPPORTS_REVERSAL_AND_DATE_OR_STATE_THAT_REOPENS_DECISION}} |

## Gate

- Every relevant source pattern has exactly one disposition and a target owner or an
  evidence-backed reason for having none.
- Every non-`ADOPT`/non-`MERGE INTO EXISTING` result has a complete deviation row and
  a disposed independent challenge.
- Source proof, target proof, and unavailable proof remain labelled separately.

Until these conditions are met for a material architecture or installation choice,
the related implementation and package-installation gates remain `BLOCKED`. A
coordinator synthesis or refreshed handoff does not authorize either gate.
