# Route: evidence and regression pins

Start from the hazard that could make the result wrong, unsafe, or unrecoverable.
Choose the cheapest observation that actually reaches that hazard.

## Evidence ladder

The exact ladder is project-specific, but usually moves through:

1. static inspection or a focused deterministic check;
2. focused unit/contract tests at the changed boundary;
3. integration with real adjacent components;
4. end-to-end behavior in the relevant runtime;
5. external, device, production, or human observation when that is the hazard.

Higher cost is not automatically stronger proof. Select the lowest rung that
directly exercises the claim, then add higher rungs only for uncovered hazards.
Never translate “command exited zero” into a broader claim than its assertions.

For each material claim, record:

- the hazard and required evidence tier;
- exact command or observation, snapshot, inputs, and result;
- whether evidence was rerun or inherited through a freshness check;
- skipped, unavailable, simulated, or substituted parts;
- `PROVED` (the named evidence ran and held), `UNPROVED`, or `BLOCKED`, with the
  consequence of the boundary.

`UNPROVED` means the work may exist but required evidence is absent. `BLOCKED` means
the authorized task cannot proceed safely without new input, access, or authority.
Neither is a failure to be hidden, and lower-tier evidence does not erase either.

A provider, tool, quota, or timeout failure alone is not `BLOCKED`. Preserve proof
already obtained, continue through any safe fallback, mark only the actually unreached
remainder `UNPROVED`, record what failed and what was skipped, and do not invent an
outage to justify a fallback.

## Source comprehension

Source comprehension is proved by inspecting the changed human-authored code files
against the target-native rule and recording the paths and result. A plan, test
pass, comment count, doc generator, or linter can locate candidates but
cannot prove that a human can recover purpose and consequential intent, and machine
evidence cannot show that an explanation is accurate. Record the writer's complete
changed-source assessment and the non-author read as separate human evidence.

The completeness claim needs the coordinator-attested frozen candidate source set
([context route](context.md)) and the writer's reconciliation against it; the
non-author reviewer independently reconciles it too. An unverified writer list proves
neither completeness nor review reach. Missing orientation or applicable operative
rationale blocks acceptance even when executable checks are green.

## Assertion and tier quality

For non-trivial rules, prefer focused examples plus an independent oracle: calculate
expectations from the contract or a separate derivation, not by reusing the production
algorithm or one shared synthetic fixture. Add table, property, or metamorphic checks
when invariants over ranges or transformations matter; generated cases do not prove the
generator, the oracle, or real integration.

Classify unit, integration, end-to-end, external, and human observations explicitly.
Final acceptance has zero unexplained skips. Coverage can locate unexercised critical
paths, but a percentage is not behavior evidence or a universal gate. Use mutation
testing only when surviving mutants can improve assertions at acceptable recurring
cost, and record what the mutator could not model.

## Regression pins

Add a persistent pin (test, check, fixture, or instruction) only when all are true:

- a concrete defect was observed and its minimal reproduction is recorded;
- the owner compares the proposed pin with the nearest ordinary behavior test or
  contract against the same recurrence and records why it is insufficient;
- the pin fails RED against the unfixed shape first: a pin that has never failed
  without the fix proves nothing. Reproduce the broken relationship, not merely a
  flipped assertion, and record the exact RED invocation and observed failure;
- a named owner and recurrence signal exist;
- the pin is deterministic enough to provide a useful decision;
- a deletion condition states when the pin can be removed or folded into an
  ordinary behavior test.

Every gate or pin records a one-line reach statement — what it cannot see — at
creation time.

When a mutation supplies recurrence evidence, the owner breaks the named relationship
while preserving the other asserted conditions. A failure caused by unrelated invalid
input does not prove sensitivity to that relationship.

Record its recurring time, dependency, maintenance, and CI cost where the pin lives.
Keep the defect cause and proof links in the existing fix or checkpoint receipt so a
future maintainer can recover why the pin exists. Delete it when the condition is met.
Do not add pins for imagined provider behavior, one-off style differences, or fear
without a reproduced defect.

Small evaluations are justified only when their result changes a current choice.
Prefer a disposable command/fixture and recorded decision over a benchmark store,
telemetry recorder, dashboard, service, or permanent automation.
