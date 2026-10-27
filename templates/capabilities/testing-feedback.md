# Testing and fast feedback

- ID: `testing-feedback`
- Trigger: the target needs a repeatable smallest check for changed behavior and a
  distinct closing set before a reviewed checkpoint.
- Anti-trigger: the target already has one clear native test owner and wrappers whose
  selection, escalation and closing semantics are current.
- Inspect before adopt: test manifests, native wrapper entry points, CI parity,
  changed-boundary rules, flaky/slow tiers, coverage policy and existing defect pins.
- Disposition
  ([definitions](../../docs/documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit)):
  record `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT`, the target
  constraint, destination, surviving owner and evidence. Prefer `MERGE INTO EXISTING`
  when credible wrappers already exist.

## Target record

- Decision owner and native command: name one target owner and one accepted native
  command, or an existing wrapper when the target already owns one; do not invent a
  wrapper or make this card the command authority.
- Execution: use the target's accepted native commands or existing wrappers.
  Focused and closing checks may share one command when it proves both needs.
- Authority, privacy and singletons: local read/execute authority only unless the
  target separately grants more. Classify fixtures, logs and snapshots; name holders
  for ports, emulators, databases, devices and generated reports.
- Focused evidence: the smallest native test set that exercises the changed boundary.
- Closing evidence: the target's accepted full/local closing command, or existing
  wrapper when one exists, plus required static, integration or UI gates.
- Recovery: stop on destructive setup, leaked sensitive output, unknown shared state
  or a wrapper/CI mismatch; the named target owner restores the fixture or resource.
- `UNPROVED`: skipped slow tiers, real services, devices, provider behavior and any
  semantic gap between fakes and production remain explicit.
- Recurring tax: wrapper upkeep, selection rules, fixtures, runtime and flaky-test
  handling.
- Delete or revisit: merge the quick/full split when two consecutive changes gain no
  decision value, or revisit when escaped defects show the closing set is incomplete.

## Suggested formula

```text
changed boundary
-> one owned target-native quick command or existing wrapper
-> escalate on contract/state/concurrency/integration hazard
-> one owned closing command or existing wrapper
-> report every unavailable tier as UNPROVED
```

Observed defects may earn a pin only with a recurrence signal, an explanation of why
behavior checks were insufficient, an owner and a deletion condition.

Keep unit, integration, consumer/provider contract, end-to-end, external, and human
evidence labelled separately. For consequential algorithms, select focused table,
property, or metamorphic checks whose expectations come from an independent calculation
or oracle rather than the production fixture builder. Independence is derivation
provenance, not merely a different agent identity. Review assertion sensitivity and
fixture independence. Use coverage to locate blind critical paths, not to reward a
percentage, and mutation testing only where its incremental signal justifies its cost.
Every skip has a reason, owner, consequence, and final-acceptance disposition; a required
unrun tier remains `UNPROVED` or `BLOCKED`.

- Source IDs: `testing-feedback-design`.
- Design evidence: [local rationale](../../docs/capability-design.md) and
  [source catalog](../../docs/capability-sources.json).
- Related cards (navigation only): [CI/build/release/deploy](ci-build-release-deploy.md),
  [quality evaluation](quality-evaluation.md), [device/rig/app control](device-rig-app-control.md).
