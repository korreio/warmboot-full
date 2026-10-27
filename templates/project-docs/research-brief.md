# Technology and options research: {{PROJECT_OBJECTIVE}}

Template use: merge into an existing kickoff record when one already owns this
evidence. Adopt as a one-time kickoff evidence brief, not a recurring research report.
Use primary or official sources for current claims. Replace every `{{MARKER}}` and
delete this note.

- Brief owner, the synthesizing coordinator (no lane research): {{COORDINATOR}}
- Authority: records evidence; grants no implementation, installation, Git, network,
  credential, deployment, release, or publication permission.
- Evidence boundary: each claim holds only for its dated source and receipt.
- Maintenance: update only until the architecture decision is accepted.
- Revisit or retire: freeze and date it when the architecture decision is accepted;
  rerun research on the ADR's revisit trigger rather than editing it.
- Research date: {{YYYY_MM_DD}}
- Objective and target users: {{SPECIFIC_OUTCOME_AND_USER}}
- Decision owner: {{COORDINATOR_OR_HUMAN_OWNER}}
- Target/repository snapshot: {{PATH_AND_COMMIT_OR_STATE}}
- Related architecture ADR: `{{ADR_PATH}}`
- Proven-pattern disposition/deviation record: `{{TARGET_OWNED_RECORD_OR_SECTION}}`

## Required exploration receipts

For a new project or genuine architecture reset, cover all six rows with the smallest
proportional set of at least two distinct non-coordinator research owners. Two is a
floor, not a target. Each row points to that owner's evidence artifact and receipt;
the coordinator synthesizes these inputs but does not research a row itself.
Destructive or high-risk work separates architecture/risk/privacy from
testing/bootstrap/operability. If a lower-risk objective merges those rows, record why
the merge is safe and give the challenger explicit coupled-hazard cross-checks.

| Concern | Owner | Receipt | Evidence artifact | Status / limit |
|---|---|---|---|---|
| Objective/context | {{OWNER}} | {{RECEIPT}} | `{{TARGET_OWNED_PATH}}` | `{{PROVED_UNPROVED_BLOCKED}}` |
| Current language | {{OWNER}} | {{RECEIPT}} | `{{TARGET_OWNED_PATH}}` | `{{PROVED_UNPROVED_BLOCKED}}` |
| Current stack + portfolio | {{OWNER}} | {{RECEIPT}} | `{{TARGET_OWNED_PATH}}` | `{{PROVED_UNPROVED_BLOCKED}}` |
| Current developer tooling | {{OWNER}} | {{RECEIPT}} | `{{TARGET_OWNED_PATH}}` | `{{PROVED_UNPROVED_BLOCKED}}` |
| Architecture/risk/privacy | {{OWNER}} | {{RECEIPT}} | `{{TARGET_OWNED_PATH}}` | `{{PROVED_UNPROVED_BLOCKED}}` |
| Testing/bootstrap/package | {{OWNER}} | {{RECEIPT}} | `{{TARGET_OWNED_PATH}}` | `{{PROVED_UNPROVED_BLOCKED}}` |

## Decision criteria

Rank the criteria for this objective before comparing stacks:

| Criterion | Why it matters | Weight/priority | Evidence needed |
|---|---|---|---|
| {{DELIVERY_SPEED_MAINTAINABILITY_PRIVACY_PERFORMANCE_ETC}} | {{OBJECTIVE_LINK}} | {{PRIORITY}} | {{OBSERVATION_OR_SOURCE}} |

Always include resource constraints, privacy/data handling, security surface, licence,
dependency health, maintenance burden, operability, learning cost, ecosystem maturity,
and fit for one solo developer. Add domain-specific criteria rather than using a generic
“best stack” score.

## Proven portfolio baselines

Use target-owned references rather than copying toolkit-local routes into the adopted
brief:

- Portfolio reference owner: `{{TARGET_OWNED_PORTFOLIO_REFERENCE_PATH_OR_UNAVAILABLE}}`
- Baseline A identity/snapshot: `{{NAME_AND_EXTERNAL_COMMIT_TAG_OR_DIGEST}}`
- Baseline B identity/snapshot: `{{NAME_AND_EXTERNAL_COMMIT_TAG_OR_DIGEST}}`
- Small-combination boundary: `{{TARGET_OWNED_COMBINATION_DESCRIPTION}}`

