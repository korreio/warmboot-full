# Testing and evidence

- Owner: `example-coordinator` while the example is maintained
- Applies to: source, CLI, metadata, workspace command parity, and local docs
- Last executed evidence: Python 3.14.2 on 2026-07-31; see [`TASK.md`](../TASK.md)

## Canonical commands and wrapper boundary

Run from this example root. Required checks use only the standard library and do not
install packages:

| Intent | Canonical project command | Raw/focused diagnostic | Pass proves | Does not prove |
|---|---|---|---|---|
| Core iteration | `python3 -m unittest tests.test_core -v` | individual case: `python3 -m unittest tests.test_core.NormalizeLabelTests.test_uses_unicode_case_folding -v` | named comparison-policy behavior on this interpreter | CLI, package installation, other interpreters |
| CLI iteration | `python3 -m unittest tests.test_cli -v` | individual case: `python3 -m unittest tests.test_cli.LabelNormalizerCliTests.test_prints_one_comparison_key_per_argument -v` | checkout module execution delegates and preserves order/cardinality | installed console entry or other shells/platforms |
| Ordinary closing suite | `python3 -m unittest discover -s tests -v` | `NONE`; this is already the native raw runner with the accepted discovery flags | all nine behavior, adapter, and kickoff-recovery checks in this example | compile, build/install, Windows, provider, external behavior |
| Syntax/import check | `python3 -m compileall -q src tests` | import the affected module in a fresh process | sources/tests parse and compile | semantics |
| Direct smoke | `PYTHONPATH=src python3 -m label_normalizer "  Warm   BOOT  "` | direct `normalize_label` REPL call when diagnosing policy | actual checkout CLI prints `warm boot` | installed entry or broad suite |
| Metadata/workspace | parse `pyproject.toml` with `tomllib` and workspace with `json` | direct field inspection | files are syntactically valid and workspace task matches closing command | build backend availability or IDE execution |

There is deliberately no project test wrapper: no setup, ordering, environment,
service, fixture, cleanup, or flag policy exists beyond the raw `unittest` command.
A wrapper that merely forwards this command would be a second truth and recurring
tax. Add one only when it owns a real prerequisite/cleanup/parity boundary; then the
wrapper becomes closing authority and raw runner use becomes diagnostic only.

## Changed boundary to minimum and closing set

| Changed boundary | Minimum focused set | Required closing set | Escalation trigger | Clean-rerun requirement |
|---|---|---|---|---|
| `core.py` semantics/type error | core module; add/run the smallest red case | full suite + compile | CLI/public docs or cross-version stability affected | fresh Python process from example root |
| `__main__.py` parsing/output | CLI module | full suite + compile; direct smoke for public output | installed entry, shell quoting, encoding, or platform behavior matters | subprocess test supplies explicit checkout `PYTHONPATH` |
| export/package metadata | import/metadata parse | full suite + compile | install/build/registry becomes required | no reused virtual environment for a future install claim |
| kickoff receipt/history | affected recovery test | full suite | any digest, ordering, or authorization state changes | recompute exact bytes before changing recorded digests |
| docs/routes/workspace | local-link and JSON/TOML parse | focused semantic/CLI set only if its contract changed | a command or owner changes | link check against final unchanged candidate |
| runtime/dependency boundary | focused affected behavior | full suite + compile + newly accepted install/platform tier | package, interpreter floor, Unicode stability, licence/security changed | fresh isolated environment owned by one holder when authorized |

A focused red belongs first to its owner. A broad red is not a regression claim until
reproduced on the owning surface and separated from concurrent or environment noise.
After a fix, rerun the failing focused check and the closing set against the final
candidate; a pass over stale files or suspect mutable state is not closing evidence.

## Behavior and ownership matrix

| Hazard/contract | Owning evidence | Current gap and consequence |
|---|---|---|
| repeated/mixed Unicode whitespace | `test_core.py` ordinary case | none for tested examples; exhaustive Unicode property proof not claimed |
| compatibility normalization | full-width core case | other normalization forms are governed by Python docs, not exhaustively enumerated |
| multi-character case folding | `Straße` core case | locale collation/transliteration are explicit non-goals |
| empty/whitespace-only key | core case | caller owns whether an empty key is acceptable domain input |
| stable public type error | exact-error core case | no broader coercion API exists |
| one CLI output per input, same owner | subprocess CLI case | optional installed console entry is `UNPROVED` |
| kickoff digest staleness and authorization order | `test_kickoff_recovery.py` | proves example artifacts only, not provider behavior |
| metadata/entry declaration | TOML parse/inspection | build and editable install remain `UNPROVED` |
| workspace task parity | JSON parse + command comparison | Visual Studio Code task execution remains `UNPROVED` |

