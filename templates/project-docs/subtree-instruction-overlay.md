# {{SUBTREE_NAME}} instruction overlay

Template use: merge into the closest existing local instruction file when present.
This file is optional: adopt it at a real subtree boundary only when local ownership,
commands, or hazards differ from the root contract. Do not copy the root safety core
into this file. Replace every `{{MARKER}}` and delete this note.

- Closest-local instruction owner: {{LOCAL_INSTRUCTION_OWNER}}
- Authority: adds local routes and may override only the named root items below,
  inside this subtree; grants no other permission.
- Evidence boundary: following a local route proves nothing until its routed evidence
  runs.
- Maintenance: update when local ownership, commands, or hazards change.
- Revisit or retire: remove the overlay when the root contract or source makes it
  redundant.
- Applies only under: `{{SUBTREE_PATH}}`
- Root instruction authority: `{{ROOT_AGENTS_OR_NEUTRAL_CONTRACT_PATH}}`
- Last verified against: {{SNAPSHOT_OR_DATE}}
- Why the overlay is earned: {{CONCRETE_LOCAL_BOUNDARY_OR_HAZARD}}

## Precedence

Read the root contract first. For work inside this subtree, the closest applicable
local overlay adds local routes and may override only the root item named below. The
root remains authoritative everywhere else. If two local files claim the same path,
the closest file wins only for its declared subtree and the conflicting routes must be
reconciled; do not maintain duplicate global policy in nested files.

| Root item affected | Local rule or route | Why it differs here | Local owner | Retirement trigger |
|---|---|---|---|---|
| {{ROOT_SECTION_ROUTE_OR_NONE}} | {{LOCAL_ADDITION_OR_EXPLICIT_OVERRIDE}} | {{TARGET_SPECIFIC_REASON}} | {{OWNER}} | {{WHEN_ROOT_OR_SOURCE_MAKES_THIS_REDUNDANT}} |

## Local task route

| Work in this subtree | Read before editing | Focused proof | Closing proof / unavailable boundary | Mutable resource holder |
|---|---|---|---|---|
| {{TASK_SHAPE}} | `{{LOCAL_SOURCE_CONTRACT_AND_PLAN_PATHS}}` | `{{FOCUSED_NATIVE_CHECK}}` | `{{CLOSING_CHECK_OR_UNPROVED_LIMIT}}` | {{RESOURCE_AND_HOLDER_OR_NONE}} |

## Delivery

Apply root Git, remote, external-effect, review, and handoff rules without restating
them. Update or delete this overlay in the same change when its subtree, local owner,
route, command, or retirement condition changes.
