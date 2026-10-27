# Warmboot Full maintainer system map

Owner: warmboot maintainer coordinator. This map describes this repository, not an
installed target.

## Three planes, one authority

| Plane | Owned surfaces | May change | Must not become |
|---|---|---|---|
| Maintainer | `MAINTAINING.md`, root `ROLE-INDEX.md`, root history, ADRs, studies/plans, source refresh, acceptance and release records | The evolving toolkit and its evidence | A second improver repository, copied policy tree, or automatic consumer payload |
| Consumer kit | `WARMBOOT.md`, `routes/`, templates, optional helper, required target-owned workspace seed/contract, opt-in capability library and teaching examples | A candidate for selective target adoption | Project truth without target inspection and role/source disposition |
| Frozen release | One immutable annotated release tag plus the compact policy/payload manifest committed at that release identity as root `release-manifest.json`, external resolved-commit receipt and clean-reproduction evidence | Nothing after freeze; a correction creates a new release tag/manifest/receipt | A raw commit presented as a release, moving branch, mutable source snapshot, or claim of provider parity |

`AGENTS.md` and `CLAUDE.md` are thin discovery loaders. `WARMBOOT.md` owns the shared
safety invariants and routes explicit toolkit maintenance to `MAINTAINING.md`.
Maintainer policy does not get copied into the managed bundle.

## Owners and dependency direction

| Surface | Owner | Depends on | Evidence/change trigger |
|---|---|---|---|
| Living repository identity | `docs/identity.md`; maintainer coordinator | Current product, repository, checkout and workspace state; frozen compatibility/history boundaries | Name, path, remote, workspace or compatibility decision changes; focused identity/link/allowlist contract |
| Provider-neutral core | `WARMBOOT.md` | Accepted invariants only | Instruction/bootstrap contract changes; cold-agent proof required |
| Routed operating detail | `routes/` | Core route names | Ownership, topology/orchestration-only mode, scope revision, context pressure, evidence, review, handoff or rotation behavior changes |
| Bounded local Git history evidence | `routes/context.md`; coordinator attestation in the current task/lane assignment | One coordinator Git mutator; exact local repository/ref/ancestry/pathspec/command scope | History changes a worker/reviewer decision; semantic allowlist/denylist tests plus a canary or complete external byte manifest when byte preservation is a hard claim |
| Agent takeover | `BOOTSTRAP.md` | Core, portfolio evidence, documentation roles | New-project integration behavior changes; full kickoff/challenge required |
| Maintainer takeover | `MAINTAINING.md` | Core, this map, current task, release authority | Self-improvement authority or proof changes |
| Maintainer engineering contract | `docs/engineering-standards.md`, `docs/testing.md`, `docs/invariants.md`, `docs/adoption-disposition.md` | Portable template lessons specialized to this repository | Root architecture, proof, invariant or adoption changes; assess portable template fallout |
| Optional helper mechanics | `bin/warmboot` | Explicit managed manifest in code; no workspace ownership | Managed create/check behavior changes; unit plus disposable-target evidence |
| Required human workspace | `BOOTSTRAP.md`; inert `templates/project.code-workspace`; target-owned root workspace | Accepted target architecture, commands and existing workspace/`.vscode/` owners | Bootstrap/workspace behavior changes; preservation, syntax/command parity and cold-discovery evidence |
| Optional capability library | Capability-library maintainer: `templates/capabilities/` and its `MANIFEST.json` | Target-native owners and accepted ADR 0003 | Card, inventory, selection or hazard change; manifest, rights, containment and managed-payload isolation checks, plus outsider evidence |
| Portable documentation | `templates/project-docs/` | Source lessons and role index | Portable maintainability/testing/human-inspectability rule changes; source fidelity/scar-removal review |
| Teaching examples | `examples/` | Current portable templates | Template semantics change; native example proof |
| Source provenance | `docs/source-refresh.md`, `docs/capability-design.md`, `examples/MANIFEST.json` | Current local design and sample licences | Explicit source-refresh task only |
| Capability source lineage | Capability-source lineage maintainer: `docs/capability-sources.json` | Digest-bound local design and inherited source rights | Attested-root/no-parent-symlink loading, strict identity/rights inheritance and restricted-source refusal; local rationale or licence/privacy disposition changes; that owner only |
| Deterministic acceptance | `acceptance/`, `tests/` | Exact fixture bytes and honest oracle limits | Contract or regression changes |
| Source-comprehension acceptance | `acceptance/source_comprehension_oracle.py` and bounded fixtures; human review remains authority | Independently declared synthetic cases, never arbitrary target source | Source-orientation/rationale/review contract changes; focused mutations plus complete changed-source non-author read |
| Historical truth | root `CHANGELOG.md`, `BUGFIXES.md`, `docs/adr/` | Observed/accepted changes | Same-change update; never rewrite causal history silently |
| Release truth | `docs/release.md`; root `release-manifest.json` at the release identity plus its external receipt (`docs/releases/` holds the machine contract and illustrative example only) | All selected consumer/evidence paths | Reviewed release candidate; singleton release holder only |
| Active backlog | `docs/plans/warmboot-build-plan.md` | Current user direction and live task authority | Backlog disposition or the owning current receipt changes |
| Current quality-control loop | Named current task/backlog, fed by standards/testing/invariants/system-map evidence | Evidence and unknowns by applicable concern; owned next action/revisit; human/non-author challenge | Material milestone, escaped defect, architecture/ownership change or new trial evidence |