## Evidence tiers

| Hazard | Cheapest valid tier | Escalate when | Mutable/singleton holder |
|---|---|---|---|
| local policy | focused unit test | another owner or interpreter boundary is implicated | none; fresh process |
| adapter wiring | subprocess CLI test | installed/platform-specific composition matters | subprocess result: invoking test process |
| whole local repository behavior | full discovery suite + compile | package/environment or platform is required by acceptance | final candidate: coordinator |
| build/install | isolated no-deps local install smoke | backend missing, build isolation downloads, or registry resolution is needed | future `.venv`/build output: one named holder |
| external/provider/platform | separately authorized native observation | never infer it from local evidence | credential/environment/device holder named in task |

The cheapest tier must be capable of seeing the hazard. Full local tests cannot prove
Windows, Python 3.11, Claude-native behavior, IDE task execution, build-backend
availability, package-index access, publication, or deployment.

The core example expectations are literal, independently reasoned normalization cases;
they are not generated by `normalize_label`. Table examples and boundary cases fit this
small deterministic policy better than a new property/mutation dependency. Coverage is
not measured because no current blind-path decision needs a percentage or report. If an
escaped rule defect exposes a broader invariant, first reproduce it red, then choose an
independently derived table/property/metamorphic check and selective mutation probe only
when each adds useful signal. Unit, subprocess-integration, install/platform/external,
and human review evidence stay separately labelled. There are no skipped tests in the
accepted local suite; a future skip must record owner, reason, consequence, and whether
final acceptance remains `UNPROVED` or `BLOCKED`.

## Package-install and external authority

Repository work does not imply permission to:

1. create or mutate an environment;
2. install from the checkout;
3. contact a package index or network endpoint;
4. publish a distribution; or
5. create hosted CI/deployment/service state.

`WB-EX-IMPL-001` authorized an isolated local environment and `--no-deps` checkout
install, but it was not run. Package-index/network, publication, CI, and deployment
were not authorized. Therefore install remains `AUTHORIZED / NOT RUN / UNPROVED`;
authority is not evidence and does not carry to a later task.

## Mutable results and freshness

| Output/resource | Holder | Namespace/state | Retention/cleanup | Collision response |
|---|---|---|---|---|
| Python subprocess and unittest output | invoking check owner | process-local; no shared report file | retain exact command/result in task; process exits | rerun in a fresh process |
| `__pycache__` created by Python | local check owner | inside example source/test trees | non-authoritative disposable cache; never use as evidence | ignore/remove only with scoped authority |
| future virtualenv/build output | explicitly named future holder | unique path, absent for current acceptance | preserve on failure until owner decides; never infer cleanup authority | block or choose new namespace |
| review/digest artifacts | coordinator | exact frozen paths under `docs/reviews/` | immutable after receipt; create a new round | any byte change expires inherited digest/verdict |

Record exact command, snapshot/input, environment, result, and proof limit. A handed-
off pass is `INHERITED` until the snapshot and inputs are checked; changed bytes become
`STALE`/`RERUN NOW`. Unavailable required proof is `UNPROVED` or `BLOCKED`.

## Automation, review, and regression-pin admission

Deterministic behavior and wiring are automated. Semantic fit, display-text ownership,
source-vs-doc authority, and the absence of a justified service/state boundary also
need independent review. Neither substitutes for the other.

The same review reads every changed human-authored code file in full against the
module-docstring rule. Syntax/tests cannot establish immediate orientation or rationale;
missing/stale/decorative/remote-only explanation blocks the scoped close.

This example has no source/wiring regression pin. Admit one only after a reproduced
recurrence passes all of these gates:

- behavior tests cannot observe the relevant source/wiring shape;
- red-before evidence and recurrence signal are recorded;
- one owner, recurring cost, and deletion condition are named; and
- the causal defect ledger explains why the behavior suite was insufficient.

The observed display-wording defect is guarded by behavior tests plus documentation
review; those can observe the contract, so a source pin would be unjustified.
