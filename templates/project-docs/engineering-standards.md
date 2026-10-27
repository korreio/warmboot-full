# Engineering standards

Template use: merge into an existing contributor or engineering guide when one owns
durable rules. Adopt only for rules that change implementation or review decisions.
Omit a separate guide when configuration and short existing docs are sufficient.
Replace every `{{MARKER}}` and delete this note.

- Standards owner: {{OWNER}}
- Authority: constrains work inside granted scope; grants no Git, package, network,
  credential, deployment, release, or publication permission.
- Evidence boundary: a rule is a gate only when its named enforcement can block.
- Maintenance: update when an invariant, tool owner, native check, or exception path
  changes.
- Revisit or retire: merge into a stronger living owner or remove rules that no longer
  affect decisions.

Applies to: {{PATHS_OR_COMPONENTS}}

## Technology baseline

- Accepted architecture ADR: `{{TECHNOLOGY_ARCHITECTURE_ADR}}`
- Runtime/tool versions and their manifest owners: {{RUNTIMES_VERSIONS_AND_PATHS}}
- Package manager and lockfile owner: `{{PACKAGE_MANAGER_AND_LOCKFILE}}`
- Formatting, linting, typing, build, and packaging owners:
  {{NATIVE_TOOL_OWNERS}}

Do not change the language, framework, package manager, lockfile strategy, or major
toolchain boundary as routine dependency work. Reopen the ADR with objective-specific
evidence and account for solo-developer maintenance, learning, diversity, security,
licence, and dependency cost.

## Invariants

- {{BEHAVIOR_OR_SAFETY_INVARIANT}}
- {{COMPATIBILITY_OR_DATA_INVARIANT}}

## Rule strength and escape

| Rule | Strength | Applies at | Enforcement or review evidence | Proportional escape and owner |
|---|---|---|---|---|
| {{RULE}} | `{{HARD_GATE_REVIEW_HEURISTIC_CONVENTION}}` | `{{BOUNDARY_OR_PATH}}` | `{{AUTOMATED_CHECK_REVIEW_OR_SOURCE}}` | {{CONCRETE_EXCEPTION_EVIDENCE_AND_DECISION_OWNER}} |

A hard gate is mechanically or authoritatively blocking. A review heuristic requires
an explicit reviewer disposition. A convention is a default with a documented reason,
not a fake automated gate. Remove a rule when it no longer changes a decision.

## Component and dependency boundaries

| Component/state boundary | Single owner | Public port / dependency direction | Pure policy seam | Composition and teardown owner | Native check |
|---|---|---|---|---|---|
| {{BOUNDARY}} | {{OWNER}} | `{{PORT_PATH}}`; {{ALLOWED_DIRECTION}} | `{{PURE_POLICY_PATH_OR_NONE}}` | `{{COMPOSITION_PATH}}`; {{TEARDOWN_OWNER}} | `{{FOCUSED_CHECK}}` |

- Keep policy independently testable where branching behavior is material; do not
  manufacture an abstraction for a trivial path.
- Construct and connect concrete dependencies at the named composition boundary.
  Consumers depend toward owned ports, not through unrelated component internals.
- For phased isolation, name old and new owners, the temporary bridge, entry/cutover
  condition, parity proof, rollback or forward-recovery boundary, and bridge deletion
  condition in the active plan. Two active writers must not own the same state.

## Human inspectability and maintainability

Names, types, and small functions explain what code does; they do not reliably orient a
human at the file boundary or preserve why a consequential choice is safe. After
inspecting current source and the language community's current module/type/API form,
adopt one target-owned rule with an owner, implementation gate, review gate and recorded
exceptions. Do not install a universal tool merely to fill this section.

- Every human-authored code file has immediate language-native orientation. One accurate
  sentence is enough for a simple file. Record generated, vendored and purely mechanical
  re-export/forwarding exceptions; never pad them with decorative prose.
- Keep operative rationale and invariant documentation adjacent to non-obvious algorithms and
  boundaries: units, coordinate/projection conventions, numerical tolerances and
  intervals, concurrency, caching, idempotency, retry/circuit behavior, persistence,
  privacy, and failure/recovery assumptions. Link durable cross-cutting rationale to
  its exact ADR/invariant section instead of duplicating it, but first state the local
  role and contract. Tests, unlinked ADRs, transcripts and agent memory do not substitute.
- Comments and API documentation explain intent, constraints, surprising trade-offs,
  and safe use. Reject prose that restates syntax, stale or misleading commentary,
  generated filler, and comment/Javadoc-count targets.
- Organize living project documentation for a human owner who must locate, understand,
  challenge, and update intent without reconstructing it from agent transcripts or the
  whole codebase. Clear prose is an engineering interface; cryptic token-saving prose
  is not an acceptable substitute.
