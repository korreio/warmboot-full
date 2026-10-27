# API and service contracts

- ID: `api-service-contracts`
- Trigger: components cross a process/network boundary or expose versioned request,
  response, error, retry, cache, auth or compatibility semantics.
- Anti-trigger: an internal function boundary is clearer, or generated schema would
  become a second unowned truth.
- Inspect before adopt: route/schema owners, clients, error envelope, auth, timeouts,
  retry/idempotency/cache policy, OpenAPI or equivalent, drift checks and compatibility
  tests.
- Disposition
  ([definitions](../../docs/documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit)):
  record `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT`; merge into
  the target's canonical schema/route authority.

## Target record

- Decision owner and native command: name the canonical contract owner and one native
  generation/diff/test command if present; generated output never outranks its source.
- Authority, privacy and singletons: local fakes by default. Network targets, tokens,
  rate limits and captured payloads require explicit authority and holders.
- Focused evidence: pure schema/serialization/error tests and a fake server/client at
  the changed boundary.
- Closing evidence: target-native contract and integration suite, drift proof and only
  an authorized bounded live probe when required.
- Recovery: fail closed on unknown version/auth/target, malformed sensitive error,
  unsafe retry or incompatible drift; keep a documented degraded/offline path where
  the product permits it.
- `UNPROVED`: local contract tests do not prove service availability, live auth, rate
  limits, latency, data policy or backward compatibility outside covered fixtures.
- Recurring tax: schema/version upkeep, client generation, fixtures, drift checks,
  deprecations and service failure handling.
- Delete or revisit: remove generated/schema layers that duplicate a single authority;
  revisit on version, client, auth, retry/cache or service-owner change.

## Suggested formula

```text
canonical schema + typed error semantics
-> fake client/server contract proof
-> target integration proof
-> authorized live probe only if the decision still needs it
```

- Source IDs: `api-service-contracts-design`.
- Design evidence: [local rationale](../../docs/capability-design.md) and
  [source catalog](../../docs/capability-sources.json).
- Related cards (navigation only): [public APIs](public-api-catalogue.md),
  [data/database](data-database-operations.md), [testing](testing-feedback.md).
