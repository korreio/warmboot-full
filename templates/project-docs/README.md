# {{PROJECT_NAME}}

Template use: merge into the existing project README when it already orients people.
Adopt only when the project lacks a current entry point. Omit a second README. Replace
every `{{MARKER}}`, remove inapplicable rows, and delete this note.

- Document owner: {{ONBOARDING_OWNER}}
- Authority: explains the project; grants no Git, package, network, credential,
  deployment, release, or publication permission.
- Evidence boundary: commands below establish only their stated local result.
- Maintenance: update when setup, entry points, architecture routes, or user-visible
  purpose changes.
- Revisit or retire: merge when another entry point becomes authoritative; remove when
  the project no longer needs separate onboarding.

{{ONE_SENTENCE_PROJECT_OUTCOME}}

## Current state and architecture

- Lifecycle/status: {{CURRENT_STATUS_AND_LAST_VERIFIED_DATE}}
- Technology/architecture decision: `{{ADR_PATH_OR_NOT_YET_DECIDED}}`
- Active kickoff/task plan: `{{PLAN_OR_TASK_PATH}}`
- Known evidence limits: {{UNPROVED_OR_BLOCKED_BOUNDARIES}}

{{PLAIN_LANGUAGE_SYSTEM_SHAPE_AND_WHY_THE_CHOSEN_STACK_FITS}}

## Start

Requirements: {{RUNTIME_AND_VERSION_REQUIREMENTS}}

Human workspace: open `{{ROOT_CODE_WORKSPACE_OR_ACCEPTED_REPLACEMENT}}`. It is the
target-owned navigation/command interface; current source, docs, tests, and ADRs remain
truth.

| Intent | Native command | What success establishes |
|---|---|---|
| Set up locally | `{{SETUP_COMMAND}}` | {{SETUP_EVIDENCE}} |
| Run a focused check | `{{FOCUSED_CHECK_COMMAND}}` | {{FOCUSED_EVIDENCE}} |
| Run the ordinary suite | `{{NATIVE_TEST_COMMAND}}` | {{SUITE_EVIDENCE}} |
| Run locally | `{{RUN_COMMAND}}` | {{LOCAL_RUNTIME_EVIDENCE}} |

## Operating boundary

- Source owner: {{SOURCE_OWNER}}
- Current task and Git holder: {{CURRENT_TASK_ARTIFACT}}
- Agent instructions: {{AGENT_ENTRY_PATH}}
- External effects: {{PUBLISH_DEPLOY_DATA_AUTHORITY}}
- Sensitive or excluded data: {{PRIVACY_BOUNDARY}}

## Stable contract

- {{INVARIANT_ONE}}
- {{INVARIANT_TWO}}

Use the project-native standards and system map if those roles were adopted. Report
commands actually run and state required unavailable proof as `UNPROVED` or
`BLOCKED`; a successful setup command is not proof of runtime behavior.

## Documentation route

| Need | Current owner |
|---|---|
| Agent startup and task routing | `{{AGENT_ENTRY_PATH}}` |
| Architecture and ownership | `{{SYSTEM_MAP_OR_ARCHITECTURE_PATH}}` |
| Technology choice and alternatives | `{{TECHNOLOGY_ADR_AND_RESEARCH_PATHS}}` |
| Engineering and test commands | `{{STANDARDS_AND_TESTING_PATHS}}` |
| Source roles and consequential rationale | immediate language-native source contracts; `{{SYSTEM_MAP_OR_ARCHITECTURE_PATH}}` for cross-cutting routes |
| Current quality assessment/control loop | `{{QUALITY_CONTROL_PATH_OR_PLAN_SECTION}}` |
| Current execution state | `{{CURRENT_PLAN_OR_TASK}}` |
