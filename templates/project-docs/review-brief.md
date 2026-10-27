# Review brief: {{PACKAGE_OR_OUTCOME}}

Template use: merge into the current task or pull request when it already carries the
review role. Adopt only when a separate review artifact improves independence or scope
control. Replace every `{{MARKER}}` and delete this note.

- Brief owner: {{REQUESTING_COORDINATOR}}
- Authority: scopes one review; grants the reviewer no repair, Git, network,
  credential, deployment, release, or publication permission.
- Evidence boundary: the verdict covers only the frozen candidate, scope, and evidence
  named here.
- Maintenance: settle every field before the review starts; a later candidate, scope,
  or evidence change needs a new review.
- Revisit or retire: freeze or remove the brief after close according to target policy;
  it is not automatically permanent.
- Requested reviewer: {{FRESH_CONTEXT_REVIEWER}}
- Reviewed authorship identities: {{DECISION_AND_BYTE_AUTHORS}}
- Candidate snapshot/diff identity: {{COMMIT_HASH_OR_EXACT_DIFF_IDENTITY}}
- Materialized review target and digest: {{DISPOSABLE_PATH_AND_SHA256}}
- Review scope: `{{EXACT_PATHS_AND_BEHAVIORS}}`
- Explicit exclusions: {{OUT_OF_SCOPE_AND_CONCURRENT_INPUTS}}
- Governing primary contract and owners/invariants: `{{PATHS_AND_SECTIONS}}`
- Predeclared target-native `CLEAN` threshold: {{NO_ACTIONABLE_FINDING_SCOPE_AND_ANY_NAMED_SPECIALIST}}
- Mutable evidence/result holders: {{RESOURCES_HOLDERS_AND_IMMUTABLE_REVIEW_PATHS}}

The coordinator supplies the materialized target, governing primary contract, applicable
route, and evidence boundary. Other reads navigate the scope; they do not grant
instruction authority.

## What changed and why

{{COMPACT_CAUSAL_SUMMARY_WITHOUT_PROMPT_OR_TRANSCRIPT}}

## Claims and evidence

| Claim | Evidence run on this candidate | What remains unproved |
|---|---|---|
| {{CLAIM}} | `{{COMMAND_OR_OBSERVATION_AND_RESULT}}` | {{UNPROVED_OR_NONE}} |

Confirm closing claims used the canonical project wrapper and the required clean
process/fixture/cache/database/result-path state. A raw runner or contaminated rerun
may diagnose but cannot close a scope whose contract requires the wrapper.

## Probe these hazards

1. {{HIGHEST_RISK_FAILURE_MODE}} — inspect `{{SOURCE_OR_TEST_OWNER}}` and require
   {{EXPECTED_EVIDENCE}}.
2. {{CROSS_OWNER_OR_LIFECYCLE_HAZARD}} — verify {{EXPECTED_INVARIANT}}.

When the scope contains consequential logic or documentation, also probe:

- assertion sensitivity, independently derived expectations, fixture independence,
  boundary/counterexample coverage, and whether skips hide a required tier;
- whether coverage evidence identifies blind critical paths rather than rewarding a
  percentage, and whether selective property/metamorphic/mutation evidence would change
  confidence cost-effectively;
- stale or misleading comments, undocumented high-risk invariants or assumptions, and
  comments/API docs that merely restate code;
- whether a human owner can locate and challenge intent, and whether diagrams carry an
  accurate text alternative, owner, and update trigger.
- every changed human-authored code file in full against the target's community-native
  rule: immediate role, applicable local operative rationale, exact deep links, recorded
  generated/vendor/mechanical exceptions, and prioritized untouched debt. Sampling,
  tests, remote ADRs or a grade do not close this lens.
- for a current quality assessment, whether every score/statement cites evidence and an
  owned next action/revisit trigger, unknowns remain visible, and a non-author/human
  challenge—not the score—closes the decision.

For a kickoff architecture review, start only after the coordinator has drafted the
technology-options research brief, ADR, and kickoff/install plan from all six
attributed concern receipts. The reviewer is a distinct non-coordinator owner who
authored none of those inputs or drafts, returns its own receipt, and reviews all three drafts plus their attributed
evidence and any separately stored disposition rows they reference.
Challenge criterion weighting, the proven-stack baseline, freshness and
primacy of sources, unsupported SOTA claims, new dependency cost, privacy/licence/
security boundaries, install reproducibility, and whether the implementation gate is
genuinely ready. Inspect the proven-pattern disposition/deviation record: applicable
precedent defaults to `ADOPT` or `MERGE INTO EXISTING`, and every material `CITE ONLY`,
`OMIT`, or novel alternative has direct source inspection, concrete mismatch, dated
primary evidence, a valid bounded comparison or honest unavailable-proof boundary,
tax/failure/recovery comparison, challenger result, and reversal trigger. Incomplete
deviation evidence is a `FINDING` or `BLOCKED`, never install/implementation readiness.
The coordinator—not the challenger—disposes findings in the ADR and plan.

When architecture/risk/privacy and testing/bootstrap/operability share one research
owner, explicitly cross-check the recorded merge rationale, path/resource aliasing,
source preservation, exact commands, failure injection, and platform prerequisites
where applicable. A high-risk or destructive scope without safe independent coverage
is a `FINDING` or `BLOCKED`.

When relevant, also challenge single component/state ownership, port/dependency
direction, composition and teardown, alternate/default entry-path parity, phased
cutover/rollback, subtree instruction precedence, and runbook abort/external-authority
boundaries. Do not demand these surfaces when the target evidence says they are not
earned.

## Known open and settled boundaries

- Known open / already owned: {{ITEM_AND_OWNER}}.
- Do not re-report without new evidence: {{SETTLED_ITEM_AND_REASON}}.
- Authority/credential/physical limits: {{BLOCKED_OR_UNPROVED_BOUNDARY}}.

## Verdict contract

Return exactly one:

- `CLEAN`: the complete scoped candidate meets acceptance and its evidence is
  sufficient;
- `FINDING`: exact defect evidence, affected invariant, smallest correction, and
  check to rerun; a behavior defect also names its trigger (what a user or caller does
  to reach it, and how often);
- `BLOCKED`: missing authority, ownership, input, or external state, plus what was
  safely verified.

Stay read-only. Do not fix findings. On `FINDING`, a separate writer addresses accepted
findings, affected evidence is rerun, and the reviewer adversarially rechecks the exact
corrected unchanged scope. The fix round enumerates the other members of the class the
finding or its fix names (shared base, sibling copy, second path), fixes each inside the
review scope, and records any other with its owner in the current task. Repeat until
`CLEAN` (no actionable finding in scope) or an honest `BLOCKED`. Any later relevant
decision, candidate-byte, or acceptance-evidence change expires `CLEAN`. A fixed number
of reviews never substitutes for dryness. Fresh
means a new non-author judgement on corrected unchanged bytes and evidence, not a new
thread, session, or provider. Fresh context does not erase authorship; compare the reviewer
against every identity above. The coordinator confirms, refutes, or downgrades each
delegated finding against the reviewed snapshot (and current candidate if different)
before relaying or assigning it; an unverified claim is not a finding. For substantial
code, one already-required round uses another model family than the writer and preceding
reviewer where reachable; if unavailable or naturally failed, a fresh-context non-author
completes that round and the record names the limit.
