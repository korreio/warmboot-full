# Engineering standards

> **EXAMPLE ONLY.** These standards are the portable subset this small project
> actually adopted. The frozen portfolio standards remain precedent, not target
> commands. Literal compliance that makes the outcome worse uses the named escape
> and decision owner; it is never hidden in another abstraction.

- Owner: `example-coordinator` while this example is maintained
- Applies to: `src/`, `tests/`, `pyproject.toml`, workspace tasks, and same-change docs
- Architecture authority: [`ADR 0001`](adr/0001-python-standard-library-core.md)
- Proven-pattern decisions: [`adoption-disposition.md`](adoption-disposition.md)

## 1. Technology baseline

- Runtime: Python `>=3.11`, declared in `pyproject.toml`; only Python 3.14.2 was
  actually exercised, so 3.11 execution remains `UNPROVED`.
- Runtime dependencies: none. Standard-library `unicodedata`, `argparse`, and
  `unittest` own the accepted implementation/test capability.
- Package metadata: `pyproject.toml`; optional build backend `setuptools>=68`.
  Metadata syntax does not prove backend availability or installation.
- Required bootstrap: source execution from the checkout. Installation, package-index
  access, registry publication, and deployment are independent gates.
- Editor entry: `label-normalizer.code-workspace` exposes the same native closing
  suite and compile command; it adds no runtime or provider requirement.

Changing language, runtime floor, dependency policy, package manager/lock strategy,
or required-install boundary requires dated official evidence, a superseding ADR,
an updated disposition record, solo-maintainer tax/failure comparison, and independent
challenge. “Cleaner”, “newer”, or personal preference is not proof.

## 2. Rule strength and proportional escape

| Rule | Strength | Applies at | Enforcement/evidence | Escape and owner |
|---|---|---|---|---|
| Full no-install suite closes any source/CLI change | `HARD GATE` | `src/`, `tests/` | `python3 -m unittest discover -s tests -v` | None while this is the accepted closing contract; change acceptance via ADR/task first |
| Sources and tests compile | `HARD GATE` | `src/`, `tests/` | `python3 -m compileall -q src tests` | Only if a replacement compiler/import gate proves the same boundary; decision owner records it |
| Runtime dependency list remains empty | `HARD GATE` for current ADR | source imports and `pyproject.toml` | manifest/import inspection plus full suite | Supersede ADR 0001 with benefit, licence/security/update/removal proof |
| One normalization owner, thin adapters | `REVIEW HEURISTIC` | public library and process entry points | source inspection + focused core/CLI tests | A second owner requires a real platform/caller constraint and parity/migration plan |
| Pure policy before I/O | `REVIEW HEURISTIC` | transformation behavior | source inspection + core tests | External state is allowed only behind a named port after it becomes an accepted outcome |
| Every human-authored code file gives immediate module orientation; consequential choices keep local rationale | `HARD GATE` | `src/` | writer assessment + non-author full changed-source read; tests cannot substitute | Generated/vendor/mechanical exception only, recorded in the task |
| Public functions use types and concise semantic docstrings | `CONVENTION` | public API | review | Omit where the language/tooling makes the contract more obvious without prose |
| Keep changes causal and extend existing owners | `CONVENTION` | repository | review + task closeout | A new component/doc must name a distinct reader, owner, trigger, tax, and retirement rule |

A hard gate blocks the scoped claim. A review heuristic requires a reviewer to
dispose an exception. A convention is a default, not fake automation. Delete any rule
that no longer changes implementation, proof, or review.

### Human inspectability

Python's community-native module docstring is the target-owned immediate orientation for
every human-authored code file; one sentence suffices for the simple export and CLI
adapter. Public docstrings and the normalization-order rationale explain semantic
constraints, not syntax. The README, invariant ledger and ADR organize cross-cutting
intent so the human owner can challenge why NFKC precedes whitespace collapse and case
folding without reconstructing kickoff transcripts. A stale or code-restating comment is
corrected or removed. This tiny project needs no SLOC threshold or architecture diagram;
adopt either only after a cohesion/findability problem and with a review trigger, text
alternative, owner and update condition.

