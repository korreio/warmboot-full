# Opt-in upgrade for an existing consumer

This secondary workflow evaluates one existing project against a newer immutable
Warmboot Full release. It is not an updater: it never silently follows `main`,
replaces a target from templates, or creates a daemon, background sync, dashboard, or
copied release tree. The workflow applies once tagged releases exist; this tree is
unreleased.

```text
Read AGENTS.md or CLAUDE.md. Take full ownership of evaluating an upgrade of
<ABSOLUTE_TARGET_PROJECT> from Warmboot Full release
<OLD_ANNOTATED_RELEASE_TAG_OR_ITS_RESOLVED_COMMIT> to Warmboot Full release
<NEW_ANNOTATED_RELEASE_TAG_OR_ITS_RESOLVED_COMMIT>. Follow UPGRADING.md, preserve
project-native authorities, and do not publish remotely without my authorization.
```

Release tags use the `agent-warmboot-v*` form, for example `agent-warmboot-v1.0.0` for a first release.

Evaluation is not mutation authority. One named target coordinator is the project's
only Git holder. The Warmboot release holder remains a separate source of release
receipts and does not operate target Git. Local checkpoint, target publication and
Warmboot release are separate actions; publication or another external effect always
requires explicit authority for that exact boundary.

## 1. Require and freeze all three identities

Release identity itself—annotated tag, resolved commit, manifest, external receipt and
release state—is defined by [`docs/release.md`](docs/release.md); read that contract
before recording the receipts below.

Before comparison or mutation, record immutable receipts for:

1. **Old release:** unchanged annotated release tag, resolved full commit, consumer
   pin, release-manifest path and SHA-256, release state, and release notes from that
   same identity. A release that predated notes may instead use an empty later-issued
   baseline record only when the old release receipt binds that record's path and
   SHA-256 to the old tag and resolved commit. A resolved commit input is accepted only
   when this receipt binds it to that tag and manifest.
2. **Proposed release:** the same fields for a different annotated release tag. A raw
   commit without that receipt, branch, moving checkout, or current `main` is not a
   release input.
3. **Target:** absolute path; exact commit when committed state is the basis,
   otherwise a canonical tree/state digest with dirty, generated and concurrent
   boundaries named; the existing adoption receipt; and a digested native-authority
   inventory.

Keep old release, proposed release and target snapshots separate. Hash the raw
manifest and release-note bytes and recheck every receipt immediately before any
authorized mutation. If the old release, its manifest, the target identity, or the
target's adoption receipt cannot be recovered and reconciled, stop `BLOCKED`; never
reconstruct them from memory, `main`, templates, or installed managed bytes.

The installed `.agent-warmboot/manifest.json` may be recorded as evidence of helper-
declared files, hashes and `source_revision`. It is self-declared local metadata, not
release authentication, target authority, compatibility evidence, or overwrite
permission. A coherent rewrite can pass helper `check`, so it never substitutes for
the release receipt.

## 2. Inventory native authorities

Read the target's instruction precedence and current task. Record surviving owners
and exact paths for root and subtree instructions/provider loaders; engineering and
testing standards; ADRs, studies, plans and architecture/system maps; native tests,
fixtures and regression pins; bug/defect and changelog/release history; workspaces,
`.vscode/`, generated configuration and settings; privacy, credentials and concurrent
work.

These are project truth. Never blind-overwrite, delete, rename or shadow them because
a Warmboot root, route, template, helper, example, standard, ADR, test, bug ledger,
changelog, workspace, or architecture document changed. Preserve stronger target
safety constraints. Any new routed file needs one owner and cannot create a second
authority.

## 3. Compare and disposition applicable material release changes

