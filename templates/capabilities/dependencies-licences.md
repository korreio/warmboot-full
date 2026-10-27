# Dependencies, licences and supply chain

- ID: `dependencies-licences`
- Trigger: a target adds or updates packages, runtimes, generated artifacts, vendored
  code or material intended for redistribution.
- Anti-trigger: inventory for its own sake with no install, security, licence,
  reproducibility or publication decision.
- Inspect before adopt: manifests/lockfiles, runtime pins, package owners, update policy,
  transitive risks, vendored/generated provenance, licences and redistribution intent.
- Disposition
  ([definitions](../../docs/documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit)):
  record `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT`; existing
  package/update authorities survive and every new dependency carries a reason.

## Target record

- Decision owner and native command: name one owner per package/runtime surface and the
  target-native lock/audit/licence command; installation remains separately authorized.
- Authority, privacy and singletons: registry credentials, private package names and
  audit outputs are classified; one holder owns lockfile or vendored updates.
- Focused evidence: parse/lock consistency and a local audit/licence check on frozen
  manifests without changing them.
- Closing evidence: target-native build/test with exact locks plus reviewed licence and
  provenance for anything distributed.
- Recovery: stop on unknown licence, mutable/unpinned source, compromised advisory,
  unexpected lock rewrite or unavailable private registry; the dependency owner chooses
  replacement, pin or removal.
- `UNPROVED`: scanner silence does not prove absence of vulnerabilities or legal
  suitability; unrun platform builds remain explicit.
- Recurring tax: updates, advisories, lock conflicts, licence notices, registry/runtime
  support and vendored fork maintenance.
- Delete or revisit: remove unused packages and tools; revisit on advisory, licence,
  runtime, distribution or support-policy change.

## Suggested formula

```text
capability need -> existing platform feature? -> smallest owned dependency
manifest + lock + licence/provenance + native build/test -> accepted
```

- Source IDs: `dependencies-licences-design`.
- Design evidence: [local rationale](../../docs/capability-design.md) and
  [source catalog](../../docs/capability-sources.json).
- Related cards (navigation only): [security/privacy](security-privacy-secrets.md),
  [CI/build/release/deploy](ci-build-release-deploy.md).