Dependencies flow from thin loaders to the core, then to task-routed detail. Examples
and inspected source evidence may inform portable artifacts; they never override them.
A release manifest records the reviewed include/exclude policy and binds every selected
regular-file byte, but it does not replace the owning documentation or source policy
owner. The capability catalog owns local design and rights references. The library is never a
dependency of the helper-managed payload.

## Change classes

- **Architecture boundary — ordinary maintenance:** planes, loader precedence,
  bootstrap topology, release identity, source authority, or helper safety. Cover all
  six concerns with the smallest proportional set of at least two independent
  non-coordinator research owners, an orchestration-only coordinator, and a distinct non-author
  challenger. The coordinator selects hazard-appropriate proof, including any live
  cold or recovery evidence, through [`docs/testing.md`](testing.md). Separate
  architecture/risk/privacy from testing/bootstrap/operability for destructive/high-risk
  work, or record why merging is safe and cross-check it explicitly. No historical exception grants current authority.
- **Material bounded change:** a portable standard, template, helper behavior or
  acceptance contract. Use a bounded writer and independent reviewer plus native
  proof.
- **Small proven correction:** prose, link, fixture or observed-defect pin whose owner
  and expected behavior are already decided. Use proportional ownership, with a distinct
  reviewer whenever code changes; do not manufacture the full kickoff.

Every class preserves one Git/release mutator and same-change documentation. For every
code change in any class, the coordinator freezes and attests the candidate source set:
every added, renamed or modified human-authored code file, plus recorded generated,
vendored and pure re-export exceptions
([`routes/context.md`](../routes/context.md#candidate-source-set-attestation)).
The writer reconciles its assessment against that attestation, and the distinct
non-author reviewer repeats the reconciliation and reads every resulting file
([`routes/review.md`](../routes/review.md#source-comprehension-release-gate));
an omitted file is a `FINDING`. A bounded history reader receives only the route's pre-attested local allowlist; it
never receives checkpoint, mutation, `git diff`, remote, configuration, worktree-
administration, or credential authority. If the map and implementation disagree,
stop and reconcile the owner; do not add another map.

Plans across these classes are living empirical backlogs, not waterfall authorities.
Evidence may change sequence and staffing; only actual authority, privacy,
destructive, Git-collision, production/HIL, and required-evidence boundaries stop
work unconditionally.

Material scope or owner addenda revise the existing task and impact-analyze lanes,
evidence and decisions before work resumes. Concise digest-bound file receipts are the
resume source; transcripts are navigation only. Human-readable standards, system maps,
invariants, rationale and optional source-controlled diagrams keep intent challengeable
without loading the whole system. Exact language tools and locally calibrated
SLOC/complexity triage remain target-owned.
