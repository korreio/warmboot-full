# Kickoff independent challenge

> **EXAMPLE REVIEW RECORD.** This frozen record demonstrates a challenge after
> synthesis, finding disposition before implementation, and a bounded verdict.

## Scope and snapshot

- Challenge receipt: `WB-EX-CHALLENGE-001`.
- Scope: the synthesized technology/options brief, proposed ADR, kickoff plan, their
  six attributed lane artifacts, proposed API/CLI, bootstrap, authority, and
  documentation routes.
- Read-only owner: `post-draft-challenger`; distinct from all six discovery
  owners, the coordinator, the fresh resumer, and the later writer.
- Timing: after six lane receipts, coordinator synthesis, and pre-challenge receipt
  [`WB-EX-PRECHALLENGE-001`](kickoff-pre-challenge-receipt.md); before the recovery
  receipt, ADR acceptance, authorization, or implementation.
- Exact reviewed inputs are the three individual files indexed by
  [`EX-KICKOFF-DRAFT-1`](snapshots/example-kickoff-draft-1.md):

| Draft | Frozen input | SHA-256 |
|---|---|---|
| `TECH-DRAFT-1` | [`technology-options-draft-1.md`](snapshots/technology-options-draft-1.md) | `222d77f2d961e070ab9a8f07ce714f58cc1c57e3c6d908977b48fbb80ec85b23` |
| `ADR-0001-DRAFT-1` | [`technology-architecture-adr-draft-1.md`](snapshots/technology-architecture-adr-draft-1.md) | `45e3af35f3e5b678ac6008b4db5dd7dd81ff31db765e7e6090ff69b359bcc613` |
| `PLAN-DRAFT-1` | [`kickoff-plan-draft-1.md`](snapshots/kickoff-plan-draft-1.md) | `2852371c0a68e4d6d892a8f59842d2e4035a6c53a4d031ee5a2e1d2e5a0c87b7` |

- Git/remotes/publication: out of scope.
- Current-SOTA claim: none. The draft makes a bounded choice using dated official
  evidence and records what remains unproved.
- Pre-authorization state at review start: ADR `PROPOSED_FOR_AUTHORIZATION`, plan
  `AWAITING_IMPLEMENTATION_AUTHORIZATION`, `implementation_authorized=false`, and
  `install_authorized=false`.

## Challenge lenses

1. Can the output be mistaken for presentation text?
2. Are context, language, stack/portfolio, tooling, architecture/risk/privacy,
   and testing/bootstrap/package genuinely separate receipts?
3. Were proven portfolio baselines considered without forcing reuse?
4. Do dated official sources support only the claims actually made?
5. Can a clean checkout test and run without hidden dependencies?
6. Does build scope accidentally imply package-install or network authority?
7. Does the CLI or packaging create a second behavior owner?
8. Has the documentation package created recurring ceremony with no trigger?

The challenger explicitly traced three preimplementation gates:

| Gate challenged | Draft evidence | Result |
|---|---|---|
| prerequisite honesty | Drafts asserted Python 3.11+ but named no inspected interpreter or version-matrix run | `F3`; separate declared floor, locally observed version, and unproved versions |
| install reproducibility | ADR/plan proposed an isolated editable-install smoke without proving backend availability | `F2` + `F3`; remove install from acceptance and keep it `UNPROVED` without an explicit grant |
| authorization | plan treated package-manager/environment setup as part of repository build authority | `F2`; require separate install and network/index fields before implementation |

## Round 1 — `FINDING`

### F1 — comparison and display ownership were ambiguous

The phrase “normalized label” could lead a caller to overwrite the original
label even though NFKC and case folding discard presentation distinctions.

Required response:

- define the output as a comparison key in API docs, README, CLI help, and ADR;
- keep display preservation out of the package;
- test compatibility normalization and multi-character case folding; and
- record locale collation/transliteration as non-goals.

### F2 — optional install instructions blurred authority

Describing an editable install beside build work did not prove that the writer
was allowed to install a package or contact an index.

Required response:

- add an explicit implementation receipt after challenge disposition;
- name repository paths and local checks it grants;
- state package installation and package-index/network access separately; and
- keep install evidence `UNPROVED` when those actions are not authorized.

### F3 — prerequisite and reproducibility claims exceeded planned evidence

The draft required Python 3.11+ but planned no 3.11 run, while its packaging
acceptance could be read as reproducible in any clean environment despite an
unproved build backend.

