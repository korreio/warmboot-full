# {{PROJECT_NAME}} agent contract

Template use: merge into existing project instructions when present. Adopt as the
project-owned, provider-neutral startup/router for native-merged adoption. Do not use
it to replace the managed Warmboot loader while still claiming an exact managed
manifest/content match. Replace every `{{MARKER}}` and delete this note.

- Contract owner: {{AGENT_CONTRACT_OWNER}}
- Authority: routes work inside granted scope; grants no Git, package, network,
  credential, deployment, release, or publication permission.
- Evidence boundary: following a route proves nothing until its routed evidence runs.
- Maintenance: update when a route, owner, singleton holder, or safety boundary
  changes.
- Revisit or retire: merge into a stronger existing instruction source; remove routes
  that no longer change a decision.

This is the always-loaded safety core, not a repository notebook. Current source,
manifests, configuration, executable tests, and observed runtime state outrank stale
prose. Load only the task route needed below.

## Always-loaded core

- Start by inspecting `{{PROJECT_ROOT}}`, the current task, snapshot/status, and the
  exact paths in scope. Preserve unrelated or concurrent work.
- Read this root contract first. When work is inside a subtree with a local instruction
  overlay, load the closest applicable overlay next. It may add local routes or
  override only a named root item within its declared subtree; this root remains the
  global authority and nested files do not duplicate its global policy.
- Scope and authority do not grow by inference. External effects allowed for the
  current task are recorded in `{{CURRENT_TASK_OR_AUTHORITY_SOURCE}}`.
- Name one top-level coordinator, who is the sole Git mutator and holder for
  checkpoints/staging/commits, refs/configuration, Git-mediated worktree
  administration, remotes, Git network access, and repository credentials. Name one
  holder for each other mutable or scarce resource; the coordinator may hold any of
  those too. When local history changes a bounded worker/reviewer decision, its
  initial assignment pre-attests the exact local repository, refs/objects and allowed
  ancestry, pathspecs, and commands. Every invocation uses
  `GIT_OPTIONAL_LOCKS=0` or `git --no-optional-locks`. Only
  `git rev-parse --verify`, `git status --short --untracked-files=all`,
  `git --no-pager log`, `git --no-pager log --follow`,
  `git --no-pager show --no-ext-diff`, and `git --no-pager blame` are eligible;
  every `git diff` form is excluded. Publication is separate from local checkpoints.
- **One-time kickoff exception:** for a new project or genuine architecture reset, act
  as an orchestration-only coordinator. Read `{{BOOTSTRAP_CONTRACT_PATH_OR_TOOLKIT}}`,
  cover the six required exploration concerns with the smallest proportional set of at
  least two distinct non-coordinator research owners, synthesize their attributed
  receipts without doing lane research, and then commission a distinct non-author owner
  to challenge the draft research brief, ADR, and plan. Two research owners are a floor,
  not a target. Risk drives further separation. Do no implementation or package
  installation until the ADR is accepted and the applicable implementation/install
  gate is explicitly `AUTHORIZED`.
- After that kickoff decision, prefer one writer; every code change gets an independent
  reviewer, as does other material risk; add parallel lanes only for genuinely
  independent paths/resources.
- Name the hazard before selecting evidence. Start with the cheapest check that can
  observe it; unavailable required proof remains `UNPROVED` or `BLOCKED`.
- Update the existing documentation owner in the same change when behavior, boundary,
  state, tests, decisions, or release-facing output changes.
- Keep the required target-owned root `*.code-workspace` aligned in the same change
  when project folders or canonical setup/test/lint/build/run/debug commands change.
  Preserve existing workspace/`.vscode/` owners; do not duplicate settings/tasks or
  add speculative commands, secrets, provider policy, or authority.

## Task router

| Work | Current owners | Load before editing | Cheapest valid proof and authority limit |
|---|---|---|---|
| {{TASK_SHAPE_ONE}} | `{{SOURCE_AND_DECISION_OWNERS}}` | `{{LIVING_CONTRACTS_AND_APPLICABLE_PLAN_SECTION}}` | `{{FOCUSED_CHECK}}`; close with `{{CLOSING_GATE}}`. {{EXTERNAL_OR_PHYSICAL_LIMIT}} |
| {{TASK_SHAPE_TWO}} | `{{SOURCE_AND_DECISION_OWNERS}}` | `{{LIVING_CONTRACTS_AND_APPLICABLE_PLAN_SECTION}}` | `{{FOCUSED_CHECK}}`; close with `{{CLOSING_GATE}}`. {{EXTERNAL_OR_PHYSICAL_LIMIT}} |
| Tooling, tests, or documentation | `{{TOOL_TEST_DOC_PATHS}}` | `{{STANDARDS_TESTING_DOCUMENTATION_GUIDE}}` | `{{STATIC_OR_NATIVE_CHECK}}`; do not run unrelated expensive tiers |

