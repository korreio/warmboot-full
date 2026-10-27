# Immutable consumer release procedure

`main` is the evolving maintainer line. A consumer release has one Git identity: an
immutable annotated release tag. Its resolved full commit is the stable consumer pin,
not a competing release identity. A correction creates a new tag; an adopted tag is
never moved silently. A defective identity is marked revoked or superseded in the
external release record while its historical bytes remain recoverable.

The singleton coordinator is also the release holder. Workers and reviewers never run
Git, create tags, contact remotes or hold credentials. A local checkpoint, candidate
manifest, local annotated tag and authorized remote publication are separate effects.

## Compact commit-contained manifest

[`release-manifest.schema.json`](releases/release-manifest.schema.json) defines the
machine contract. [`release-manifest.example.json`](releases/release-manifest.example.json)
is illustrative and explicitly not a release. The compact manifest records:

- release ID, `CANDIDATE` status and the declared annotated-tag name;
- one canonical include/exclude payload policy and its SHA-256;
- one SHA-256 over every regular file selected by expanding that policy;
- canonical lineage/privacy receipt paths and their content SHA-256 values;
- fixed conservative claims (`release_ready: false`, `tag_verified: false`, remote
  authenticity `UNPROVED_LOCAL_ONLY`); and
- four exact, machine-checkable `known_unproved` domain records: annotated tag,
  resolved commit, signature authenticity and remote authenticity all remain
  `UNPROVED` in commit-contained bytes.

`declared_ref` is a conservative short tag name, not a full `refs/...` path. The
verifier rejects empty or dot components, leading-dot components, any component ending
in `.` or `.lock`, ref-normalization sequences such as `..`, `@{` or `//`, forbidden
Git ref characters, whitespace/control characters and non-ASCII normalization
variants. Examples such as `agent-warmboot-v1.0.0` and `release/2026-08-01` are valid.

The payload aggregate is SHA-256 over records sorted by path and encoded exactly as:

```text
path + NUL + type + NUL + mode + NUL + sha256 + NUL + decimal_bytes + LF
```

`type` is `regular`; mode is normalized to `100644` or `100755`. The verifier expands
the include roots/files from a clean local checkout, applies explicit `FILE` or
`SUBTREE` exclusions, and rejects traversal, symlinks, special nodes, missing includes,
unexpected eligible files, missing files, type/mode/content changes and aggregate
mismatch. Every exclusion has a non-empty reason and binds a listed lineage/privacy
receipt. Every lineage receipt must remain selected and match its recorded bytes. The
verifier fails on anything below an include that it cannot list or inspect, excluded or not.

The manifest cannot hash its own bytes. Its separately supplied canonical path must
therefore be an explicit policy exclusion whose reason is bound to a lineage/release
receipt. The release commit nevertheless contains the exact manifest bytes; the later
external receipt binds their SHA-256 to the resolved annotated tag.

Policy hash, release ID and declared tag are independently frozen inputs to repository-
backed verification. Supplying the values from the manifest itself would let a changed
manifest bless a widened exclusion or renamed identity. The canonical verifier takes
all three explicitly:

```sh
python3 -B acceptance/release_manifest.py \
  --repository <ABSOLUTE_CLEAN_CHECKOUT> \
  --manifest <REPOSITORY_RELATIVE_MANIFEST> \
  --expected-policy-sha256 <FROZEN_POLICY_SHA256> \
  --expected-release-id <FROZEN_RELEASE_ID> \
  --expected-declared-ref <FROZEN_ANNOTATED_TAG>
```

Its pass proves local policy expansion, selected regular-file bytes/modes and bound
lineage receipts only. It deliberately does not prove an annotated tag, resolved
commit, signature, trusted remote provenance, publication, provider behavior or
consumer usefulness. The commit-contained status therefore remains `CANDIDATE`; no
post-commit fact is written circularly into the commit it identifies.

The ordinary verifier, repository-backed verifier and CLI all reject
`ILLUSTRATIVE_NON_RELEASE`. The checked-in example remains useful only through the
explicit structure-only API, which cannot receive a repository or frozen release
inputs:

```sh
python3 -B -c 'import sys; from pathlib import Path; from acceptance.release_manifest import load_manifest, verify_illustrative_manifest; verify_illustrative_manifest(load_manifest(Path(sys.argv[1])))' \
  docs/releases/release-manifest.example.json
```

That command proves the example matches the compact non-release shape. It is never a
release-candidate, payload, tag, commit or authenticity proof.

## External/local release receipt

After the reviewed manifest and selected bytes are committed, the coordinator resolves
that exact commit, creates the declared annotated tag locally only with current
authority, and writes a separate release receipt. It records at least:

- release ID and declared annotated tag;
- tag-object identity and resolved full commit;
- manifest path, manifest SHA-256, frozen policy SHA-256 and payload SHA-256;
- verifier command/output and clean-checkout identity;
- lineage/privacy reconciliation and remaining `UNPROVED` items;
- local release state (`REVIEWED_LOCAL`, `SUPERSEDED` or `REVOKED` as applicable);
- reviewer verdict and revocation/supersession reason when applicable; and
- remote/publication state separately.

That receipt is the source of post-commit state. A private publication receipt may
later add `PUBLISHED_PRIVATE` only after separately authorized push and remote identity
verification. Local hashes do not establish trusted remote origin or signature
authenticity.

## Consumer receipt and later upgrade

