# Data and database operations

- ID: `data-database-operations`
- Trigger: the target owns durable/stateful data, schema changes, imports, backups or
  recovery whose hazards exceed unit-only proof.
- Anti-trigger: the target is stateless or its existing database owner/runbooks already
  cover the relevant operation and evidence.
- Inspect before adopt: data classification, schema/migration authority, transaction and
  isolation semantics, fixtures, backup/restore ownership, retention and environment
  separation.
- Disposition
  ([definitions](../../docs/documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit)):
  record `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT`; normally
  merge into the existing migration/data authority.

## Target record

- Decision owner and native command: name schema, migration and recovery owners plus
  each target-native command; no generic command receives database authority.
- Authority, privacy and singletons: credentials, database/environment, migration lock,
  backup and restore target each need explicit authority and one holder. Use synthetic
  data by default.
- Focused evidence: pure schema/serialization checks, disposable local database or fake
  migration-state tests at the changed boundary.
- Closing evidence: target-native migration/integration suite and, only when separately
  authorized, backup/restore or rollout evidence for the named environment.
- Recovery: abort on uncertain target, non-synthetic data, unknown concurrent writer,
  irreversible migration or unproved restore; the named data owner performs recovery.
- `UNPROVED`: local/disposable tests do not prove production volume, locks, replication,
  backup integrity, restore time or live migration safety.
- Recurring tax: version support, migrations, fixtures, backups, restore drills, privacy
  retention and operational ownership.
- Delete or revisit: remove data machinery when persistence disappears; revisit on
  schema, scale, retention, provider or recovery-objective changes.

## Suggested formula

```text
schema contract -> reversible/disposable proof -> migration state machine
backup claim -> named artifact + independent restore proof; otherwise UNPROVED
```

- Source IDs: `data-database-operations-design`.
- Design evidence: [local rationale](../../docs/capability-design.md) and
  [source catalog](../../docs/capability-sources.json).
- Related cards (navigation only): [security/privacy](security-privacy-secrets.md),
  [observability](observability-diagnostics.md), [API contracts](api-service-contracts.md).
