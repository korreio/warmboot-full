# Kickoff plan draft — `PLAN-DRAFT-1`

- Status: `AWAITING_IMPLEMENTATION_AUTHORIZATION`
- `implementation_authorized`: `false`
- `install_authorized`: `false`
- External effects authorized: `false`

## Preconditions and proposed work

Python 3.11+ and ordinary local shell tools are proposed prerequisites. Discovery and
challenge are read-only. Git, remotes, publication, deployment, network access, and
destructive cleanup are not authorized.

Completed discovery receipts are `CONTEXT-01`, `LANGUAGE-01`, `STACK-01`,
`TOOLING-01`, `ARCH-01`, and `TEST-01`. The coordinator synthesized them into
`TECH-DRAFT-1` and `ADR-0001-DRAFT-1`. The seventh owner must challenge all three
drafts before any authorization decision.

After challenge, the proposed sequence is to disposition findings, refresh stale
handoff evidence, seek ADR acceptance and explicit plan authorization, assign one
bounded writer, run red-first tests, implement the pure owner and thin CLI, and obtain
independent final review.

Proposed evidence includes full tests, compile, CLI, links, and metadata. An optional
isolated editable install is a separately gated tier. This draft deliberately preserves
the ambiguity about install authority and the overbroad “normalized label” wording for
the challenger to detect.