Bootstrap records the annotated tag, resolved full commit, manifest path and SHA-256,
release state, release-note digest, frozen target identity and actual applicable
dispositions in the target-owned adoption record. Irrelevant release-note material
creates no target row or recurring obligation. That external identity—not the installed helper's
self-declared manifest—is the old-release input to [`UPGRADING.md`](../UPGRADING.md).
Missing identity is `BLOCKED`. Historical releases stay recoverable by their immutable
tag/commit receipts; do not copy per-release trees into `main`.

The changed selected-path set equals the release-note path set plus only the current
release-note file as a self-reference meta-artifact. That exception's path and SHA-256
are bound in the external receipt. A release that predated notes may receive an empty
later-issued baseline record only when that receipt binds its path/digest to the old tag
and resolved commit. Any other missing selected-path row is `BLOCKED`.

Each release-note change needs a material summary of what changed. A state-only
restatement such as `Changed for the agent-warmboot-v1.1.0 candidate.` is invalid even
when its path and digests are exact.

### Where a consumer finds a real release manifest

[`releases/`](releases/) never holds a real release manifest. It holds the machine
contract and one `ILLUSTRATIVE_NON_RELEASE` example, which every verifier rejects as a
release; that example is a schema reference, not a manifest a consumer may adopt. The
real manifest is the one committed at the release identity itself: check out the
annotated release tag (or its resolved full commit) and read the manifest at the
repository-relative path named in that release's external receipt, which binds the
path's SHA-256 to the tag and commit. A manifest taken any other way—from the current
`main` tip, from a branch or moving checkout, from the installed helper's self-declared
`.agent-warmboot/manifest.json`, or from the example file—is not a release input.

`acceptance/release_manifest.py` above is also the consumer-side validator, not a
maintainer-only instrument: a consumer runs the same command against a clean checkout of
the release it is adopting or upgrading from, taking the frozen policy SHA-256, release
ID and declared tag from that release's external receipt. See
[`UPGRADING.md`](../UPGRADING.md) for how the result is consumed on the upgrade path.

The root `SOURCE_REVISION` file, which `bin/warmboot` copies into an installed target's
manifest as `source_revision`, is owned by the release holder, who sets it to the
release identity at each annotated release tag; between releases it is informational
only and never evidence of authenticity or provenance.

## Freeze and release sequence

1. Finalize all ordinary authored bytes and test literals, then freeze the release ID/tag
   declaration, include/exclude policy, policy digest, lineage/privacy receipts, manifest
   path, limitations, and evidence inputs. No Git/tag/remote action occurs in this step.
2. The release holder writes `SOURCE_REVISION` and both release-note records, validates
   selected-path equality and receipt-bound exceptions, then generates the compact manifest
   last from raw bytes and normalized executable modes. Material change summaries are
   required; state-only summaries are invalid. Keep the manifest path explicitly excluded
   and every exclusion justified/bound.
3. The coordinator creates and freezes one exact local `CANDIDATE` commit containing
   those bytes. No clean-checkout proof runs before this frozen candidate identity exists.
4. In a dedicated clean verifier checkout of that exact frozen candidate, run focused and full
   release-boundary proof and the verifier with independently frozen inputs. The release holder
   separately runs and records source dispositions and rights/notice coverage; the payload verifier proves bytes
   and modes, not authorship or legal sufficiency. Tests run from and
   read that checkout with `python3 -B`; they are read-only and write-free there. Only disposable prepare targets write beneath designated repository-local
   `.acceptance-work/` children, outside selected release paths.
   Reject an unexpected eligible addition, omission, traversal, symlink, special node,
   type/mode/content, exclusion, lineage, claim, schema, or domain mismatch.
5. Independently review the unchanged candidate and evidence. Any selected-byte, policy,
   lineage, manifest, or evidence change expires the verdict. A correction repeats steps
   1–4 and creates a new exact candidate before rereview.
6. Only with current tag authority, resolve the reviewed candidate commit and create the
   declared annotated tag. The external/local receipt binds tag, resolved commit, and
   manifest digest without changing commit-contained bytes.
7. Detach a second clean checkout at the resolved commit; rerun manifest verification
   and release-boundary evidence. A mismatch blocks or revokes release.
8. Only with explicit remote authority, verify the exact private remote and publish the
   reviewed tag/commit. Re-resolve remote identity and record publication separately. Do
   not dispatch hosted CI merely for release ceremony.

## External release states

| State | Meaning |
|---|---|
| `CANDIDATE` | Commit-contained manifest state; tag/receipt/reproduction/publication may not exist |
| `REVIEWED_LOCAL` | Annotated tag, external receipt, complete payload, lineage and clean reproduction agree locally |
| `PUBLISHED_PRIVATE` | Authorized private push was verified at that same identity |
| `SUPERSEDED` | A later release is preferred; this immutable release remains historical |
| `REVOKED` | A named safety/privacy defect forbids new adoption; bytes remain evidence |

No state implies provider parity. Any current external/provider result is routed through
`docs/plans/warmboot-build-plan.md` to its owning artifact. Historical handoffs grant no
current release, provider, remote, or programme authority.

## Current unreleased tree and local lineage

`SOURCE_REVISION` is `UNRELEASED-development`; no root release manifest or historical
release readiness applies to the current bytes. The current task owns all candidate
results. A future release binds actual current local evidence: `docs/release.md`,
`docs/capability-design.md`, `docs/capability-sources.json`, `examples/MANIFEST.json`
and `LICENSING.md`, plus any selected current privacy/rights receipt. Every listed
receipt remains selected and is checked by digest. No prior release receipt is required
or fabricated. The illustrative manifest remains structure-only evidence.
