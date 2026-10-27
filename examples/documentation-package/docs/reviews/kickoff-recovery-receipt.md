# Refreshed recovery receipt — `WB-EX-RESUME-001`

- Sender: `example-coordinator`
- Receiver/resumer: `example-fresh-resumer`
- Resumer independence: distinct from the coordinator, six exploration owners, and
  `post-draft-challenger`
- Inherited receipt: [`WB-EX-PRECHALLENGE-001`](kickoff-pre-challenge-receipt.md)
- Trigger: challenge `WB-EX-CHALLENGE-001` and coordinator reconciliation changed all
  three working artifacts
- Authority: evidence refresh only

The fresh resumer recomputed every current working-artifact SHA-256, compared it with
the inherited pre-challenge digest, marked the old claim `STALE` and `RERUN NOW`, then
reloaded the reconciled artifact before recording this receipt.

| Claim | Pre-challenge SHA-256 | Freshness | Action | Reconciled working artifact | Current SHA-256 |
|---|---|---|---|---|---|
| technology/options brief | `222d77f2d961e070ab9a8f07ce714f58cc1c57e3c6d908977b48fbb80ec85b23` | `STALE` | `RERUN NOW` | [`work/technology-options.md`](work/technology-options.md) | `7cfd01014f3f6439ef1fed8da40836a70f9d7758338c1d8e5be0635d3ad55b47` |
| ADR | `45e3af35f3e5b678ac6008b4db5dd7dd81ff31db765e7e6090ff69b359bcc613` | `STALE` | `RERUN NOW` | [`work/technology-architecture-adr.md`](work/technology-architecture-adr.md) | `eec09d573e70062983a4ab7825934d1af69f8cbbe3275bbb3ce37ecd79d181e3` |
| kickoff plan | `2852371c0a68e4d6d892a8f59842d2e4035a6c53a4d031ee5a2e1d2e5a0c87b7` | `STALE` | `RERUN NOW` | [`work/kickoff-plan.md`](work/kickoff-plan.md) | `5b8f44d02084ec1606c082126840d0b0415933687cca2688fab99fe47031e3f8` |

SHA-256 covers each file's exact raw UTF-8 bytes, including its final LF. The current
digests above are the refreshed evidence; the old digests remain historical input
identities only.

## Reloaded pre-authorization verdict

- Six exploration receipts present: `CONFIRMED`
- Seventh-owner challenge receipt present: `WB-EX-CHALLENGE-001`
- Coordinator remained orchestration-only: `CONFIRMED`
- ADR: `PROPOSED_FOR_AUTHORIZATION`
- Plan: `AWAITING_IMPLEMENTATION_AUTHORIZATION`
- `implementation_authorized`: `false`
- `install_authorized`: `false`
- Receiver decision: `ACCEPTED` for evidence refresh only

Accepting this receipt does not accept the ADR and grants no implementation or
installation authority. The next step belongs separately to the decision owner, which
may accept or reject the ADR and then set explicit plan gates.
