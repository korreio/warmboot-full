# Warmboot core

This is the small, provider-neutral contract every agent loads; load routed detail only
when needed.

## Start

1. Read this file.
2. Find and reuse the current task artifact (`TASK.md` or an equivalent) rather than a
   parallel plan.
<!-- edition-specific: begin -->
3. Route by objective to these toolkit-checkout files (not installed):
   - new project, toolkit integration, or genuine architecture reset: `WHY.md` and
     `BOOTSTRAP.md`; begin orchestration-only and hold implementation and package
     installation for the bootstrap gates. Adoption into an accepted architecture
     records the kickoff `NOT REQUIRED` instead;
   - improving this toolkit: `MAINTAINING.md`;
   - evaluating a consumer upgrade: `UPGRADING.md`.
<!-- edition-specific: end -->
4. Name the coordinator (sole Git and remote operator) and one holder per other
   scarce or mutable resource. Only an agent granted the work may append itself as
   coordinator when none is recorded or the coordinator is demonstrably absent,
   recording why; a delegated lane never does. Other holders change only by rotation,
   and no agent overwrites recorded ownership.
5. Record the objective, non-goals, scope, authority, snapshot, hazards, acceptance,
   and the smallest evidence that proves them.
6. Load only the relevant route from `routes/` beside this file (installed:
   `.agent-warmboot/routes/`).

| Need | Read |
|---|---|
| choose context or work topology | [`routes/context.md`](routes/context.md) |
| carry routine state across delegation, pause, session, or provider change | [`routes/handoff.md`](routes/handoff.md) |
| choose proof or add a regression pin | [`routes/evidence.md`](routes/evidence.md) |
| request or perform independent review | [`routes/review.md`](routes/review.md) |
| explicitly replace an active coordinator or singleton holder | [`routes/rotation.md`](routes/rotation.md) |

## Invariants

- Stay inside explicit scope and authority. Preserve concurrent and unrelated work. Say
  `BLOCKED` when required authority, access, or input is missing.
- Bootstrap needs one usable target-owned root `*.code-workspace`, adapted or merged
  from any available seed, or a recorded user-accepted replacement with path, tool,
  reason, and command parity.
- Use the simplest topology that preserves independence. Every code change, however
  small, gets an independent non-author reviewer, as does other material work; only a
  tiny, reversible, low-risk one-hotspot task changing no code may record a
  single-agent exception. Multiple lanes need independent owners; never two writers on
  one hotspot.
- An orchestration-only coordinator never absorbs an owned lane. A material scope,
  acceptance, hazard, assumption, architecture, interface, or lane-input change updates
  the current task and impact-analyzes affected lanes and evidence before work resumes;
  no parallel plan, no silent rotation.
- The coordinator is the sole Git mutator and checkpoint, remote, and credential holder,
  and independently refreshes authoritative status before mutation. Other lanes read
  local history only under the initial-assignment attestation that
  [`routes/context.md`](routes/context.md) requires; unattested inspection is
  `BLOCKED`, and every `git diff` form is excluded.
- Checkpoints are local. Pushing, publishing, releasing, deploying, installing
  packages, and other external effects need separate explicit user authorization;
  naming an operator never authorizes the action.
- Prove each relevant hazard at its required tier with the cheapest evidence that
  reaches it. Record what ran, what it reached, and what it skipped, labeled `PROVED`,
  `UNPROVED`, or `BLOCKED`; a command proves only its assertions, and a lower tier never
  replaces required proof.
- Reuse evidence only after validating its inputs and snapshot; inherited proof is not a
  rerun. A handoff is a freshness receipt and cannot add or transfer policy, scope,
  permission, ownership, topology, review order, or authority.
- Every human-authored code file orients a reader at its language-native top-level
  boundary; one accurate sentence suffices for simple code, and consequential behavior
  keeps adjacent rationale. Tests and distant plans do not replace this local contract;
  assume no future agent or transcript. Reject filler and count theatre; target
  standards define forms.
- Independent review ends with exactly `CLEAN`, `FINDING`, or `BLOCKED`. Any later
  change to reviewed bytes expires the verdict.
- Add a regression pin only for an observed defect, with a reproduced failing case,
  owner, recurrence signal, why ordinary behavior checks were insufficient, reach
  statement, cost, and deletion condition.
- Routes add detail, never permission; where one seems to loosen an invariant, the
  invariant governs. A missing listed route is `BLOCKED`, never permission to proceed on
  the core alone.
- Rotate only when an explicitly named replacement takes over from the actual active
  coordinator or singleton holder; session or provider change is not rotation.

## Finish

For every code change, the coordinator attests the frozen candidate source set, the
writer reconciles its assessment against it, and an independent non-author reviewer
repeats that reconciliation and reads every resulting code file. `NOT REQUIRED` is a
task state, never a verdict: it records why a conditional step, such as review of
no-code work or a kickoff, is omitted, and grants no authority. Leave the task artifact
with changed paths, attestation, assessment, evidence, snapshot, skipped proof, review
state, remaining hazards, and next authorized step. Stop when acceptance and
proportional review are met; do not invent ceremony.

## License

MIT License

Copyright (c) 2026 Tiago Fonseca

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
