# Route: independent review

Every code change gets independent review by at least one non-author reviewer, however
small the change. Other work gets it for material behavior, safety, migration, security,
or release risk, and whenever a stricter target or user rule requires it. For a tiny,
reversible, low-risk one-hotspot task that changes no code and has none of those
requirements, record `NOT REQUIRED` with a scope/risk reason in the task. This is a
task state, not a fourth reviewer verdict; the candidate inventory and writer
assessment still apply.

Review is a bounded decision, not a standing committee. Define the reviewed snapshot,
exact paths, acceptance criteria, hazards, and required evidence before the reviewer
starts. The coordinator materializes a digest-bound disposable target holding the exact
reviewed bytes and supplies the governing primary contract, applicable route, and
evidence boundary; read dependencies remain navigation, never additional instruction
authority. The reviewer must be independent of the reviewed authorship.

One independent review is the minimum when review is required. A stricter target or
user rule may size the review larger; the task declares the size before the review
starts.

## Reviewer procedure

1. Confirm the review target and concurrent dirt; do not silently expand scope.
2. Read the governing contract and relevant implementation and tests directly. For a
   code change, read every changed human-authored code file in full and the
   target-owned language rule; sampling is not a complete source-comprehension review.
3. Try to falsify the highest-impact claims first, including unsafe failure paths,
   stale evidence or handoffs, missing authority, and checks that prove less than
   claimed.
4. Run the cheapest valid checks available to the review scope. State anything not
   run and do not substitute a lower evidence tier.
5. Return exactly one terminal verdict:

- `CLEAN` — no actionable finding within the defined scope and evidence boundary.
- `FINDING` — one or more actionable defects, each with path/location, impact,
  reproduction or reasoning, and the acceptance condition for a fix. A behavior defect
  also names its trigger: what a user or caller does to reach it, and how often.
- `BLOCKED` — review cannot reach a valid verdict; name the missing snapshot,
  evidence, access, or authority.

Style preferences, unverified claims about provider behavior, and unrelated
improvements are not findings. `CLEAN` is scoped, not a claim that the entire project
is defect-free.

## Maintainability and test-quality lens

For consequential code, inspect assertion quality, fixture and oracle independence,
unexplained skips, and evidence-tier claims. Look for stale or misleading comments,
comments that restate code, and undocumented high-risk rationale, invariants,
assumptions, units, numerical boundaries, concurrency, retry, idempotency, caching, or
privacy behavior. Do not substitute comment, test, coverage, or tool counts for quality
evidence; ask whether the target-native rule changes a maintenance or acceptance
decision.

## Source-comprehension release gate

First reconcile the writer inventory against the coordinator-attested frozen candidate
source set. Independently inspect the derivation receipt and every resulting changed
human-authored code path, not only the task plan, tests, or architecture decisions.
An omitted authored code file is a `FINDING`. Each file must immediately orient a
reader using the target language's adopted convention; one accurate sentence is enough
for a simple file. For consequential behavior, inspect the operative code for adjacent
rationale, invariants, and applicable units, precedence and failure, state,
concurrency, security, or resource semantics. An exact ADR-section link may supplement
that local contract; tests, unlinked or remote explanations, and agent memory cannot
replace it.

Return `FINDING` when explanation is missing, stale, decorative, or merely narrates the
code, even if tests pass. Accept recorded generated, vendored, and pure re-export
exceptions. For untouched existing debt, require a risk-ranked inventory and owner
rather than silently approving it or blocking all work indefinitely. The writer's
changed-source assessment is an input, never approval.

## Fix and stop rule

Predeclare the target-native `CLEAN` threshold and freeze candidate bytes, decision,
and evidence identities. `CLEAN` means no actionable finding within that scope and
evidence boundary; no arbitrary fixed count substitutes for this dryness.

Before relaying, assigning, or fixing a delegated or reviewer-supplied claim, the
coordinator verifies it against the reviewed snapshot and, when different, the current
candidate, then records `CONFIRMED`, `REFUTED`, or `DOWNGRADED` with evidence; an
unverified claim is not a finding. A behavior claim that no user or caller can reach is
`REFUTED`.

On `FINDING`, a separate writer, not the reviewer, addresses accepted findings; the
reviewer never repairs reviewed bytes. A fix removes the cause at its owner; a guard
around the symptom is not a fix. The fix round enumerates the other members of the
class the finding or its fix names (shared base, sibling copy, second path), fixes each
inside the review scope, and records any other with its owner in the current task.
Rerun affected evidence, freeze the corrected scope, then obtain a fresh adversarial
rereview by a non-author on those unchanged bytes and evidence. Fresh means a new
judgment on the corrected scope, not a new thread, session, or provider; fresh context
alone does not erase authorship. Repeat until `CLEAN` or `BLOCKED`. When a
second fix for the same component and kind of defect comes back `FINDING`, stop
patching: return to the state before those fixes and have a different writer redo it in
a different direction, from another model family where one is reachable.

A later relevant decision, candidate-byte, or evidence change expires `CLEAN` for the
affected scope. Add a predeclared named-hazard specialist only when the task record
identifies a distinct hazard that the general review cannot reach. Stop when acceptance
evidence holds and the predeclared review requirement returns `CLEAN`; do not add
reviewers after results merely to fish for agreement.

For a substantial code package, one already-required review round uses a reviewer from
a model family different from the writer's and, when a prior round exists, the
preceding reviewer's where reachable. This selects who performs that round; it adds no
round, stop, or authority. If none is reachable, or a review lane fails, refuses, times
out, or exhausts quota, a fresh-context non-author completes the round and the record
names what happened and the unavailable evidence. The coordinator's own reread never
substitutes.

`FINDING` returns the work to a fix-and-review cycle. `BLOCKED` stops the review until
its named prerequisite changes.
