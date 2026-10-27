# Code-native diagrams and graphics

- ID: `code-native-graphics`
- Trigger: a state, ownership, dependency or sequence relationship is materially easier
  to review visually and should remain diffable with the code/docs it explains.
- Anti-trigger: prose or a small table is clearer, or rendering adds a second design
  authority with no owner.
- Inspect before adopt: existing documentation renderer, diagram syntax, generated-file
  policy, link/image conventions, accessibility needs and stale-output checks.
- Disposition
  ([definitions](../../docs/documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit)):
  record `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT`; prefer the
  target's existing diagram and documentation toolchain.

## Target record

- Decision owner and native command: the owning document/component owns source truth;
  one target-native renderer/check command owns generated output if output is committed.
- Authority, privacy and singletons: diagrams must not expose private topology, account
  IDs, endpoints, credentials or user data. One holder owns generated output paths.
- Focused evidence: parse/render only the changed diagram and inspect its labels,
  direction and accessibility text.
- Closing evidence: target docs/link/render checks plus stale-output parity when
  generated artifacts are committed.
- Recovery: retain the textual/source authority when rendering is unavailable; remove
  a generated output that could disclose restricted detail.
- `UNPROVED`: parser success does not prove semantic correctness or visual readability;
  an unavailable renderer remains explicit.
- Recurring tax: renderer pinning, generated diffs, accessibility, privacy review and
  source/output parity.
- Delete or revisit: replace a diagram with prose/table when it ceases to aid a real
  decision; revisit after ownership or flow changes.

## Suggested formula

```text
owned model/state -> code-native diagram source -> deterministic render if needed
source change -> semantic review + render/link parity
```

- Source IDs: `code-native-graphics-design`.
- Design evidence: [local rationale](../../docs/capability-design.md) and
  [source catalog](../../docs/capability-sources.json).
- Related cards (navigation only): [quality](quality-evaluation.md),
  [API contracts](api-service-contracts.md).
