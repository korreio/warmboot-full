# Kickoff exploration and implementation plan

> **EXAMPLE ONLY.** This completed mechanics/evidence ledger is frozen after the
> kickoff scenario. Its owners, receipts and outputs are invented teaching records;
> actual results for current bytes belong to the toolkit current task. Current behavior
> lives in code, tests, README and living references.

## 1. Prerequisites and initial authority

- Objective and acceptance are recorded in `TASK.md`.
- Existing project files and concurrent changes are inspected before delegation.
- `example-coordinator` is orchestration-only through discovery, synthesis, and
  challenge disposition; it does not act as a hidden lane owner or writer.
- Discovery and challenge are read-only.
- Package installation, package-index/network access, Git, remotes, publication,
  deployment, and destructive cleanup are outside initial authority.
- Python 3.11+ must be locally available. Missing Python is a bootstrap blocker,
  not permission to install it globally.
- Initial ADR state: `PROPOSED_FOR_AUTHORIZATION`.
- Initial plan state: `AWAITING_IMPLEMENTATION_AUTHORIZATION`.
- Initial flags: `implementation_authorized=false`; `install_authorized=false`.

## 2. Six independent discovery lanes

Each owner returns a conclusion, evidence or source links, assumptions, and
`UNPROVED` boundaries—not a file dump.

| Order | Named owner | Owned question | Receipt |
|---|---|---|---|
| 1 | `context-owner` | Who needs this, what exact outcome matters, and what is out? | [`CONTEXT-01`](../exploration/context.md): comparison keys only; original display values remain outside; no operated-product scope. |
| 2 | `language-owner` | Which language directly expresses the required semantics with current official evidence? | [`LANGUAGE-01`](../exploration/language.md): Python's documented Unicode primitives fit; no general superiority claim. |
| 3 | `stack-portfolio-owner` | Which invented reference shape fits this example, and what upkeep would it add? | [`STACK-01`](../exploration/stack-portfolio.md): hypothetical service/application boundaries are oversized; choose the small Python boundary. |
| 4 | `tooling-owner` | Which local tools, versions, editor/workspace, build, and test entries are justified? | [`TOOLING-01`](../exploration/tooling.md): stdlib tests/CLI/compile, plain files, one metadata surface; optional install remains separate. |
| 5 | `architecture-risk-privacy-owner` | Where is truth owned, what can fail, and what data crosses which boundary? | [`ARCH-01`](../exploration/architecture-risk-privacy.md): one pure owner + thin CLI; destructive display misuse is the main risk; no retention/transmission. |
| 6 | `testing-bootstrap-package-owner` | What prerequisites and cheapest-valid evidence prove a clean start; what install authority is needed? | [`TEST-01`](../exploration/testing-bootstrap-package.md): no-install red/green path; package install and network/index are separate grants. |

Decision-relevant detail and illustrative source titles are preserved in
[`../studies/2026-07-31-technology-options.md`](../studies/2026-07-31-technology-options.md).

## 3. Coordinator synthesis, then seventh-lane challenge

`example-coordinator` synthesized the six receipts into three working drafts. Immediately
before challenge it emitted
[`WB-EX-PRECHALLENGE-001`](../reviews/kickoff-pre-challenge-receipt.md), which records
separate SHA-256 identities for the exact
[`technology/options brief`](../reviews/snapshots/technology-options-draft-1.md),
[`ADR`](../reviews/snapshots/technology-architecture-adr-draft-1.md), and
[`plan`](../reviews/snapshots/kickoff-plan-draft-1.md). Only after that receipt existed
did `post-draft-challenger` independently review all three as
`WB-EX-CHALLENGE-001`.

The challenger returned `FINDING`:

- `F1`: “normalized label” could be misused as preserved display text.
- `F2`: optional install prose could be mistaken for implementation or network
  authority.
- `F3`: the Python floor and editable-install reproducibility claims exceeded
  the evidence planned for the actual environment.

Disposition before implementation:

- `F1 ACCEPTED`: use “comparison key,” keep display preservation outside, test
  NFKC and multi-character case folding, and publish semantic non-goals.
- `F2 ACCEPTED`: add a task receipt that separately states repository-write,
  local-check, package-install, package-index/network, Git, and publication
  authority.
- `F3 ACCEPTED`: accept source execution as the required deterministic
  bootstrap, record the actual interpreter, and leave Python 3.11 plus editable
  installation `UNPROVED` until separately run.

The exact [`EX-KICKOFF-DRAFT-1`](../reviews/snapshots/example-kickoff-draft-1.md)
index records the three individual digests. The coordinator then dispositioned every
finding and reconciled the three working artifacts. No implementation work began.

## 4. Fresh-resumer recovery receipt

After challenge reconciliation, distinct `example-fresh-resumer` received the old
pre-challenge receipt. It recomputed all three current working-artifact digests, marked
all inherited claims `STALE` and `RERUN NOW`, reloaded the reconciled artifacts, and
emitted [`WB-EX-RESUME-001`](../reviews/kickoff-recovery-receipt.md).

The refreshed receipt explicitly preserved this state:

