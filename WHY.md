# Why Warmboot Full exists

A cold engineering agent can read a repository and still miss what makes it safe to own:
which source outranks which plan, where a subsystem's owner lives, what evidence proves a
claim, which local state belongs to another session, and what needs the user's authority.
Reading every old document is not a warm start; it only adds ambiguity.

Warmboot Full creates a warm path from one objective to responsible ownership. The
intended experience is one prompt: point a capable agent at this repository and the
target, state the objective, tell it to read the root agent loader, and let it take over
within the stated authority — no installer flags or topology to pick first.

## What the warm path does

### 1. Intensive one-time kickoff

For a new project or genuine architecture reset the fresh agent acts only as coordinator,
covering six independent exploration concerns with the smallest proportional multi-agent
set. `BOOTSTRAP.md` is their single home: it names them and fixes the floor of at least
two distinct non-coordinator research owners, each concern carrying an attributed evidence
artifact and receipt.

Proven prior stacks are preferred baselines when they fit; where an owner overlay exists,
the stack lane reads it. Research validates fitness rather than rewarding novelty, and
high-risk work keeps architecture and privacy separate from testing and operability.

The coordinator remains the only holder of Git mutation, checkpoints, remotes and
credentials. A bounded worker or reviewer reads local history only when it changes one
of its decisions. Its initial assignment then names the exact repository, refs, allowed
ancestry and paths, plus the narrow inspection commands from
`routes/context.md`, run with optional locks disabled. Every `git diff` form
stays excluded. The coordinator does no lane research itself. It synthesizes the six
receipts into a dated options brief, a draft ADR and a draft kickoff plan with separate
implementation and install gates. A distinct non-author owner challenges them, and the
coordinator disposes of each challenge. Missing research stays `UNPROVED` or `BLOCKED`,
never invented; code and installation wait for an accepted ADR and `AUTHORIZED` gates.

### 2. Lean steady-state ownership

Kickoff and a genuine architecture reset are the only automatic triggers for that
exploration. Afterwards the project keeps a tiny always-loaded safety core and routes to
richer documentation only when needed. Topology stays proportional: one writer by default,
an independent reviewer for every code change and other material risk, more lanes only for
genuinely independent work. Build history, examples and acceptance
machinery stay discoverable without becoming startup context.

The documentation package is the navigation architecture:
`docs/documentation-architecture.md` assigns one authority per documentation role, and
each role is adopted, merged, cited only, or omitted on target value. No sample installs
itself.

The human workspace is different: every fresh project leaves one useful target-owned root
VS Code workspace, or an explicitly user-accepted replacement, so owner and agents share a
current way to open, navigate, test, run and debug the project without it becoming
policy.

Source is also a human entry surface. Every human-authored code file gives a reader an
immediate language-native statement of its role; consequential behavior keeps its
operative why, invariant, units and failure semantics beside the decision. Tests and
ADRs deepen that contract but cannot make a human search the repository or reconstruct
an agent transcript merely to learn what a file owns. Generated, vendored and purely
mechanical forwarding code is identified rather than padded.

Scripts stay secondary: `bin/warmboot` previews, copies and compares a known bundle, but
it cannot understand an objective, select a stack, reconcile existing rules, accept risk,
review its own work, or own the project workspace.

## Success means

- one objective and one entry point let a fresh agent discover the takeover protocol,
  documentation roles and templates;
- the agent inspects before mutating and keeps the user out of installer mechanics;
- the architecture choice is current, source-backed, objective-specific, and honest about
  unavailable evidence;
- proven stacks are reused when suitable and novelty is justified when not;
- docs have one authority per role, visible update triggers, and deletion conditions;
- a human can open any human-authored code file, learn its role immediately, and locate the
  applicable local rationale without assuming the creating agent still exists;
- the workspace's folders and commands match their current owners;
- native tests, review, recovery points and publication authority stay distinct;
- a fresh agent recovers task, ownership and freshness boundaries from the installed
  contract.

## This is not

Warmboot Full is not a project generator, fixed technology stack, documentation dump,
agent scheduler, benchmark database, dashboard, telemetry recorder, deployment or
publishing pipeline, or permanent multi-agent ceremony. It does not make scripts the
owner, archive every review, require generated indexes, or claim cross-provider parity
before provider-native evidence and independent review close it.
Warmboot is not a substitute for project knowledge, architecture judgment, tests, access
control, or human accountability.

This file is one-time adoption context, never an automatic target payload. A bootstrap
coordinator may classify it `ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY`, or `OMIT`, and
adapt it only when accurate, target-owned, and worth its cost.