- Use an editable source-controlled diagram format (for example Mermaid or SVG) only
  when a relationship, state machine, or data flow is materially clearer than prose.
  Supply a useful text alternative, name its
  owner and update trigger, and review it against the implementation. Diagram counts
  and decorative diagrams are not evidence.
- Small, cohesive files and explicit architecture boundaries reduce human and agent
  context cost. A target may adopt locally calibrated SLOC, file-size, complexity, or
  dependency pressure as a review/refactoring trigger, with an exception rationale.
  It is not a universal cap, a quality score, or a proxy for comments and tests.

Record the selected checks, review-only heuristics, exceptions, and update triggers in
the rule table above. Human reviewability is required evidence for consequential
rationale; a green machine check cannot prove that the owner can find or challenge it.
Before every implementation handoff, the coordinator attests the frozen candidate source
set and the writer reconciles and assesses every changed human-authored code file against
it. A non-author reviewer independently repeats that reconciliation, reads the complete
set, and returns `FINDING` for an omitted file or for missing, stale, decorative or
remote-only explanation even when tests pass. Untouched debt is inventoried by consequence
and prioritized rather than silently accepted.

For a materially complex or multi-component codebase, name one current quality-control
owner and location (the active plan, system map or a dedicated assessment). Periodically
assemble evidence by applicable concern, keep unknowns explicit, and give each material
weakness an owner plus next action/revisit trigger. A human or independent non-author
challenges it. Scores/grades cannot self-close; automation collects facts or regressions,
not semantic adequacy. Tiny projects may merge this loop into ordinary plan/review.

## Native evidence

| Change or hazard | Cheapest valid command/observation | Evidence owner |
|---|---|---|
| {{FOCUSED_BEHAVIOR}} | `{{FOCUSED_NATIVE_COMMAND}}` | {{OWNER}} |
| {{INTEGRATION_BOUNDARY}} | `{{INTEGRATION_COMMAND}}` | {{OWNER}} |
| {{RELEASE_RELEVANT_HAZARD}} | `{{RELEASE_CHECK_OR_OBSERVATION}}` | {{OWNER}} |

Commands are examples only after adaptation from current project source. Record what
ran, its relevant snapshot/input, and what it proves. Do not substitute a lower tier
for required unavailable proof; use `UNPROVED` or `BLOCKED`.

## Ownership and authority

- The current task artifact names the top-level coordinator as the sole Git/remote
  holder and operator, exact path owners, and one holder for each other mutable or
  scarce resource. The coordinator may hold any of those other resources too.
- The coordinator is the sole Git mutator and checkpoint/stage/commit/ref/
  configuration/Git-mediated-worktree/remote/credential holder. When history changes
  a worker/reviewer decision, its initial assignment pre-attests the exact absolute
  repository, frozen refs/objects and ancestry, pathspecs, and exact commands. The
  invocation uses `GIT_OPTIONAL_LOCKS=0` or `git --no-optional-locks`. The only
  eligible local reads are `git rev-parse --verify`,
  `git status --short --untracked-files=all`, `git --no-pager log`,
  `git --no-pager log --follow`, `git --no-pager show --no-ext-diff`, and
  `git --no-pager blame`. Every `git diff` form and every unlisted/mutating/config/
  remote/credential operation is excluded.
- The coordinator alone chooses, stages, and commits exact reviewed checkpoint paths
  and performs any separately authorized Git/remote operation. Publication and other
  external effects require separate authority.
- For a coherent checkpoint, the coordinator preserves the cause or decision, directly
  or by a durable reference, and one useful sentence explaining why the evidence and
  review support it. The target's native checkpoint convention determines where this
  belongs; merge into that record rather than create a duplicate ledger.
- Preserve unrelated local work and {{PROJECT_SPECIFIC_PROTECTED_INPUTS}}.

## Change rule

Update this file only when an invariant, native check, owner, or authority boundary
changes. A preference without a decision consequence does not belong here.

Applicable portfolio precedent is presumed `ADOPT` or `MERGE INTO EXISTING`. A
material `CITE ONLY`, `OMIT`, or novel alternative points to
`{{ADOPTION_DEVIATION_RECORD}}`; incomplete current evidence, bounded comparison, tax/
failure analysis, challenger disposition, or reversal trigger blocks the related
implementation/install gate.

## Documentation fallout

- User-visible behavior updates `{{CHANGELOG_OR_RELEASE_OWNER}}`.
- A reproduced defect updates `{{BUGFIX_OR_ISSUE_OWNER}}`.
- Boundary/owner/state changes update `{{SYSTEM_MAP_OR_INVARIANT_OWNER}}`.
- A load-bearing technology or architecture change updates its ADR, research evidence,
  plan, and any stale bootstrap/test command in the same change.
