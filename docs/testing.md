# Warmboot Full testing and evidence

Owner: warmboot evidence owner. This is the repository-specific adoption of the
portable [`testing.md`](../templates/project-docs/testing.md) role.

## Changed boundary to minimum focused set

| Changed boundary | Minimum focused evidence | Escalate when |
|---|---|---|
| Core/loaders/maintainer routing | loader/path assertions, local-link scan, self-improvement oracle | discovery, precedence, topology or authority semantics changed |
| Topology/scope revision/review convergence | focused `test_installed_topology_contract_preserves_proportional_role_separation`, `test_review_contract_converges_on_unchanged_non_author_scope`, self-improvement coordinator-owner rejection, and scope-change fixture tests | live agent usefulness, provider behavior, context-pressure recovery, or authorship identity is claimed |
| Bounded worker Git history contract | `tests.test_warmboot.WarmbootCliTests.test_bounded_worker_git_history_contract_is_consistent_and_installed`; inspect the exact attestation/command receipt and external complete-byte manifest when byte preservation is claimed | command/environment/repository shape changes, another Git command is proposed, or a lock/index/ref/config/worktree byte changes |
| Helper/managed bundle | the `tests` helper suite from the `acceptance.md` inventory, plus preview/apply/check on a disposable absolute target; manifest contains no workspace and helper preserves arbitrary workspace bytes | filesystem failure/recovery, platform or installed-byte behavior changed |
| Toolkit Python or style configuration | the two `ruff` lines from the `acceptance.md` inventory | the ruff version or `.ruff.toml` changed |
| Required target-owned workspace | syntax inspection, existing-workspace byte preservation, folder existence and workspace/native-command parity; Warmboot dogfood assertion lives in `tests.test_warmboot` | discovery/omission contract changed (run context-clean cold proof), or target layout/command/debug ownership changed |
| Bootstrap/kickoff schema | the `acceptance/tests` suite and the kickoff oracle on its fixture, both from the `acceptance.md` inventory | cold discovery, owner independence, recovery or authorization changed |
| Source-comprehension contract | `acceptance.tests.test_source_comprehension_oracle` plus kickoff source-rule mutations; non-author reconciles the attested candidate source set and reads every changed human-authored code file | arbitrary target semantics, comment quality, community fit or live agent compliance is claimed |
| Documentation templates/source knowledge | local link/path/privacy/manifest checks and populated example native tests | source fidelity, adoption/deviation or target usefulness changed |
| Optional capability library/local source catalog | the outsider capability-oracle run from the `acceptance.md` inventory, with its all-12 selection and fake-cases inputs, plus focused/helper unit tests | inventory, source identity/rights, discovery, authority/refusal or usefulness changed; run the two-outsider gate |
| Example behavior | that example's native unit tests | shared template or installed contract changed |
| Release manifest/boundary | compact schema plus all 25 paired adversarial classes, conservative short-tag component boundaries, exact four-domain `UNPROVED` semantics and explicit illustrative-only rejection; freeze the exact candidate first, then recompute the path/type/mode/bytes/content aggregate and lineage digests in a dedicated clean verifier checkout. Deterministic tests run from and read that checkout with `python3 -B`; disposable output targets use the dedicated repository-local `.acceptance-work/` children and never selected release paths. | selected bytes, eligible additions, exclusions, lineage/privacy receipts, claims, schema, tag declaration, example/release kind, external receipt or release identity changed |
| Existing-consumer upgrade record | `acceptance.tests.test_upgrade_oracle`, direct compact-record oracle, eight identity/adoption/overwrite/rollback/stale/publication/dirt/workspace canaries, duplicate-JSON/exact-workspace-task/indented-U04/escaped-pipe/state-only-release-summary regressions, a fresh disposable-copy resumer receipt, and whole-record independent review for contradictory prose | release/adoption/target/workspace/dirt identity, disposition, migration, rollback, authority, parser, release-summary, or recovery semantics changed; live agent proof only when discovery/resumption behavior is claimed |
| Provider or trial claim | current provider-native evidence plus the owning receipt routed by the active backlog | relevant behavior, candidate bytes, tool semantics, trial input or provider context changed |

## Deterministic closing set

The commands are owned by [`acceptance.md`](acceptance.md), the single home of the
deterministic command inventory for all five evidence surfaces. Run them from there;
this file keeps no closing-set copy, so a command absent from that inventory is not part
of the closing set. The repository workspace tasks and the CI workflow are tested
mirrors: `tests/test_warmboot.py` holds their commands to that inventory, and the
workflow's helper steps to the README walkthrough.

`.github/workflows/tests.yml` runs the inventory's test suites, fixture oracles and
diagram check, plus the README helper walkthrough, on every push and pull request, on
Ubuntu and macOS with Python 3.11 and 3.15; a separate style job runs the inventory's two
`ruff` lines once, on Ubuntu with Python 3.15. A green run is deterministic evidence for
those runners only.

