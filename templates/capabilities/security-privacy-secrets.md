# Security, privacy and secrets

- ID: `security-privacy-secrets`
- Trigger: the target handles credentials, personal/sensitive data, external exposure,
  dependencies, uploads, logs or privileged operations.
- Anti-trigger: adding a generic scanner without a threat, owner, target authority,
  triage path or safe artifact policy.
- Inspect before adopt: data flows/classification, trust boundaries, secret locations,
  logging/capture behavior, auth/session policy, dependency exposure, current scanners,
  suppressions and incident/recovery ownership.
- Disposition
  ([definitions](../../docs/documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit)):
  record `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT`; merge into
  existing security/privacy authorities and justify every omitted relevant control.

## Target record

- Decision owner and native command: one security/privacy owner names each local native
  check; an external scanner also needs target and network authorization.
- Authority, privacy and singletons: credentials and scan targets have one holder;
  outputs are sensitive until reviewed and must not contain secrets/user data.
- Focused evidence: local secret/PII canaries, pure policy tests and synthetic auth/error
  fixtures scoped to the changed boundary.
- Closing evidence: target-native security/privacy gates, dependency review and, only
  when authorized, bounded external evidence against the exact target.
- Recovery: stop and contain on a suspected real secret or user-data disclosure; do not
  echo it. The target incident owner rotates/removes/records under its policy.
- `UNPROVED`: absence of findings is not proof of security; local fakes do not prove
  hosted configuration, live TLS, external exposure or incident recovery.
- Recurring tax: ruleset updates, false-positive triage, suppressions, dependency alerts,
  data maps and artifact retention.
- Delete or revisit: retire a control only when its threat path disappears or a simpler
  owned control proves equal coverage; revisit after exposure/data/auth changes.

## Suggested formula

```text
threat + owned boundary -> cheapest local canary -> target-native closing check
external scan = exact authorized target + safe artifact + recovery owner
```

- Source IDs: `security-privacy-secrets-design`.
- Design evidence: [local rationale](../../docs/capability-design.md) and
  [source catalog](../../docs/capability-sources.json).
- Related cards (navigation only): [dependencies/licences](dependencies-licences.md),
  [data/database](data-database-operations.md).