Validate both compact immutable manifests and their external tag/commit receipts. The
manifest proves one whole selected-payload identity; the frozen release notes carry
the material per-path additions/removals/changes with old/new content digests for
upgrade disposition. Treat those rows as release-holder evidence bound to the same
immutable receipt, not as proof recovered from the aggregate. A missing row, malformed
digest, duplicate path, manifest/notes identity disagreement or whole-payload change
without reconciled notes is `BLOCKED`. The release holder proves that changed selected
paths equal note paths, except only the current note's receipt-bound self-reference
meta-artifact; any other exception is `BLOCKED`.

The shared manifest validator is
[`acceptance/release_manifest.py`](acceptance/release_manifest.py), and the consumer
runs it as well as the release holder. It ships with the toolkit source, not with the
installed target files, so run it from a clean checkout of the release being validated. The exact
invocation and its flag semantics are owned by [`docs/release.md`](docs/release.md).
Validate the old and the proposed release each in its own checkout; the three
expected values come from that identity's external release receipt, never from
the manifest under test. The
validator expands the independently frozen include/exclude policy and proves the
complete selected regular-file aggregate plus bound lineage bytes in a clean local
checkout. Its `release_ready: false`, `tag_verified: false` and remote/
signature `UNPROVED` receipt means the release holder must still supply the external
tag/commit/manifest receipt, semantic lineage reconciliation and clean reproduction.
Upgrade remains `BLOCKED` when that release evidence is absent.

Every applicable material change receives exactly one target-owned disposition.
`ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` and `OMIT` are defined once, in
[`docs/documentation-architecture.md`](docs/documentation-architecture.md); this workflow
uses that definition and does not restate it. Two upgrade-path deltas apply:

- the unit of disposition is one material release-note change row, not a documentation
  role, and it is always decided against an existing target authority rather than an
  absent one; and
- `OMIT` additionally records the recurring cost and the evidence limit next to the
  concrete mismatch and revisit trigger, because the change has already shipped in the
  proposed release and will resurface at the next comparison.

The compact comparison row needs only the release-note change ID, disposition, reason,
surviving target destination/owner, and required native proof or honest limit. Exact
old/new bytes already bound by the immutable release identities are not repeated.
Unchanged or irrelevant teaching/example material is recorded once as inspected and
irrelevant, with no target disposition, destination, edit or recurring obligation.
Never turn release-note inventory into a permanent target checklist.

## 4. Gate incompatible core, schema and safety changes

A release-manifest schema change, helper-manifest schema change, instruction-
precedence change, incompatible provider-neutral core change, or weaker safety
invariant requires an explicit target migration. Before implementation, the plan
names:

- old, transition and intended states, exact paths and one holder per mutable path;
- ordering, compatibility window and the condition that blocks the next step;
- a coordinator-selected local rollback point and exact restoration procedure;
- cheapest focused native proof and full closing target evidence, with unavailable
  required proof labelled `UNPROVED` or `BLOCKED`;
- an independent challenger of identities, preservation, migration, rollback, proof
  and authority; and
- an observable reversal trigger and its authorized owner.

The challenger returns exactly `CLEAN`, `FINDING` or `BLOCKED`. Findings must be
disposed and later changed bytes expire `CLEAN`. No incompatible migration starts
without a recoverable rollback point, explicit target mutation authority, passing
prerequisite proof and clean challenge. Rollback restores the target's own reviewed
checkpoint; it never reinstalls an old template over native truth.

## 5. Apply only an accepted target plan

