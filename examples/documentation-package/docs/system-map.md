# System map

Read one matching row, then the owner source and relevant living reference. This map
routes investigation; source/tests remain implementation authority.

- Map owner: `example-coordinator`
- Last verified: final local candidate on 2026-07-31

## Boundary and ownership map

| Area/boundary | Single owner | Invariant | Source/public port | Allowed dependency direction | Cheapest check | Singleton/resource |
|---|---|---|---|---|---|---|
| comparison policy | `core.py` | destructive NFKC → whitespace collapse → casefold comparison key; never display text | `src/label_normalizer/core.py`; `normalize_label(str) -> str` | exports/adapters/callers → core; core → standard library only | `python3 -m unittest tests.test_core -v` | none |
| command adapter | `__main__.py` | one owner-produced output line per argument, in order | `src/label_normalizer/__main__.py`; `main(argv)` | process/argparse → core; never core → CLI | `python3 -m unittest tests.test_cli -v` | subprocess owned by test invocation |
| package/bootstrap | `pyproject.toml` | empty runtime dependencies; source run required, install optional | `pyproject.toml`; console entry delegates to `main` | packaging → adapter; no semantic owner in metadata | TOML parse + full suite | future environment/build dir needs one named holder |
| editor workspace | `label-normalizer.code-workspace` | tasks mirror native commands; no provider/runtime policy | workspace JSON | editor → native commands; docs/commands do not depend on IDE | JSON parse + command parity inspection | IDE session belongs to user/future task holder |
| kickoff/provenance | study + ADR + plan + receipts + adoption record | six lanes precede synthesis; challenge precedes recovery/acceptance; precedent is evidence, not target authority | routed `docs/exploration`, `studies`, `adr`, `plans`, `reviews`, `adoption-disposition.md` | frozen lane/source evidence → coordinator synthesis → independent challenge; never reverse authority | recovery tests + link/digest inspection | coordinator owns task/receipts; reviewers read-only |
| project instructions/docs | `AGENTS.md` + documentation guide | one provider-neutral core; living owners outrank frozen history | root router + `docs/documentation-guide.md` | loader → smallest routed owner | local-link/route check | coordinator owns shared docs |
| source comprehension | module docstrings + local function rationale; exact ADR section for cross-cutting depth | every human-authored code file gives immediate role; consequential decisions remain locally operable | `src/`; engineering standards; ADR normalization-order anchor | source local contract → exact cross-cutting owner, never transcript | complete changed-source non-author read | none |

## Task routing

| Task shape | Minimum context | Cheapest first evidence | Closing/authority limit |
|---|---|---|---|
| change normalization behavior | `core.py`, core tests, invariants, standards §§3–5 | focused core tests | full suite + compile; no cross-version persistence claim |
| change CLI parsing/output | `__main__.py`, CLI tests, README quickstart, invariant row | focused CLI test | full suite + compile + smoke if output changes; installed/platform entry `UNPROVED` |
| change package/bootstrap/workspace | metadata/workspace, README, testing, ADR | JSON/TOML parse and source run | full suite + compile; install/network/IDE execution require separate authority/evidence |
| reconsider language, stack, or service | dated study, ADR, adoption record, [stack comparison](exploration/stack-portfolio.md) | refresh only decision-relevant official sources and run bounded comparison | accepted superseding ADR and explicit gates before implementation/install |
| start/audit/replay kickoff | `AGENTS.md`, `TASK.md`, exploration index, receipts, challenge, plan | recompute exact draft/current digests | coordinator synthesizes only; accepted ADR + explicit flags before writing/installing |
| change docs/process | role index, documentation guide, affected owner | local link/route check | smallest affected native check; no duplicate provider/subtree policy |
| change human-authored code | complete changed file + standards/source rationale | focused behavior + source assessment | full suite/compile + non-author full changed-source read; green tests alone cannot close |
| add stateful, external, or migration behavior | [adoption record](adoption-disposition.md), invariants, ADR triggers | pure policy seam first, then evidence able to see new boundary | state/runbook/service/migration docs only after real owners/hazards are accepted |

## Symptom routing

| Symptom | First owner/path | First boundary question | Do not infer |
|---|---|---|---|
| equivalent labels compare differently | `core.py`, `test_core.py` | NFKC, whitespace, case fold, or a non-goal such as collation? | that every Unicode/locale relation is supported |
| original display typography was lost | caller + README/invariants/BUGFIXES | did caller replace display value with comparison key? | that a correct key is preserved display text |
| CLI differs from library | `__main__.py`, `test_cli.py` | did adapter delegate once per item and print only owner result? | installed console/platform parity |
| editable install is proposed/fails | task authority, metadata, README/testing | were environment/install and network/index separately granted? | metadata parse proves build/install |
| stack/service copied because familiar | study, ADR, adoption record, [stack comparison](exploration/stack-portfolio.md) | is there a concrete target need and complete deviation/adoption proof? | an illustrative reference shape fits this target |
| docs disagree | source/tests, living owner, then ADR/study/plan | which current owner must be corrected, and which history stays frozen? | a dated plan overrides executable truth |
| state-machine/runbook/pin file is proposed | invariants/adoption record | what observed state, operational procedure, or invisible recurrence earns it? | template availability creates a requirement |

## Cross-boundary flows and lifecycle

- CLI arguments → `main` → `normalize_label` → stdout: only the core transforms text;
  CLI tests guard delegation and cardinality.
- Library caller → public export → `normalize_label`: caller retains display text and
  owns whether empty comparison keys are allowed.
- Optional console entry → `main`: declared in metadata; installed parity remains
  `UNPROVED` because install was not run.
- Startup/teardown: no long-lived resources. Each call/process is independent.
- Migration bridge/cutover/rollback: none. A genuine dual path requires a plan with
  parity, cutover, recovery, and deletion conditions before a second owner appears.

## Source-of-truth links

- Behavioral invariants: [`invariants.md`](invariants.md)
- Technology/options and architecture: [`study`](studies/2026-07-31-technology-options.md),
  [`ADR 0001`](adr/0001-python-standard-library-core.md)
- Proven-pattern dispositions: [`adoption-disposition.md`](adoption-disposition.md)
- Active/completed execution: [`TASK.md`](../TASK.md), [`kickoff plan`](plans/kickoff-plan.md)
- Engineering/testing: [`engineering-standards.md`](engineering-standards.md),
  [`testing.md`](testing.md)
- Documentation roles: [`ROLE-INDEX.md`](../ROLE-INDEX.md),
  [`documentation-guide.md`](documentation-guide.md)
- Current merged quality-control loop: [`TASK.md`](../TASK.md) acceptance/review; no
  grade or separate quality file

No operational runbook, subtree overlay, external-service reference, deployment
workflow, component-migration plan, runtime state-machine ledger, or source-pin suite
exists. The role index and adoption record own each omission's summary reason and
revisit trigger; do not create empty files.
