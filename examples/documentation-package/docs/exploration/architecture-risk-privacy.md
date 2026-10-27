# Architecture, risk, and privacy lane evidence

- Owner: `architecture-risk-privacy-owner`
- Scope: propose truth ownership and data flow, identify hazards/security/privacy
  boundaries, and define stop conditions; do not select language or test tools.
- Status: `REPORTED / FROZEN` on 2026-07-31.

## Input snapshot

Snapshot `EX-ARCH-INPUT-1` received the comparison-key outcome, explicit display
preservation non-goal, CLI requirement, offline constraint, and absence of any
service, persistence, account, credential, or telemetry requirement.

## Evidence

Proposed value flow:

```text
caller or CLI argument -> one pure normalization owner -> returned/printed comparison key
```

| Hazard | Smallest boundary/control | Required evidence or stop |
|---|---|---|
| comparison key overwrites display label | name output as a comparison key; retain display values outside the package | API/README wording plus compatibility/casefold tests |
| CLI drifts from library behavior | adapter calls the single owner and adds no transformation | subprocess test across the adapter boundary |
| semantic creep into slugging/collation/transliteration | explicit non-goals and a superseding decision for new semantics | stop implementation if requested behavior crosses the boundary |
| unexpected side effects | pure owner; CLI reads arguments and prints only the result | source review and behavior test |
| private text retention or transmission | no filesystem, database, logging, analytics, or network owner exists | adding one requires new privacy/data ownership and evidence |
| unstable keys across Unicode upgrades | do not promise cross-version serialized stability | record `UNPROVED`; re-evaluate if keys become persisted identifiers |

No threat model for accounts, remote transport, or stored data was invented
because those boundaries do not exist in scope.

## Receipt

`ARCH-01 — PURE OWNER / THIN ADAPTER`: One pure function owns normalization; the
CLI only parses and prints. Inputs are not retained or transmitted. Stop and
supersede the decision before adding persistence, network, telemetry, credentials,
or stable cross-version key guarantees.
