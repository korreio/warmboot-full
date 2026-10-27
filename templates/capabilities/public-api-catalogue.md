# Public and external API catalogue

- ID: `public-api-catalogue`
- Trigger: an objective may depend on a third-party/public service and choosing it
  changes architecture, privacy, cost, reliability or maintenance.
- Anti-trigger: speculative provider lists, copied credentials/endpoints, or a live
  probe without a concrete decision and authority.
- Inspect before adopt: current official terms/docs, auth/data scopes, privacy and data
  residency, quotas/cost, availability, SDK/protocol, export/deletion, substitutes,
  degraded mode and target precedent.
- Disposition
  ([definitions](../../docs/documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit)):
  record `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT` for each
  considered service; precedent is evidence, never a forced provider choice.

## Target record

- Decision owner and native command: name a target integration owner and local
  fake/contract command; live calls need separate service/account/network authority.
- Authority, privacy and singletons: one holder for credentials, account, quota and
  live session. Record data categories, purpose, retention and provider boundary.
- Focused evidence: official-doc research plus a local fake/fixture proving the needed
  contract and failure/degraded behavior.
- Closing evidence: target-native contract/integration tests and, only when authorized,
  the cheapest bounded non-sensitive live confirmation.
- Recovery: stop on changed terms/scope, unknown data flow, quota/cost surprise,
  credential exposure or missing substitute; disable or degrade through the target owner.
- `UNPROVED`: documentation and fakes do not prove current availability, account access,
  data correctness, quotas, privacy practice or long-term compatibility.
- Recurring tax: doc/terms review, auth refresh, quotas/cost, SDK/API versions, provider
  incidents, fixtures and substitute upkeep.
- Delete or revisit: remove unused integrations; revisit on official API, terms, cost,
  data, account, product-objective or substitute changes.

## Suggested formula

```text
objective constraint -> official current source -> privacy/cost/failure comparison
-> local fake contract -> adopt provider | choose substitute | OMIT
```

Common integration categories include first-party APIs, third-party data providers,
location services, cloud/mobile services, error/analytics services, hosting, translation
and browser APIs. Revalidate them for the target; do not copy provider choice blindly.

- Source IDs: `public-api-catalogue-design`.
- Design evidence: [local rationale](../../docs/capability-design.md) and
  [source catalog](../../docs/capability-sources.json).
- Related cards (navigation only): [API contracts](api-service-contracts.md),
  [security/privacy](security-privacy-secrets.md), [observability](observability-diagnostics.md).
