# Delivery and Git hooks

- ID: `delivery-git-hooks`
- Trigger: repeated local mistakes are cheaply caught before a coordinator-selected
  checkpoint and the target has a native validation command.
- Anti-trigger: a hook would duplicate a reliable gate, mutate files unexpectedly,
  hide repository state, or give workers Git authority.
- Inspect before adopt: repository instructions, hook configuration, staged-file
  semantics, formatter behavior, CI parity, bypass/recovery path and Git ownership.
- Disposition
  ([definitions](../../docs/documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit)):
  record `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT`; default to
  `MERGE INTO EXISTING` for an owned native hook and `CITE ONLY` when the idea is useful
  but hook mutation is not authorized.

## Target record

- Decision owner and native command: the target coordinator owns Git; a hook may call
  one reviewed native check but never commits, pushes, stages or rewrites unrelated
  files.
- Authority, privacy and singletons: hook installation changes developer workflow and
  requires explicit target authority. Treat the index and working tree as singleton
  mutable resources; avoid printing staged secrets.
- Focused evidence: run the native check against a synthetic staged candidate without
  changing the real index.
- Closing evidence: compare hook and canonical gate outcomes on success and failure,
  then run the target closing set outside the hook.
- Recovery: a documented bypass is for tool failure only; the coordinator restores
  the index/worktree and records why the hook was bypassed.
- `UNPROVED`: another developer environment, provider Git semantics and hosted checks
  remain unproved until run there.
- Recurring tax: hook installation, cross-platform shell support, formatter parity and
  false-positive handling.
- Delete or revisit: delete when the canonical wrapper alone prevents recurrence or
  when hook divergence costs more than the defect it catches.

## Suggested formula

```text
candidate bytes -> isolated staged view -> target-native check -> pass/fail only
Git commit/push/stage authority -> coordinator only
```

Do not add a generic commit or push helper merely for convenience.

- Source IDs: `delivery-git-hooks-design`.
- Design evidence: [local rationale](../../docs/capability-design.md) and
  [source catalog](../../docs/capability-sources.json).
- Related cards (navigation only): [testing](testing-feedback.md),
  [security/privacy](security-privacy-secrets.md),
  [CI/build/release/deploy](ci-build-release-deploy.md).
