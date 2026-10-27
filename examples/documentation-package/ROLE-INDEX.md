# Project-document role index — populated example

> **EXAMPLE ONLY.** This is the label-normalizer project's completed adoption
> inventory. It shows what survived bootstrap, where it lives, and what was
> deliberately not created. It is not a universal file list.

- Record owner: `example-coordinator`
- Decision snapshot: accepted ADR 0001 and completed kickoff plan, 2026-07-31
- Detailed pattern decisions: [`docs/adoption-disposition.md`](docs/adoption-disposition.md)
- Living documentation rules: [`docs/documentation-guide.md`](docs/documentation-guide.md)

## Roles retained

| Need | Project owner | Why this surface survives | Read/update trigger | Retirement rule |
|---|---|---|---|---|
| Provider-neutral startup and routing | [`AGENTS.md`](AGENTS.md); [`CLAUDE.md`](CLAUDE.md) points to it | A fresh agent needs one small authority and task routes | Stable safety, authority, route, or closing gate changes | Merge into a surviving equivalent; never keep two provider rulebooks |
| Human entry and offline start | [`README.md`](README.md) | The outcome, destructive comparison-key warning, and no-install path must be obvious | Public semantics, prerequisites, or native start changes | Merge into an established project entry point |
| Current authority, evidence, and handoff | [`TASK.md`](TASK.md) | One active record prevents shadow plans and overstated proof | Scope, authorization, evidence, review, or next step changes | Replace in place for the next task; preserve durable facts in living owners |
| Boundary/symptom navigation | [`docs/system-map.md`](docs/system-map.md) | Core, CLI, package metadata, and kickoff evidence have different owners | Owner, entry path, dependency direction, or first check changes | Merge into README/AGENTS if navigation becomes obvious enough |
| Behavioral invariants | [`docs/invariants.md`](docs/invariants.md) | The destructive-output and adapter-delegation contracts cross code/document boundaries even though runtime state does not | Comparison-key, ordering, side-effect, or package boundary changes | Merge into source/tests if those become sufficient for fresh-agent recovery |
| Enforceable engineering rules | [`docs/engineering-standards.md`](docs/engineering-standards.md) | Rule strength, one-owner design, dependency constraints, and same-change fallout affect reviews | An enforceable gate/heuristic/convention or owner changes | Delete any rule that stops changing a decision |
| Native commands and proof limits | [`docs/testing.md`](docs/testing.md) | Focused and closing sets, raw-runner boundary, evidence limits, and pin admission must be unambiguous | Test entry, fixture, tier, or evidence meaning changes | Merge into standards only if the route remains equally clear |
| Document precedence and lifecycle | [`docs/documentation-guide.md`](docs/documentation-guide.md) | The example deliberately has living, frozen, and omitted roles | Role, authority, update, or retirement rule changes | Merge into README/AGENTS if every remaining role is obvious |
| Proven-precedent classification | [`docs/adoption-disposition.md`](docs/adoption-disposition.md) | This one-time synthetic record shows how reuse is classified and keeps each deviation's summary reason and revisit condition | A named revisit trigger fires or a genuine architecture reset begins | Freeze with ADR 0001; do not turn it into a compliance register |
| Dated technical evidence | [`docs/studies/2026-07-31-technology-options.md`](docs/studies/2026-07-31-technology-options.md) | Illustrative source titles and portfolio comparison support ADR 0001 | Only ADR re-evaluation triggers | Freeze; supersede with a new dated study |
| Architecture decision | [`docs/adr/0001-python-standard-library-core.md`](docs/adr/0001-python-standard-library-core.md) | The language/runtime/packaging boundary is costly to rediscover | A listed re-evaluation trigger fires | Supersede explicitly; never rewrite accepted history silently |
| Kickoff execution and authorization | [`docs/plans/kickoff-plan.md`](docs/plans/kickoff-plan.md) | It proves orchestration, challenge, recovery, gates, and implementation sequence | Historical corrections only after completion | Frozen; new work uses `TASK.md` or a new earned plan |
| Independent review and freshness | [`docs/reviews/`](docs/reviews/kickoff-challenge.md) | Exact pre-challenge identities and stale-resume behavior are acceptance evidence | A new reviewed candidate or replay exists | Freeze each closed round; substantive changes require a new verdict |
| User-visible change history | [`CHANGELOG.md`](CHANGELOG.md) | Users need public semantic changes, not internal work logs | Public behavior or migration changes | Follow release retention; do not list documentation-only churn |
| Causal defect knowledge | [`BUGFIXES.md`](BUGFIXES.md) | A reproduced wording defect could cause callers to destroy display text | A real defect closes or its recurrence guard changes | Retire only when a successor preserves the causal warning |
| Required human-and-agent workspace entry | [`label-normalizer.code-workspace`](label-normalizer.code-workspace) | Gives the owner and agents a named root plus current no-install test commands without changing runtime architecture | Folder layout or canonical setup/test command changes | Merge only into an explicitly user-accepted compatible human workspace replacement |

## Roles deliberately absent

| Optional role/pattern | Disposition | Summary reason | Revisit trigger |
|---|---|---|---|
| Subtree instruction overlay | `OMIT` | One tiny source package and one test tree share the root contract; no local owner, command, or hazard differs | A subtree gains a distinct command, owner, or safety boundary |
| Operational runbook | `OMIT` | There is no service, data store, deployment, credential, incident, or recovery procedure | An operated or credentialed boundary is accepted |
| External-service reference | `OMIT` | Inputs are neither retained nor transmitted; error trackers, analytics, hosting platforms, databases, and dashboards add privacy/cost tax without a decision owner | Remote diagnosis, analytics, persistence, or deployment becomes an accepted outcome |
| Deployment/release runbook and hosted workflow | `OMIT` | Publication and deployment are out of scope; local evidence is sufficient | Distribution or remote availability becomes authorized and required |
| Component-migration plan | `OMIT` | There is one established pure owner, no legacy/new dual path, and no bridge to cut over | A real refactor introduces two temporarily coexisting owners |
| Runtime state-machine ledger | `OMIT` | The function and CLI have no stored state, retries, async completion, lifecycle, or teardown | Stateful lifecycle behavior appears; `docs/invariants.md` must then be expanded or superseded |
| Source/wiring regression pin | `OMIT` | No reproduced recurrence escaped behavior tests; speculative pins would be permanent tax | A real recurrence is reproduced and behavior tests cannot observe its wiring/source shape |

Absence is part of the architecture. Do not create placeholder files for these rows.
Each row above carries its summary reason and revisit trigger; the adoption record
classifies only the techniques it lists. This synthetic example does not carry full
evidence or challenger records for any row.
