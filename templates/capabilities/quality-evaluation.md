# Quality evaluation

- ID: `quality-evaluation`
- Trigger: a bounded evaluation can change a real architecture, usability, performance
  or release decision.
- Anti-trigger: the metric has no decision owner, threshold, action or deletion rule,
  or would create a dashboard/benchmark bureaucracy.
- Inspect before adopt: target outcomes, current tests, user-facing risks, existing
  performance/accessibility/visual checks, representative fixtures and evidence cost.
- Disposition
  ([definitions](../../docs/documentation-architecture.md#disposition-adopt-merge-into-existing-cite-only-omit)):
  record `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT`; state the
  decision the evaluation can change before adding it.

## Target record

- Decision owner and native command: one target owner names a bounded local/native
  evaluation and its decision threshold.
- Authority, privacy and singletons: classify screenshots, traces, prompts, outputs and
  user-derived fixtures; one holder owns each report directory/browser/session/model.
- Focused evidence: a representative local fixture and the smallest measurement that
  distinguishes the candidate choices.
- Closing evidence: repeat the accepted evaluation on frozen inputs, record variance
  and combine it with target-native correctness checks.
- Recovery: stop on sensitive capture, non-representative input, unstable measurement
  or a metric that cannot change the decision; discard unsafe artifacts via the target
  owner.
- `UNPROVED`: a synthetic score does not prove production usability, accessibility,
  model quality, device behavior or user value.
- Recurring tax: fixture curation, runtime, result interpretation, threshold drift and
  artifact review.
- Delete or revisit: delete after the decision if recurrence is not useful; revisit on
  a changed user outcome, platform or observed quality regression.

## Suggested formula

```text
decision -> representative frozen input -> cheapest discriminating measure
measure + correctness evidence -> choose | reject | UNPROVED
```

- Source IDs: `quality-evaluation-design`.
- Design evidence: [local rationale](../../docs/capability-design.md) and
  [source catalog](../../docs/capability-sources.json).
- Related cards (navigation only): [testing](testing-feedback.md),
  [graphics](code-native-graphics.md), [observability](observability-diagnostics.md).
