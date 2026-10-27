# Pre-challenge freshness receipt — `WB-EX-PRECHALLENGE-001`

- Sender: `example-coordinator`
- Receiver: `post-draft-challenger`
- Created: immediately before the seventh-owner challenge of `EX-KICKOFF-DRAFT-1`
- Invalidation event: any challenge reconciliation change to a working artifact
- Authority: read-only challenge only

At receipt creation, each working artifact had the exact bytes preserved by its frozen
snapshot below. SHA-256 was computed over the raw UTF-8 file bytes, including the final
LF.

| Claim | Working artifact | Frozen byte snapshot | Pre-challenge SHA-256 | State |
|---|---|---|---|---|
| technology/options draft is the current challenge input | [`work/technology-options.md`](work/technology-options.md) | [`snapshots/technology-options-draft-1.md`](snapshots/technology-options-draft-1.md) | `222d77f2d961e070ab9a8f07ce714f58cc1c57e3c6d908977b48fbb80ec85b23` | `CURRENT` |
| ADR draft is the current challenge input | [`work/technology-architecture-adr.md`](work/technology-architecture-adr.md) | [`snapshots/technology-architecture-adr-draft-1.md`](snapshots/technology-architecture-adr-draft-1.md) | `45e3af35f3e5b678ac6008b4db5dd7dd81ff31db765e7e6090ff69b359bcc613` | `CURRENT` |
| kickoff-plan draft is the current challenge input | [`work/kickoff-plan.md`](work/kickoff-plan.md) | [`snapshots/kickoff-plan-draft-1.md`](snapshots/kickoff-plan-draft-1.md) | `2852371c0a68e4d6d892a8f59842d2e4035a6c53a4d031ee5a2e1d2e5a0c87b7` | `CURRENT` |

## Pre-authorization state

- ADR: `PROPOSED_FOR_AUTHORIZATION`
- Plan: `AWAITING_IMPLEMENTATION_AUTHORIZATION`
- `implementation_authorized`: `false`
- `install_authorized`: `false`
- Independent challenge: `NOT STARTED`

This receipt authorizes no reconciliation, implementation, package installation, Git,
network, publication, or external effect. Its next and only use is the read-only
seventh-owner challenge.
