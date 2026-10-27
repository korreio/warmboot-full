# Observability and diagnostics

- ID: `observability-diagnostics`
- Trigger: remote or intermittent failure cannot be diagnosed safely with local tests
  and a bounded signal will change an operational/product decision.
- Anti-trigger: telemetry is added by convention, product success depends on it, or no
  one owns privacy, failure, alerts, retention and removal.
- Inspect before adopt: existing logs/errors/traces/analytics, data classification,
  consent, scrubbers, release identity, offline/degraded behavior, alert ownership and
  artifact retention.
- Disposition
  ([definitions](../../docs/documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit)):
  record `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT`; merge into
  an existing diagnostic surface and keep analytics distinct from error diagnosis.

## Target record

- Decision owner and native command: a target observability/privacy owner names the
  native local scrubber/contract check and any separately authorized service.
- Authority, privacy and singletons: telemetry projects, release uploads, API keys,
  sessions and captured artifacts each have one holder; minimize and scrub by default.
- Focused evidence: synthetic event/error tests prove scrubbing, failure isolation and
  no-crash behavior without contacting a service.
- Closing evidence: target-native tests plus an authorized non-sensitive canary only
  when live delivery is necessary to the decision.
- Recovery: disable/degrade safely on SDK/service failure; stop on sensitive fields,
  wrong environment or unknown consent and let the named owner remove affected data.
- `UNPROVED`: local capture does not prove hosted ingestion, alerting, quotas, release
  symbolication, analytics accuracy or privacy compliance.
- Recurring tax: SDK upgrades, consent/scrubbing tests, quotas/cost, release mapping,
  alert triage and retention.
- Delete or revisit: remove a signal that does not change decisions; revisit on data,
  consent, provider, release, cost or diagnostic-need changes.

## Suggested formula

```text
decision-useful event -> minimize -> scrub -> local synthetic proof
service unavailable -> product continues; diagnostic claim becomes UNPROVED
```

- Source IDs: `observability-diagnostics-design`.
- Design evidence: [local rationale](../../docs/capability-design.md) and
  [source catalog](../../docs/capability-sources.json).
- Related cards (navigation only): [security/privacy](security-privacy-secrets.md),
  [quality](quality-evaluation.md), [CI/build/release/deploy](ci-build-release-deploy.md).
