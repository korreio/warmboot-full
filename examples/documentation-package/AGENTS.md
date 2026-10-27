# Working contract — documentation-package example

> **EXAMPLE ONLY.** This populated project demonstrates how a fresh agent can
> take ownership after reading the repository. It is not the toolkit's own
> contract and its technology choice is not a default for another project.

`AGENTS.md` is the provider-neutral, always-load safety core. `CLAUDE.md` only
points here. Keep this file short; route detail through
[`docs/system-map.md`](docs/system-map.md).

## Start

1. Read [`TASK.md`](TASK.md), inspect the working tree, and reuse the current task
   record. Preserve unrelated work and stop on unclear overlap.
2. Record authority explicitly. Read-only local discovery is allowed. Git
   writes, publishing, network changes, credentials, package installation, and
   destructive cleanup require a task-specific grant.
3. For a new-project kickoff, the initial agent is **orchestration-only**. It
   covers six independent read-only concerns through the smallest proportional set
   of at least two distinct non-coordinator research owners, then uses a distinct
   non-author post-draft challenger. Two research owners are a floor, not a target;
   risk drives additional separation:

   | Order | Concern owner | Question owned |
   |---|---|---|
   | 1 | context owner | objective, users, constraints, success, and non-goals |
   | 2 | language owner | language options and decision-relevant current official evidence |
   | 3 | stack + portfolio owner | fit of proven portfolio baselines, combinations, novelty, and recurring solo cost |
   | 4 | tooling owner | local tools, versions, editor/workspace, build/test entry points, and maintenance cost |
   | 5 | architecture + risk + privacy owner | truth ownership, boundaries, hazards, data handling, security, and failure modes |
   | 6 | testing + bootstrap + package owner | prerequisites, cheapest-valid evidence, clean start, and install/network boundaries |
   | 7 | distinct non-author challenger | independently challenge the synthesized draft, exclusions, authority, and acceptance |

   Concern-owner labels may repeat while every concern retains an attributed artifact
   and receipt. Destructive/high-risk work separates architecture/risk/privacy from
   testing/bootstrap/operability; lower-risk work may merge them only when it records why
   merging is safe and assigns explicit challenger cross-checks. The coordinator
   synthesizes concern receipts; it does not
   silently perform research. Immediately before challenge, record exact individual SHA-256 digests for
   the draft brief, ADR, and plan. After challenge disposition changes the working
   artifacts, a distinct fresh resumer must mark the inherited claims `STALE` and
   `RERUN NOW`, reload them, and refresh their digests while the ADR remains
   `PROPOSED_FOR_AUTHORIZATION`, the plan remains
   `AWAITING_IMPLEMENTATION_AUTHORIZATION`, and both authorization flags remain
   `false`. That receipt refreshes evidence only.
   Owner evidence is routed from the kickoff-only
   [`exploration index`](docs/exploration/README.md); coordinator synthesis is in
   [`docs/studies/2026-07-31-technology-options.md`](docs/studies/2026-07-31-technology-options.md).
4. Only after challenge disposition and the refreshed pre-authorization receipt may
   the decision owner separately accept the ADR and set explicit implementation and
   installation gates. Before assigning a writer, the final receipt names the writer,
   owned paths, permitted checks, and excluded effects. Package installation and
   package-index/network access are separate permissions; neither is implied by build
   scope.
5. Route the task through the smallest matching row in
   [`docs/system-map.md`](docs/system-map.md), then read the owner source and only
   the relevant living references. Use ADRs, studies, plans, and reviews for the
   decision or history they actually own.
6. Before editing, leave one compact context receipt naming the route, owner,
   checks, owned paths, and excluded effects.

During bootstrap, classify useful document roles with the populated
[`ROLE-INDEX.md`](ROLE-INDEX.md). Applicable portfolio precedent starts as `ADOPT`
or `MERGE INTO EXISTING`; any `CITE ONLY`, `OMIT`, or novel replacement must satisfy
the evidence/challenge/reversal burden in
[`docs/adoption-disposition.md`](docs/adoption-disposition.md). Incomplete material
deviation evidence blocks implementation and installation.

## Invariants

- Prefer the existing owner and the smallest causal change. Do not add a second
  representation, lifecycle, or abstraction for a hypothetical caller.
- One named coordinator owns synthesis and the task record and is the sole Git
  mutator/checkpoint/remote/credential holder. When local history changes a bounded
  worker/reviewer decision, its initial assignment may attest one exact local
  repository/ref/ancestry/pathspec and commands. Every invocation uses
  `GIT_OPTIONAL_LOCKS=0` or `git --no-optional-locks`; only
  `git rev-parse --verify`, `git status --short --untracked-files=all`,
  `git --no-pager log`, `git --no-pager log --follow`,
  `git --no-pager show --no-ext-diff`, or `git --no-pager blame` is eligible. Every
  `git diff` form is excluded. One named holder owns each other scarce or mutable
  resource; workers never stage, commit, push, publish, or mutate shared singleton
  outputs.
- Use the cheapest evidence that can see the relevant hazard. Report exact
  commands and results; label required but unavailable proof `UNPROVED` or
  `BLOCKED`.
- Independent reviewers are read-only and return exactly `CLEAN`, `FINDING`, or
  `BLOCKED`, with path/line evidence. Any substantive fix expires a prior clean
  verdict.
- Add a regression pin only for an observed recurrence that behavior tests
  cannot see. Name its owner, recurrence signal, insufficiency, and deletion
  condition.
- Update documentation only when its contract changed: ownership changes update
  the system map; behavior changes update tests and release notes; a durable
  decision gets an ADR; a resolved defect gets a bugfix record.

## Routes

| Need | Read next |
|---|---|
| understand ownership or a symptom | [`docs/system-map.md`](docs/system-map.md) |
| find retained and deliberately absent roles | [`ROLE-INDEX.md`](ROLE-INDEX.md) |
| change a cross-surface behavior contract | [`docs/invariants.md`](docs/invariants.md) |
| change code or review quality | [`docs/engineering-standards.md`](docs/engineering-standards.md) |
| choose or interpret evidence | [`docs/testing.md`](docs/testing.md) |
| add, move, or retire documentation | [`docs/documentation-guide.md`](docs/documentation-guide.md) |
| inspect proven-pattern adoption or a deviation | [`docs/adoption-disposition.md`](docs/adoption-disposition.md) |
| inspect the six concern records from this project's historical kickoff | [`docs/exploration/README.md`](docs/exploration/README.md) |
| inspect technology/options evidence | [`docs/studies/2026-07-31-technology-options.md`](docs/studies/2026-07-31-technology-options.md) |
| understand the accepted technology choice | [`docs/adr/0001-python-standard-library-core.md`](docs/adr/0001-python-standard-library-core.md) |
| inspect the completed kickoff and authorization | [`docs/plans/kickoff-plan.md`](docs/plans/kickoff-plan.md) |
| inspect the independent challenge | [`docs/reviews/kickoff-challenge.md`](docs/reviews/kickoff-challenge.md) |

## Finish

Update `TASK.md` with changed paths, evidence actually run, review verdict,
assumptions, unproved remainder, and next authorized action. Stop when acceptance
and proportional review are satisfied.