Before handoff the coordinator attests the frozen candidate source set, and the writer
lists and assesses every changed human-authored code file against it. The non-author
reviewer repeats that reconciliation, reads every file in full and returns `FINDING` for
an omitted file or for missing, stale, decorative or remote-only explanation even when
tests pass. Tests and the ADR deepen but do not replace the local file contract.
Untouched debt is recorded by consequence rather than inferred from counts. This tiny
project merges its current quality-control loop into `TASK.md` and final review:
architecture/ownership, source comprehension and test evidence are checked;
security/privacy/operations remain explicitly inapplicable except the transient-input
boundary. No letter grade or separate assessment file is earned.

## 3. Behavioral invariants

The living detail is [`invariants.md`](invariants.md). The load-bearing summary is:

1. `normalize_label` produces an intentionally destructive comparison key; callers
   keep original display text.
2. Order is NFKC normalization, Unicode-whitespace collapse, then case folding.
3. The CLI emits one owner-produced key per input argument, in input order.
4. The library is pure: no filesystem, environment, network, clock, logging, or
   process output.
5. No stable-key promise crosses Python/Unicode database versions.

## 4. Components, ports, composition, and teardown

| Boundary | Single owner | Public port / direction | Pure policy seam | Composition / teardown | Focused proof |
|---|---|---|---|---|---|
| comparison policy | `src/label_normalizer/core.py` | `normalize_label(str) -> str`; adapters/callers depend inward | same function; no I/O | library export re-exports owner; no teardown | `python3 -m unittest tests.test_core -v` |
| command adapter | `src/label_normalizer/__main__.py` | arguments/stdout depend on core; core never imports process concerns | delegates every item to core | `main` builds parser; process exit is composition; no long-lived resource | `python3 -m unittest tests.test_cli -v` |
| optional packaging | `pyproject.toml` | console entry points to `label_normalizer.__main__:main` | never owns semantics | build/install lifecycle is authority-gated; installed execution `UNPROVED` | TOML parse/inspection only |

Do not manufacture an interface around the one function. A named port is earned when
an external boundary exists or two implementations must be selected. For a genuine
phased isolation, the active plan must name old/new owners, temporary bridge, entry
gate, parity proof, cutover, rollback/forward-recovery, and bridge deletion. None is
present here; component-migration apparatus is explicitly `OMIT`.

## 5. Change-to-proof contract

| Changed boundary | Minimum focused set | Closing set | Documentation fallout | Escalate when |
|---|---|---|---|---|
| normalization semantics/type boundary | `python3 -m unittest tests.test_core -v` | full suite + compile | README/invariants; changelog if public; BUGFIXES only for a reproduced fix | CLI contract or interpreter-version stability is affected |
| CLI arguments/output/exit | `python3 -m unittest tests.test_cli -v` | full suite + compile + direct smoke when output wording changes | README/system map; changelog if public | installed entry parity or platform quoting matters |
| package metadata/bootstrap | TOML parse + import/source run | full suite + compile | README/testing/ADR if boundary changes | build/install/registry evidence becomes required |
| docs/routes/workspace | local link check + JSON parse | smallest affected native check; full suite if command/semantics changed | role index/documentation guide/task | a route or workspace command disagrees with native truth |
| language/runtime/dependency | focused affected behavior | full suite + compile + newly required tier | dated study, ADR, disposition, README, testing, task | current official evidence, migration, licence/security, or platform proof is missing |

Focused evidence diagnoses the owner. It is not closing evidence unless the current
contract explicitly says so. The exact wrapper/raw-runner choice and clean-rerun rules
live in [`testing.md`](testing.md).

## 6. Dependency, data, and external-effect safety