- ADR: `PROPOSED_FOR_AUTHORIZATION`;
- plan: `AWAITING_IMPLEMENTATION_AUTHORIZATION`;
- `implementation_authorized=false`;
- `install_authorized=false`.

That receipt refreshed evidence only. It did not accept the ADR or grant either
authorization.

## 5. Separate decision acceptance and authorization

Only after `WB-EX-RESUME-001`, decision owner `example-coordinator` separately accepted
[`ADR 0001`](../adr/0001-python-standard-library-core.md). It then issued
`WB-EX-IMPL-001`, changing the final plan gates to:

- Implementation gate: `AUTHORIZED`;
- Package-installation gate: `AUTHORIZED`;
- `implementation_authorized=true`;
- `install_authorized=true`.

Package-index/network access remained `NOT AUTHORIZED`. Installation authority covered
only an isolated local environment and `--no-deps` installation from this checkout; it
was granted explicitly so the gate was not implicit, but the optional tier was not run
and remains `UNPROVED`.

### Authorized topology and receipt

The code has one coupled invariant, so parallel writers would create overlap.
Topology shrank to one writer plus one independent read-only reviewer.

Receipt `WB-EX-IMPL-001`:

| Field | Authorized boundary |
|---|---|
| issuer | `example-coordinator` |
| writer | `example-writer` |
| exact scope | all source, test, metadata, and documentation paths inside this example repository only |
| permitted checks | local Python tests, compile, CLI, link resolution, and TOML parsing |
| implementation | `AUTHORIZED` |
| package installation | `AUTHORIZED` only for an isolated local environment and `--no-deps` install from this checkout; `NOT RUN` |
| package-index/network access | `NOT AUTHORIZED` |
| Git/remotes/publication/deployment/destructive cleanup | `NOT AUTHORIZED` |

## 6. Ordered implementation

1. **Red contract:** add behavior and CLI tests; run the full suite before source
   exists and record the expected import failure.
2. **Pure owner:** add `normalize_label` with NFKC, whitespace collapse, case
   folding, and the stable type boundary.
3. **Adapter/metadata:** add the CLI and package metadata without duplicating the
   normalization rule or installing a build backend.
4. **Documentation fallout:** populate startup, role index, disposition evidence,
   routing, behavioral invariants, standards, testing, documentation lifecycle,
   workspace, study, changelog, bugfix, ADR, plan, and review. Explicitly omit
   unearned overlays, runbooks, services/deployments, state/migration, and pins.
5. **Verify:** run full tests, compile, CLI smoke, link inspection, and TOML parse.
6. **Review:** an independent reviewer returns `CLEAN`, `FINDING`, or `BLOCKED`;
   any substantive fix resets the clean verdict.

## 7. Bootstrap and authorized but unexercised install tier

Accepted no-install path:

```sh
python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m label_normalizer "  Warm   BOOT  "
```

The README documents an optional editable-install path. `WB-EX-IMPL-001` authorized a
strictly local isolated install from this checkout, but the example did not run it.
Authorization is not evidence: editable installation remains `UNPROVED`. If Python or
the local build backend is missing, stop and report the prerequisite; package-index,
global installation, and network access remain outside authority.

## 8. Evidence matrix

| Claim | Evidence | Limit |
|---|---|---|
| tests detect missing implementation | same full command before source exists | import failure proves red, not behavior quality by itself |
| normalization semantics | full unit suite | tested interpreter only |
| adapter delegates correctly | subprocess CLI test | local process only |
| sources import | compileall | no behavior claim |
| metadata is syntactically readable | `tomllib` parse | no build/install claim |
| package installs | none | `AUTHORIZED / NOT RUN / UNPROVED`; network/index access remained unauthorized |
| docs navigate | local Markdown link resolution | local paths only |
| workspace is syntactically valid and command-aligned | JSON parse + task/native-command comparison | does not prove IDE execution |
| precedent dispositions are complete | local reference-shape comparison + target checks + adaptation challenge | invented comparisons prove no outside source or service state |

## 9. Build record

| Step | Result |
|---|---|
| red-first full test | `ILLUSTRATIVE: expected red; 2 discovered, 1 failure + 1 import error with production source absent` |
| implementation | one pure owner, one thin CLI, no runtime dependencies |
| restored full test | `ILLUSTRATIVE: 9 passed on Python 3.14.2, including 3 recovery-contract checks` |
| compile/CLI | `ILLUSTRATIVE: compile exit 0; CLI exit 0 and printed warm boot` |
| documentation/metadata | `ILLUSTRATIVE: 189 example-local Markdown link occurrences resolved on the expanded candidate; pyproject TOML and workspace JSON parsed; tasks match canonical commands` |
| optional install | `AUTHORIZED / NOT RUN / UNPROVED`; no package-index/network authority |
| independent review | populated challenge record reached `CLEAN`; enclosing toolkit review remains separate |

## 10. Completion and retirement

Freeze this plan when `TASK.md` contains actual evidence and a final review
verdict. Do not keep updating it for ordinary feature work; route to living docs
and create a new plan only for a genuinely multi-step change.
