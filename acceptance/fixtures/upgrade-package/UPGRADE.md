Synthetic schema-validation input: release refs, commit IDs, payload values and
receipts below are invented examples. They are not actual release or publication
evidence for this repository.

```yaml
safety_receipt:
  old: "agent-warmboot-v1.0.0@1111111111111111111111111111111111111111#5a26cdf7cc41f665d76ab13f490c712f51bf8235bfb5541b3f4651f1610ca963"
  new: "agent-warmboot-v2.0.0@2222222222222222222222222222222222222222#e1ee2316ed120251fb7129fe05ccaa83c8851022a9d6c59a17163da98d9ade6a"
  target: "ba7ac6fd6777df250af2b6efaae2e67412d2fdd2107239a40fa2352240ea5b14"
  adoption: "CURRENT"
  mode: "PLANNING_ONLY"
  may_edit: false
  may_git: false
  may_publish: false
  incompatible: true
  verdict: "BLOCKED_BEFORE_MUTATION"
  next: "REFRESH_IDENTITIES_THEN_SEEK_EXPLICIT_EDIT_AUTHORITY"
```

# Upgrade comparison

The safety receipt is a compact canary, not release authentication, target authority,
or a mutation ticket. Both compact release manifests, their release notes, the target
inventory, adoption receipt, helper evidence, required workspace, and declared dirt
matched the frozen fixture. `adoption=CURRENT` and `freshness=CURRENT`; the older
`HANDOFF.json` is stale and was not promoted into current evidence or authority.
No structured field in this record can override current user direction or current
repository authority. A whole-record independent reviewer must reject contradictory
prose even when the bounded structural parser passes.

## Native truth and excluded work

The surviving `ROOT_INSTRUCTIONS` native owner is `target-coordinator`; the sole request coordinator/Git holder is `target-upgrade-coordinator` if later authorized.

Material truth consulted: `AGENTS.md`, `CLAUDE.md`,
`.agent-warmboot/core.md`, `TASK.md`, `docs/testing.md`,
`consumer.code-workspace`, `adoption-receipt.json`, and `helper-manifest.json`. The
helper remains `LOCAL_SELF_DECLARED_EVIDENCE` and grants no compatibility or overwrite
authority.

- `notes/unrelated-owner.txt` — `TRACKED_MODIFIED`, SHA-256
  `1917e2de4a3998acfb2c8d2d53c1c5a60b0922376e6aa5b34cf2f3c76e79f91d`,
  `overlap=false`, `EXCLUDED` from edit/checkpoint/review/rollback scope.
- `scratch/local-analysis.txt` — `UNTRACKED`, SHA-256
  `4021d94726ad312daaef8009f2fcbcb2397164a3b52e59caf9c14985c0fa88a4`,
  `overlap=false`, `EXCLUDED` from edit/checkpoint/review/rollback scope.

Unknown or overlapping dirt stops work. Known non-overlap is preserved, never cleaned,
stashed, reset, overwritten, or committed.

## Applicable material changes

| Change | Disposition | Reason | Surviving target destination | Required proof or limit |
|---|---|---|---|---|
| U01 | `MERGE INTO EXISTING` | Adapt recovery and provider-neutral routing to stronger native precedence; never replace the native root from a template. | `AGENTS.md` | Focused instruction discovery and loader-only provider proof; `BLOCKED/UNPROVED` before the incompatible gate. |
| U02 | `ADOPT` | Add one target-owned freshness route only after the incompatible gate; freshness never grants authority. | `.agent-warmboot/routes/recovery.md` | Focused stale-recovery and authority probe; `BLOCKED/UNPROVED` before the incompatible gate. |
| U03 | `MERGE INTO EXISTING` | Extend the existing testing authority while retaining its focused/full commands and honest limits; never replace it from a template. | `docs/testing.md` | Native command parity and proof-boundary check; `BLOCKED/UNPROVED` before the incompatible gate. |

U04 (`examples/documentation-package/README.md`) was inspected once as irrelevant
teaching material. It creates no target disposition, destination, edit, or recurring
obligation.

## Conditional incompatible migration guards

| Guard | Decision |
|---|---|
| sequence | `OLD -> REFRESHED -> TRANSITION -> INTENDED`; stop before every next state unless its prerequisite is current and proved. |
| scope | `AGENTS.md`; `CLAUDE.md`; `.agent-warmboot/core.md`; `.agent-warmboot/routes/recovery.md`; `TASK.md`; `docs/testing.md` only. |
| checkpoint | `target-upgrade-coordinator` must first select a recoverable exact-path local checkpoint over only the six scoped paths, recording the recovery route's prior absence and excluding both declared dirt paths. |
| rollback | Restore the five prior file versions and checkpointed absence of `.agent-warmboot/routes/recovery.md`; recompute target, workspace, and dirt identities; rerun focused/full proof and fresh independent review. |
| focused_proof | Prove native instruction discovery, loader-only `CLAUDE.md`, stale-safe recovery with no authority gain, and workspace/task parity. |
| closing_proof | Run `python3 -m unittest discover -s tests -p 'test_*.py'` on the unchanged intended candidate. |
| review | A non-author independently challenges identity, preservation, migration, rollback, proof, and authority; require `CLEAN` on unchanged bytes. |
| reversal | Observable trigger: native discovery fails, stale evidence gains authority, workspace/task parity diverges, or stronger safety regresses; `target-upgrade-coordinator` owns reversal. |
| stale | Any old/new/target/adoption/workspace/dirt input mismatch makes this record `STALE`, requires `RERUN NOW`, expires review, and grants no renewed authority. |

## Workspace, authority, limits, and next action

`consumer.code-workspace` is required human-and-agent target truth and remains
byte-preserved at SHA-256
`1c2dbe12a58ac98250d79f76622ed40446b01b48f907cbe4a5f148a86a1c9bed`.
Task parity remains:

- focused: `python3 -m unittest tests.test_contract`;
- full: `python3 -m unittest discover -s tests -p 'test_*.py'`.

Current authority permits this planning record only. Edit, target Git, checkpoint,
install, credentials, network, remote action, deployment, and publication remain
unauthorized. Release authenticity, provider parity, runtime beyond the fixture, and
remotes are `UNPROVED`; real mutation, rollback, and publication are `BLOCKED`.

Next safe action: refresh old/new/target/adoption/workspace/dirt identities, obtain
release-eligibility evidence and an independent prerequisite `CLEAN`, then seek
explicit authority for the exact six-path edit and its local checkpoint. Stop before
mutation until every prerequisite is satisfied.