Required response:

- record the actual interpreter used by evidence;
- keep Python 3.11 execution explicit as `UNPROVED` until run;
- make source execution the deterministic required bootstrap; and
- do not infer install reproducibility from metadata parsing or behavior tests.

## Disposition before implementation

- `F1 ACCEPTED`: comparison-key wording, display ownership, Unicode edge tests,
  and non-goals were added to the proposed contract.
- `F2 ACCEPTED`: later receipt `WB-EX-IMPL-001` separately grants repository writes,
  local checks, and an isolated local `--no-deps` install; network/index, Git, and
  publication remain explicitly `NOT AUTHORIZED`. The install tier was not run.
- `F3 ACCEPTED`: the no-install checkout path is acceptance; actual evidence
  names Python 3.14.2, while Python 3.11 execution and editable installation stay
  `UNPROVED`.

The coordinator reconciled the three working artifacts in place, producing
[`TECH-RECONCILED-1`](work/technology-options.md),
[`ADR-0001-RECONCILED-1`](work/technology-architecture-adr.md), and
[`PLAN-RECONCILED-1`](work/kickoff-plan.md). The ADR remained
`PROPOSED_FOR_AUTHORIZATION`; the plan remained
`AWAITING_IMPLEMENTATION_AUTHORIZATION`; and both authorization flags remained
`false`.

## Reconciled challenge check — `CLEAN`

The reconciled planning artifacts satisfy all three challenge dispositions. The
comparison-key owner is singular, portfolio alternatives and solo cost are visible,
the authority split is explicit, and unavailable tiers remain explicit. This verdict
closes the preimplementation challenge only; it does not accept the ADR, grant either
authorization, or claim implementation evidence.

After this reconciliation, distinct `example-fresh-resumer` used the old receipt and
emitted [`WB-EX-RESUME-001`](kickoff-recovery-receipt.md), marking all three old claims
`STALE` and `RERUN NOW`, recording current digests, reloading the artifacts, and
preserving the proposed/awaiting/false pre-authorization state. Only after that receipt
did the decision owner separately accept ADR 0001 and issue the implementation and
installation gates recorded in the [kickoff plan](../plans/kickoff-plan.md).

## Post-implementation review — `CLEAN`

Distinct `example-final-reviewer` reviewed the implemented comparison-key behavior,
thin CLI, documentation links, metadata boundary, and evidence limits. The no-install
behavior, compile, CLI, link, and metadata checks are the accepted local evidence.

**Final verdict: `CLEAN` for this populated example's bounded scope.** This
illustrative record is not a substitute for independent review of the enclosing
toolkit. Python 3.11 execution, Windows, Claude-native replay, editable installation,
package-index access, registry publication, and production remain `UNPROVED` or
`NOT RUN` and are not required by acceptance.

## Documentation adaptation challenge

After the mature portable roles were populated, distinct read-only owner
`example-documentation-challenger` reviewed `ROLE-INDEX.md`, the disposition record,
living standards/testing/system/invariant/documentation routes, workspace tasks,
ADR/plan/study fallout, and release/defect separation. This round did not rewrite the
frozen six-lane or pre-challenge artifact bytes.

Initial verdict: `FINDING`.

- `D-F1`: “too small” did not justify omitting proven architecture. Require exact
  precedent, concrete mismatch, official evidence or honest non-applicability,
  bounded observation, tax/failure comparison, challenge, and reversal trigger.
- `D-F2`: omitting a state-machine ledger must not erase real cross-surface
  invariants. Keep a small behavioral owner but reject invented transitions/rollback.
- `D-F3`: testing must distinguish minimum focused/closing sets, clean reruns, the
  raw-runner/wrapper boundary, and source-pin admission.
- `D-F4`: changelog mixed internal documentation mechanics with user-visible history;
  the causal defect record needed an explicit no-source-pin decision.

All four were accepted and reconciled. The package now shows `ADOPT`, `MERGE INTO
EXISTING`, `CITE ONLY`, and `OMIT`; the invariant ledger contains no fake state; the
test contract says why no wrapper exists; and changelog/defect history have separate
owners.

Reconciled verdict: `CLEAN` for this example's documentation architecture, subject to
refreshed local test/link/JSON/TOML evidence on the unchanged candidate. It does not
claim live portfolio, provider, IDE, install, publication, or deployment behavior.
