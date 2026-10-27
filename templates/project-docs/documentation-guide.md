# Documentation guide

Template use: merge into an existing documentation or contributor guide when present.
Adopt when documentation roles, locations, or update triggers are hard to find. Keep
the taxonomy proportional; do not introduce generated indexes, mandatory frontmatter,
or archive machinery solely because this sample mentions lifecycle. Replace every
`{{MARKER}}` and delete this note.

- Guide owner: {{DOCUMENTATION_OWNER}}
- Authority: routes documentation roles; grants no Git, package, network, credential,
  deployment, release, or publication permission.
- Evidence boundary: this guide does not prove that any routed document is current.
- Maintenance: update when a role, location, lifecycle, owner, or same-change trigger
  changes.
- Revisit or retire: merge into a stronger guide, or remove roles the project no longer
  uses.

Last verified against: {{SNAPSHOT_OR_DATE}}

## Authority and locations

| Role | Current path or system | Lifecycle | Owner |
|---|---|---|---|
| Provider-neutral startup/router | `{{AGENT_ENTRY_PATH}}` | Living, small | {{OWNER}} |
| Human/project entry | `{{README_PATH}}` | Living | {{OWNER}} |
| System boundaries and owners | `{{SYSTEM_MAP_PATH_OR_NONE}}` | Living | {{OWNER_OR_NONE}} |
| Engineering/testing contract | `{{STANDARDS_AND_TEST_PATHS}}` | Living | {{OWNER}} |
| Invariants/state | `{{INVARIANT_PATHS_OR_CODE_OWNERS}}` | Living | {{OWNER}} |
| Decisions | `{{ADR_OR_DECISION_LOCATION}}` | Accepted decisions are superseded explicitly | {{OWNER}} |
| Technology/options research | `{{RESEARCH_BRIEF_LOCATION_OR_NONE}}` | Frozen and dated after kickoff | {{OWNER_OR_NONE}} |
| Proven-pattern dispositions/deviations | `{{ADOPTION_RECORD_OR_RESEARCH_PLAN_SECTION}}` | Frozen with the architecture choice; reopened only on its trigger | {{OWNER_OR_NONE}} |
| Active plan/task | `{{PLAN_OR_TASK_LOCATION}}` | Current until complete/superseded | {{OWNER}} |
| User-visible changes | `{{CHANGELOG_OR_RELEASE_SYSTEM}}` | Append/current release policy | {{OWNER}} |
| Observed defects | `{{BUGFIX_OR_ISSUE_SYSTEM}}` | Retain while recurrence knowledge matters | {{OWNER}} |
| Runbooks, studies, and reviews | `{{LOCATIONS_OR_NONE}}` | Living runbooks; frozen dated evidence | {{OWNER_OR_NONE}} |
| Subtree instruction overlays | `{{LOCAL_INSTRUCTION_PATHS_OR_NONE}}` | Living only while local rules differ | {{OWNER_OR_NONE}} |

Current source and executable evidence outrank prose. Living owners outrank dated
studies and superseded plans. Correct stale mirrors in the same change.

## Naming and lifecycle

- Use `{{PROJECT_NAMING_RULE}}`; keep one living owner per topic and update it in place.
- Date frozen studies/reviews with `{{DATE_RULE}}` when the target retains them.
- An accepted ADR is not silently rewritten; add a superseding decision and link both.
- A superseded document names its successor. Archive it only if historical evidence is
  useful; otherwise remove it after inbound references are updated.
- A temporary doc or source pin states owner, recurring cost, and deletion condition.
- Extend an existing role before creating a new file. Empty documentation is not a
  successful bootstrap.
- Root agent instructions own global policy. The closest applicable subtree overlay
  may add local routes or explicitly override one named root item only for its declared
  path; it does not copy the global core.

## Human-readable intent and diagrams

Documentation exists for human collaboration as well as agent resumption. A human owner
must be able to find the rationale, assumptions, invariant, evidence, and update point for
a consequential behavior without reconstructing them from generated code or transcripts.
Use complete, direct prose; do not compress durable knowledge into cryptic fragments to
save tokens.

Keep local rationale adjacent to the code it qualifies and route cross-cutting intent to
the system map, invariant ledger, ADR, or subsystem guide that owns it. Avoid duplicating
the same rule in comments and several documents. Reject comments that restate code and
remove or correct stale comments in the same change as behavior.

Use an editable source-controlled diagram format (for example Mermaid or SVG) when
relationships, state transitions, or data flow are materially easier to understand
visually. Store the source with the project, provide a text
alternative that conveys the important meaning, and record an owner plus the source or
decision change that requires an update. Verify diagrams during relevant review. Do not
add decorative graphics or diagram-count targets.

Every human-authored code file is itself a documentation entry point: use the
language/community-native module, file or type form to state its role immediately. One
sentence is sufficient for simple code; consequential decisions add local why,
invariants, units/bounds and applicable failure/state/concurrency/security/resource
semantics. An exact ADR-section link may deepen but never replace that local contract.
Generated/vendor/mechanical exceptions are recorded, not padded.

## Same-change triggers

- User-visible behavior → {{CHANGELOG_OR_RELEASE_OWNER}}.
- Reproduced defect fixed → {{BUGFIX_OR_ISSUE_OWNER}}.
- Boundary/owner/flow → {{SYSTEM_MAP_OWNER}}.
- State/event/retry/reset semantics → {{INVARIANT_OWNER}}.
- Native command or proof meaning → {{TESTING_OWNER}}.
- Engineering rule or closing gate → {{STANDARDS_OWNER}}.
- New or materially changed authored code → immediate source orientation, applicable
  local rationale, changed-source assessment and non-author review.
- Load-bearing decision → {{ADR_OR_DECISION_OWNER}}.
- Technology/stack choice → dated research brief + architecture ADR + kickoff plan.
- Proven-pattern adoption, merge, citation, omission, or novel replacement → the
  current adoption/deviation record and its challenger disposition.
- Repeatable external/operational procedure → runbook owner, including abort,
  rollback/recovery, unavailable proof, and sign-off.
- Plan/task state, stop, acceptance, or cleanup → {{PLAN_OR_TASK_OWNER}}.

## Add, move, or delete a document

1. Search for an existing owner and extend it first.
2. Name the reader, decision value, owner, lifecycle, and update trigger.
3. Add only the smallest useful content and links to source/evidence.
4. Run `{{LINK_OR_DOC_CHECK}}` when available; otherwise inspect every changed local
   link and routed path directly.
5. Update inbound routes and mirrors in the same change.
6. On retirement, preserve unique current facts in the successor before removal.

Do not create a generated catalogue, doc database, mandatory schema, or scheduled
documentation ceremony without a reproduced findability defect and a cheaper-option
comparison.