What this file owns is the selection rule: run the whole inventory for a release
candidate or when the changed-boundary matrix above selects it for architecture,
instructions, bootstrap, provider or acceptance-routing work, and for an ordinary change
run only the focused/native rows that reach its hazards. The current plan or release
receipt records exact commands/counts; this file does not turn pending results into a
claim.

## Live cold-start and recovery gates

For architecture, instruction discovery or loader, bootstrap, provider,
acceptance-routing or acceptance-machinery, or release-boundary changes, the current
coordinator chooses the smallest clean live evidence that proves the hazard after
exploration. A before/after comparison, identical input bytes, fresh agents or a fresh
resumer remain useful when the claim actually depends on them; historical prompts,
fixtures and scenario digests are not mandatory inputs. Any chosen fresh agent
must discover the right authority, preserve Git/singleton ownership and stop at the
stated authorization boundary. A chosen resumer must reject stale receipts, reload
current truth and grant no new authority.

Record owner identities, paths, revision, prompts, outputs, interventions, natural
failures, review verdict and practical utility. A fixture oracle is not a substitute
for this live evidence. Reusing an implementation agent or exposing baseline findings
to the after agent invalidates the comparison.

When the bootstrap workspace discovery/omission contract changes, a context-clean
after agent receives the same objective/authority prompt and a clean candidate target
without implementation reasoning or the baseline output. For a fresh target with no
accepted replacement, require exactly one regular root `*.code-workspace`, a named
existing root folder, target-owned task/adoption evidence, no `OMIT`/`CITE ONLY`, only
current safe command/folder entries, no speculative launch, no forbidden external or
credential action, intact planning stop, zero owner intervention for discovery, and
final independent `CLEAN`. Deterministic helper/workspace checks prepare that proof but
cannot replace it.

When the optional capability boundary changes materially, run the hardware-free
[outsider gate](acceptance.md#optional-capability-cold-outsider-gate).

## Evidence limits and stop rules

Review test evidence for assertion sensitivity, independent expectations and fixture
independence. Keep unit, integration, consumer/provider contract, end-to-end, external,
and human evidence separate; database or other environment-gated tests do not become a
pass by being skipped. Every skip needs a reason, owner, consequence, and final-
acceptance disposition. Use coverage to locate blind critical paths, never as a gamed
percentage. Select property/metamorphic checks and mutation testing only where their
incremental signal justifies their cost. An escaped defect is reproduced red before its
smallest behavior regression is retained.

Independent reviewers also inspect stale/misleading rationale, undocumented high-risk
invariants, and whether a human owner can locate and challenge intent. Machine checks do
not prove human comprehensibility. For every code change, the coordinator attests the
frozen candidate source set
([`routes/context.md`](../routes/context.md#candidate-source-set-attestation))
and the writer reconciles its assessment against it. The non-author reviewer repeats
that reconciliation and reads every resulting human-authored code file in full against
the adopted language-native rule; an omitted file is a `FINDING`. Tests, remote ADRs, a
quality score or the fixture oracle cannot substitute for that review.

- Deterministic unit/oracle proof covers only named bytes and invariants.
- The source-comprehension oracle checks independently declared literal evidence in four
  tiny synthetic Java cases only. It is not a parser, comment counter, comment-quality
  classifier or target linter; the target-owned rule and non-author complete-source read
  remain the operating gate.
- The WB-016 semantic pin proves the documented allowlist/denylist and installed
  contract agree. It does not prove Git commands byte-preserving on another Git
  version, repository/config/filesystem shape, provider, or platform. Use a disposable
  canary or complete external before/after byte manifest when that claim is required.
- Clean example proof does not prove a different target's architecture.
- Local CLI proof does not prove hostile filesystems, every OS, remote provenance or
  package ecosystems. Its `APPLIED`/`PASS` result deliberately proves nothing about
  completion or usefulness of the target-owned human workspace. Other actors must not
  relocate opened parents during installation: a rename after validation can move a
  directory outside the target before a write, which the helper detects only afterward;
  its preservation warnings then say that recorded paths may have moved.
- The capability oracle proves exact inventory and hashes, non-executable
  library files, selection isolation, attested-root
  repository JSON loading, source-rights inheritance, twelve design entries,
  exact card/source mappings, duplicate-key rejection, ordered canonical card
  source fields, privacy canaries and local fake decisions only. It does not
  prove legal advice, future rights, live operations, provider behavior or a
  real target's usefulness.
- One provider's evidence does not prove another provider or general parity. The
  current task owns any live claim and exact input identity.
- No remote, hosted, deployment, private-data or source-write test runs without exact
  authority. The one authorized hosted tier is the owner-authorized deterministic CI
  workflow: push and pull request, Ubuntu and macOS, Python 3.11 and 3.15, read-only
  token, SHA-pinned actions, no persisted checkout credentials. It never gates or
  replaces release proof.

Missing required evidence is `UNPROVED`; missing authority/input that prevents safe
progress is `BLOCKED`. A high-risk unresolved finding blocks release. Do not replace
unavailable native proof with more prose or speculative tests.
