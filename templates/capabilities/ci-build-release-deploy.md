# CI, build, release and deployment

- ID: `ci-build-release-deploy`
- Trigger: the target has build artifacts, release identity or an authorized external
  deployment whose states and proofs must be separated.
- Anti-trigger: no artifact or external environment exists, or the user has not
  authorized hosted execution/mutation.
- Inspect before adopt: native build/test wrappers, workflow paths, branch protections,
  version sources, artifact provenance, environment ownership, deployment states,
  rollback/recovery and hosted-minute cost.
- Disposition
  ([definitions](../../docs/documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit)):
  record `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT`. Existing
  CI/release/deploy authorities survive unless a proved gap justifies a merge.

## Target record

- Decision owner and native command: name separate owners for build evidence, release
  identity and deployment mutation; name the one target-native command for each used
  phase.
- Authority, privacy and singletons: hosted CI, tags, releases, registries, production
  environments and credentials each require explicit authority and one holder.
- Focused evidence: local fake/state-machine tests and a native build/check that cause
  no external effect.
- Closing evidence: target-native full gate, artifact/version parity and an authorized
  environment proof; observation must be independent of mutation when risk requires it.
- Recovery: stop on ambiguous environment, stale artifact, version mismatch, failed
  health signal or missing rollback owner. Recovery is target-owned, never inferred.
- `UNPROVED`: fake deploys and local builds do not prove hosted CI, registry, release,
  production, network, rollback or live health.
- Recurring tax: workflow upkeep, hosted minutes, pins, artifact retention, environment
  drift, release notes and rollback rehearsal.
- Delete or revisit: remove an unused workflow/environment; revisit when build and
  deploy identity diverge or the target changes hosting model.

## Suggested formula

```text
source identity -> native gates -> immutable artifact identity -> authorized mutation
authorized mutation -> independent observation -> ACCEPTED | RECOVER | BLOCKED
```

No deployment or rollback executable belongs in this generic library.

- Source IDs: `ci-build-release-deploy-design`.
- Design evidence: [local rationale](../../docs/capability-design.md) and
  [source catalog](../../docs/capability-sources.json).
- Related cards (navigation only): [testing](testing-feedback.md),
  [observability](observability-diagnostics.md).