Record only targeted facts relevant to the objective. Treat familiar proved baselines
or a small combination as preferred when they meet the criteria; current research
validates fitness rather than rewarding novelty. Reuse is not forced. If a reference
or source path is unavailable, record that exact boundary as `UNPROVED` rather than
retaining a toolkit path that the target does not own.

For every relevant proven pattern, record `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY`,
or `OMIT` in the linked target-owned record. Applicable precedent is presumed `ADOPT`
or `MERGE INTO EXISTING`. A material citation, omission, or novel replacement requires
a concrete target mismatch, dated current primary/official evidence, bounded
comparison where observable, tax/migration/failure/recovery comparison, distinct
challenger result, and reversal/revisit trigger.

## Current primary/official evidence

| Claim | Primary/official source and URL | Published/updated | Accessed | Relevance | Confidence / limit |
|---|---|---|---|---|---|
| {{CURRENT_CLAIM}} | [{{SOURCE_TITLE}}]({{HTTPS_URL}}) | {{DATE_OR_NOT_STATED}} | {{YYYY_MM_DD}} | {{OBJECTIVE_SPECIFIC_EFFECT}} | `{{HIGH_MEDIUM_LOW_UNPROVED}}` — {{LIMIT}} |

If current web research or a required official source is unavailable, record the claim,
date, attempted source, and consequence as `UNPROVED` or `BLOCKED`. Do not fill the gap
from memory or call an undated opinion “SOTA.”

## Options

| Option | Objective fit | Proven pattern IDs / disposition | Dependencies/tooling | Privacy/security/licence | Solo maintenance/learning | Operability/testing and failure recovery | Risks and unknowns |
|---|---|---|---|---|---|---|---|
| {{PROVEN_BASELINE_COMBINATION_OR_NEW_OPTION}} | {{FIT}} | {{PATTERN_IDS_AND_DISPOSITIONS}} | {{COST}} | {{BOUNDARY}} | {{COST}} | {{FIT_FAILURE_AND_RECOVERY}} | {{RISKS}} |

For every new language, framework, database, service, or major dependency, state the
specific advantage that outweighs portfolio diversity and recurring cost.

## Bounded comparisons and unavailable proof

| Decision claim | Comparison/spike and owner | Result on target snapshot | Limit | Decision effect |
|---|---|---|---|---|
| {{CLAIM}} | `{{COMMAND_OR_PROCEDURE}}` — {{OWNER}} | {{RESULT}} | {{UNPROVED_EXTERNAL_PHYSICAL_OR_NONE}} | {{KEPT_CHANGED_OR_BLOCKED_CHOICE}} |

Do not install candidate packages merely to complete this table before install
authority. Use non-mutating inspection, existing environments, source evidence, or an
explicitly authorized disposable spike. If no valid comparison is authorized or
available, state the decision consequence as `UNPROVED` or `BLOCKED`.

## Recommendation and challenge

- Recommended option: {{OPTION}}
- Why it wins for this objective: {{EVIDENCE_LED_REASON}}
- What would falsify it: {{REVISIT_TRIGGER}}
- Independent post-draft challenger (distinct non-author): {{REVIEWER_AND_RECEIPT}}
- Strongest counterargument: {{COUNTERARGUMENT}}
- Challenge result: `{{CLEAN_FINDING_BLOCKED}}`
- Corrections made after challenge: {{NONE_OR_CHANGES}}
- Non-`ADOPT`/non-`MERGE INTO EXISTING` deviations checked and disposed: {{IDS_OR_NONE_AND_RESULT}}

The challenger reads the three kickoff drafts and any separately stored disposition
rows they reference. The coordinator, not the challenger, reconciles findings into
the ADR and plan; a clean challenge does not itself accept or authorize either.

## Unproved boundaries

- `{{UNPROVED_OR_BLOCKED_CLAIM}}` — consequence: {{DECISION_OR_IMPLEMENTATION_LIMIT}};
  next valid evidence: {{SOURCE_OR_OBSERVATION}}.

This brief informs the ADR. It does not authorize implementation, package installation,
publication, deployment, or external account creation.