If work crosses rows, load every applicable owner and serialize overlapping writers.
The system map may hold larger task/symptom routing; do not duplicate its subsystem
detail here. A local overlay routes only a genuinely different subtree and is removed
when the distinction no longer earns its recurring cost.

## One-time project kickoff

The top-level coordinator remains the sole Git mutator and remote/credential holder.
Every other singleton resource has one named holder. The exploration owners use the
coordinator-attested snapshot and exact paths. Only when history changes their
decision may the initial assignment grant the exact bounded local reads in the
always-loaded core above; it never grants Git mutation, `git diff`, remote access, or
repository credentials. Cover the following concerns with the smallest proportional
set of at least two distinct non-coordinator research owners. Every concern keeps its
own attributed evidence artifact and receipt; every owner has a stop condition:

1. objective, constraints, authority, repository, and context inspection;
2. current objective-specific language using dated primary/official sources;
3. current application stack plus target-owned proven-portfolio comparison;
4. current developer tooling using dated primary/official sources;
5. architecture options, boundaries, risks, privacy, security, and maintenance cost;
6. testing, bootstrap, package installation, and operability design.

Two research owners are a floor, not a target. Add owners where uncertainty,
specialist knowledge, or coupled hazards make another independent view useful. For
destructive or high-risk work, architecture/risk/privacy and
testing/bootstrap/operability use different owners. Any lower-risk merge records why
it is safe and gives the challenger explicit cross-checks for path/resource aliasing,
source preservation, exact commands, failure injection, and platform prerequisites
where applicable.

After all six concern receipts, the coordinator synthesizes `{{TECHNOLOGY_RESEARCH_BRIEF}}`
and drafts `{{TECHNOLOGY_ARCHITECTURE_ADR}}` plus `{{KICKOFF_PLAN}}`; it does not
perform lane research or implementation. Only then a distinct non-author read-only owner
challenges all three drafts and returns its own receipt. The final plan records exact
prerequisites, versions, package manager/lockfile, install/bootstrap commands,
verification, ownership, and separate implementation/install gates. If current evidence is unavailable, record the affected claim
and date as `UNPROVED` or `BLOCKED`; never invent SOTA. The ADR must be accepted and
the applicable plan gate explicitly `AUTHORIZED` before product code or package installation.
This topology is mandatory only for a new project or genuine architecture reset, not
for steady-state work.

## Routine handoff, exceptional rotation, and review

Use the current task or freshness-receipt role for a substantial delegation, pause,
resume, session change, or provider change. Carry only the relevant snapshot, changed
and concurrently owned paths, evidence as `INHERITED`, `RERUN NOW`, or `UNPROVED`,
blockers/unknowns, next unresolved outcome, and links to the live governing sources.
A handoff does not add or transfer policy, scope, permission, Git/resource ownership,
topology, review order, external authority, or provider process. Re-read the live
repository and refresh affected evidence before editing.

Use exceptional rotation only when an explicitly named replacement takes over from
the actual active coordinator, Git holder, or another scarce-singleton holder. Only
that event needs quiescence plus `RELINQUISHED`/independent-preflight/`ACCEPTED`.
Session/provider change and disjoint cross-provider work under the same named holder
are routine, not rotation.

Every code change, and any other substantial package, is reviewed by a different
read-only reviewer. The verdict is exactly `CLEAN`, `FINDING`, or `BLOCKED`; a candidate
or evidence change expires prior clean credit.

## Delivery

- Focused checks diagnose; `{{CLOSING_GATE}}` closes substantive work in its scope.
- User-visible change → `{{CHANGELOG_OWNER_OR_NONE}}`; reproduced defect fixed →
  `{{BUGFIX_OWNER_OR_NONE}}`; changed boundary/state/decision → its existing owner.
- The coordinator chooses reviewed exact paths for a local recovery commit and alone
  stages or commits them. The coordinator is also the only person who may perform a
  separately authorized push or other Git/remote operation. PR, release, deploy,
  credentials, and other external mutations require separate authority.
