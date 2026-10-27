# Frozen pre-challenge package — `EX-KICKOFF-DRAFT-1`

> **EXAMPLE HISTORICAL INPUT.** This index preserves the exact three draft byte
> snapshots recorded immediately before the seventh-owner challenge. The coordinator
> later reconciled the corresponding working artifacts in place, so their current
> digests intentionally differ.

## Individually frozen drafts

| Draft | Frozen byte snapshot | Working path at handoff | SHA-256 |
|---|---|---|---|
| technology/options brief `TECH-DRAFT-1` | [`technology-options-draft-1.md`](technology-options-draft-1.md) | [`../work/technology-options.md`](../work/technology-options.md) | `222d77f2d961e070ab9a8f07ce714f58cc1c57e3c6d908977b48fbb80ec85b23` |
| ADR `ADR-0001-DRAFT-1` | [`technology-architecture-adr-draft-1.md`](technology-architecture-adr-draft-1.md) | [`../work/technology-architecture-adr.md`](../work/technology-architecture-adr.md) | `45e3af35f3e5b678ac6008b4db5dd7dd81ff31db765e7e6090ff69b359bcc613` |
| plan `PLAN-DRAFT-1` | [`kickoff-plan-draft-1.md`](kickoff-plan-draft-1.md) | [`../work/kickoff-plan.md`](../work/kickoff-plan.md) | `2852371c0a68e4d6d892a8f59842d2e4035a6c53a4d031ee5a2e1d2e5a0c87b7` |

The digests are SHA-256 over each file's exact UTF-8 bytes, including its final LF.
The [pre-challenge receipt](../kickoff-pre-challenge-receipt.md) recorded these values
before `post-draft-challenger` began. The individual snapshots, not a digest of this
index, are the review inputs.

## Boundary

No production source, implementation authorization, installation authorization, test
result, or final verdict existed in this package. The draft ADR was
`PROPOSED_FOR_AUTHORIZATION`; the draft plan was
`AWAITING_IMPLEMENTATION_AUTHORIZATION`; and both authorization flags were `false`.