- Runtime dependency additions are architecture changes, not casual imports. Record
  capability, licence, security/update owner, lock/resolution strategy, degraded mode,
  migration/removal path, and native evidence.
- Input labels are transient process data. Do not log, retain, transmit, analyze, or
  attach them to remote diagnostics without a new privacy/data decision.
- Source/test work does not authorize environment creation, installation, index or
  network access, credentials, Git, publication, hosted CI, registry, or deployment.
- No secret belongs in source, docs, workspace tasks, fixtures, or command examples.
  If a future boundary needs one, document the variable name/owner only.
- Preserve unrelated work. The coordinator alone mutates Git and owns checkpoints,
  refs/configuration, Git-mediated worktree administration, remotes, and credentials.
  If local history changes a bounded worker/reviewer decision, its initial assignment
  must attest the exact repository, refs/ancestry, pathspecs, and exact command. Every
  invocation uses `GIT_OPTIONAL_LOCKS=0` or `git --no-optional-locks`; only
  `git rev-parse --verify`, `git status --short --untracked-files=all`,
  `git --no-pager log`, `git --no-pager log --follow`,
  `git --no-pager show --no-ext-diff`, and `git --no-pager blame` are eligible. Every
  `git diff` form and every unlisted/mutating/remote/configuration command is excluded.
  This example's current task records that bounded history inspection is not required.

## 7. Testing and regression pins

- Add the smallest behavior test that fails for the changed rule, then rerun the
  applicable closing set from a fresh process.
- Ordinary behavior tests own semantic recurrence. Do not replace them with source
  text assertions merely because source checks are easy.
- Admit a source/wiring pin only after an observed recurrence cannot be seen by
  behavior tests. Record owner, reproduced red-before signal, insufficiency, exact
  recurrence boundary, recurring tax, and deletion condition in the causal defect
  record and test header.
- This example has no admitted source/wiring pins. That absence is a reviewed `OMIT`,
  not missing coverage.
- Broad failures stay owned by the broad-run holder until reproduced on the owning
  surface or classified as infrastructure/concurrent noise.

## 8. Error, recovery, and honest evidence

- Public type misuse raises `TypeError("value must be str")` exactly.
- CLI argument errors use `argparse`; the library never prints or exits.
- Every report records exact command, environment/snapshot, result, and limit.
- Inherited evidence is `INHERITED` until its inputs are checked. Changed inputs make
  it `STALE` and `RERUN NOW`. Missing required evidence is `UNPROVED` or `BLOCKED`.
- A lower tier never substitutes for unavailable install, platform, provider,
  external-account, publication, or deployment evidence.

## 9. Documentation and release fallout

- Public comparison semantics/non-goals → README, core docstring/tests, invariants,
  changelog, and system route when ownership changes.
- Reproduced defect → causal `BUGFIXES.md` entry; not every implementation edit.
- Rule/command/evidence meaning → standards/testing and matching workspace task.
- Durable architecture choice → dated study, disposition, accepted/superseding ADR,
  and active plan/task.
- User-visible history belongs in `CHANGELOG.md`; internal documentation or review
  churn belongs in `TASK.md`/plan/review. A version heading never implies a Git tag,
  registry package, deploy, or release.

## 10. Review and retirement

After the one-time intensive proportional kickoff, every code change and
other material work uses one writer and an independent read-only
non-author reviewer. On `FINDING`, a separate writer
fixes accepted findings, reruns affected evidence, and returns unchanged corrected bytes
for rereview until no actionable finding (`CLEAN`) or honest `BLOCKED`. Any relevant
decision, byte, or evidence change expires clean credit; a review count does not replace
this convergence.

Remove preferences, empty abstractions, obsolete pins, duplicate docs, wrappers, and
workspace settings when they stop changing a decision. Mature standards preserve earned
conclusions; they do not preserve obsolete project-specific assumptions or permanent
ceremony.