After the gates pass, revalidate all three identities and concurrent state. Serialize
overlapping writers, change only accepted target paths, and use native edit, test and
bootstrap mechanics. The create-only helper is not an upgrade engine and must not be
forced through conflicts. Preview and `check` remain mechanical evidence only. When a
release changes the managed loader text, its `check` reports `incompatible managed
loader` for loaders an earlier release installed. Replacing only the loaders does not
restore `PASS`: the installed manifest still holds the earlier loader digests, so
`check` then reports a content/hash mismatch. The accepted plan reinstalls the whole
managed set (both loaders, the core, every route and the manifest) from the new
release. It first moves any project-owned content a loader carries into a target-owned
file, as [Existing agent instructions](BOOTSTRAP.md#existing-agent-instructions)
describes; then, for example, it removes the earlier managed files under that plan's
authority and runs the new release's `init <target> --apply` after reviewing its preview.
A manually reconciled target, as
[Existing agent instructions](BOOTSTRAP.md#existing-agent-instructions) describes, has no
manifest, so `check` fails on it and is not evidence. Its accepted plan keeps the
target's own loaders, replaces by hand the core and the routes it copied, removes any
copied route the new release no longer ships, and changes a loader only where an
accepted disposition row requires it.
Installs are interchangeable at the protocol level: each edition's `check` passes the
other's install. Moving a target to the other edition is a reinstall of the managed set
under an accepted plan, like an upgrade.

Run focused proof first and closing target evidence on the unchanged candidate. Review
the exact diff, authority preservation, disposition rows, receipt update, recovery and
proof limits independently. Only the coordinator may select reviewed paths for an
authorized local recovery commit. Push, tag, release, merge, deploy, messaging and
other publication remain separately unauthorized without explicit user authority.

## 6. Compact comparison record and recovery

Planning writes one agent-owned `UPGRADE.md`, not an exhaustive JSON result or second
schema. It begins with one fenced `yaml` `safety_receipt` containing exactly eleven
scalar keys:

```yaml
safety_receipt:
  old: "<TAG>@<RESOLVED_COMMIT>#<MANIFEST_OR_EXTERNAL_RECEIPT_SHA256>"
  new: "<TAG>@<RESOLVED_COMMIT>#<MANIFEST_OR_EXTERNAL_RECEIPT_SHA256>"
  target: "<CURRENT_TARGET_STATE_SHA256>"
  adoption: "CURRENT"
  mode: "PLANNING_ONLY"
  may_edit: false
  may_git: false
  may_publish: false
  incompatible: true
  verdict: "BLOCKED_BEFORE_MUTATION"
  next: "REFRESH_IDENTITIES_THEN_SEEK_EXPLICIT_EDIT_AUTHORITY"
```

After it, the coordinator owns concise prose and tables containing only material
native owners/dirt, applicable disposition rows, inspected-only irrelevant material,
workspace preservation, and the conditional migration/rollback/proof/review/reversal
path. The receipt is a stale/authority canary, not authentication, a mutation ticket,
or the full comparison. Neither the structured receipt nor any other record field can
override current user direction or the target repository's current authority. The
whole-record independent reviewer must reject contradictory prose even when the
bounded parser passes; do not add NLP to the oracle. Do not add empty sections, repeat
per-file release digests, list every native role regardless of relevance, or create a
JSON sidecar. Checked Markdown table rows may use zero to three leading spaces; U04
must never appear as a disposition row, and escaped pipes are conservatively rejected.

If mutation is later authorized and completed, update the target's existing adoption
record with the adopted annotated release identity, before/after target identity,
actual dispositions/owners, proof/review, rollback/reversal state and publication
boundary. Do not pre-fill that final receipt during planning.

On resume, recompute every identity and digest. A mismatch is `STALE` and `RERUN NOW`;
freshness renews evidence only, never edit, Git or publication authority. Old releases
remain recoverable through their annotated tags, resolved-commit receipts and
historical manifests. Do not copy per-release trees into `main`. A revoked release
stays historical evidence but is not eligible for new adoption.

The planning fixture under `acceptance/fixtures/upgrade-package/` stops at
`STRUCTURE_ONLY` with one `UPGRADE.md`. Its standard-library oracle checks the eleven
keys, three material rows, migration guard table, eight fail-closed mutations and
fresh-copy resumption, duplicate JSON keys, exact workspace task shape and the bounded
Markdown indentation/pipe cases. That parser is recurring maintenance tax and must
remain bounded; it does not own or semantically interpret prose. The fixture proves
structure and fail-closed boundaries only—not agent discovery, whole-record semantic
consistency, release authenticity, migration quality, provider behavior, target
mutation, native runtime behavior, Git recovery, or publication.
