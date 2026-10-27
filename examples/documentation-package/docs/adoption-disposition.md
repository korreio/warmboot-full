# Example adoption and deviation record

**Synthetic teaching example.** These are invented project decisions. Owner:
`example-coordinator`.
The target is one offline comparison-key function with a thin CLI.

## Warmboot evaluation

This manually populated package is a `NON_RELEASE_EVALUATION`; no immutable release
identity, helper manifest, publication or live-agent completion is claimed. A real
upgrade requires recoverable release, manifest and target identities first.

## Disposition matrix

| Technique | Disposition | Surviving owner | Reason, proof and revisit condition |
|---|---|---|---|
| Shared neutral instructions | `ADOPT` | Root [AGENTS](../AGENTS.md), pointer-only [CLAUDE](../CLAUDE.md) | One policy avoids drift; inspect routes and reopen if discovery changes. |
| Native engineering and testing rules | `MERGE INTO EXISTING` | [Standards](engineering-standards.md), [testing](testing.md) | Python owns its commands; keep focused and closing evidence separate. |
| Pure policy behind a CLI adapter | `MERGE INTO EXISTING` | [Core](../src/label_normalizer/core.py), [entry point](../src/label_normalizer/__main__.py) | Native tests reach behavior; no service or dependency injection framework is needed. |
| Larger service/application architecture | `OMIT` | [ADR](adr/0001-python-standard-library-core.md) | The objective has no UI, database, remote API or concurrent service caller. Revisit only when one is accepted. |
| Separate subtree instructions | `OMIT` | Root instruction owner | All current code shares commands and hazards; avoid duplicate authority. Revisit if a subtree gains a distinct command, owner or safety boundary. |
| Release and operations checklist | `CITE ONLY` | [Changelog](../CHANGELOG.md) | Local execution is not deployment or release proof; revisit when distribution is authorized. |

## Evidence and limits

The [study](studies/2026-07-31-technology-options.md),
[kickoff plan](plans/kickoff-plan.md) and [challenge](reviews/kickoff-challenge.md)
show the relationship among roles. Receipts and draft hashes demonstrate stale-evidence
recovery within the example. They do not prove an outside source, provider parity or
current test outcome. The repository coordinator reruns native example tests for changed
bytes and records results in the current task.
