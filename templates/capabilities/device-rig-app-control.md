# Device rig, app and LLM control

- ID: `device-rig-app-control`
- Trigger: the target outcome depends on a physical device, device simulator, app
  automation or an LLM-controlled action boundary.
- Anti-trigger: hardware is unnecessary, simulation can answer the decision, no exact
  target/holder exists, or live/credentialed action authority is absent.
- Inspect before adopt: target rig/simulator/app-control owners, lease identity, exact
  device/port/session, allowlisted semantics, redaction, same-child evidence, abort and
  recovery, process cleanup and verdict separation.
- Disposition
  ([definitions](../../docs/documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit)):
  record `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT`; merge into
  the target's existing rig/simulator/control boundary.

## Target record

- Decision owner and native command: one named holder controls each rig, device,
  simulator, app session, port and LLM action session. Use target-native controls only.
- Authority, privacy and singletons: default to simulator/fakes. Live devices, user
  data, credentials, screenshots, logs, model prompts and mutations need separate exact
  authority and redacted evidence.
- Focused evidence: pure parser/state tests, fake process/port/session seams and a local
  simulator with an explicit no-live-action receipt.
- Closing evidence: target-native simulator/integration set and, only when authorized,
  hazard-first live evidence on the exact leased target with independent verdict.
- Recovery: abort on identity mismatch, lost lease, unsafe action, wrong child/process,
  sensitive output or uncertain physical state; the named holder performs bounded
  recovery, teardown and explicit release.
- `UNPROVED`: simulation does not prove timing, device software, OS automation, physical
  motion, account state, model behavior or recovery on real hardware.
- Recurring tax: simulator parity, drivers/toolchains, device availability, leases,
  flake triage, privacy scrubbing, device software/OS/model drift and recovery rehearsal.
- Delete or revisit: remove control layers when the device/action boundary disappears;
  revisit on protocol, device software, OS, driver, model, safety or rig topology change.

## Suggested pseudocode

```text
acquire(exact_target, named_holder)
assert lease_and_identity
prefer simulator; allow only semantic actions
bind evidence to same child/session; redact inputs and outputs
abort safely on mismatch; recover within bounded owner runbook
release explicitly; controller never awards its own verdict
```

- Source IDs: `device-rig-app-control-design`.
- Design evidence: [local rationale](../../docs/capability-design.md) and
  [source catalog](../../docs/capability-sources.json).
- Related cards (navigation only): [testing](testing-feedback.md),
  [security/privacy](security-privacy-secrets.md), [API contracts](api-service-contracts.md).
