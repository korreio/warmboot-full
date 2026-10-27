# Decisions

Template use: merge into an existing decision source when present. Adopt to record
only a choice that affects future work and is costly to rediscover; obvious or cheaply
reversible choices do not need an entry. Use an ADR instead for a load-bearing,
cross-cutting technology or architecture choice; never record the same decision in
both systems. Replace every `{{MARKER}}` and delete this note.

- Decision-log owner: {{DECISION_LOG_OWNER}}
- Authority: records decisions; grants no Git, package, network, credential,
  deployment, release, or publication permission.
- Evidence boundary: an entry holds only for the evidence that changed the choice.
- Maintenance: add an entry when a choice that affects future work is made.
- Revisit or retire: each entry's revisit trigger reopens it; supersede rather than
  delete it.

## {{DECISION_ID}}: {{DECISION_TITLE}}

- Status: {{PROPOSED_ACCEPTED_SUPERSEDED}}
- Date / snapshot: {{DATE_OR_SNAPSHOT}}
- Decision owner: {{OWNER}}
- Context and constraint: {{WHY_A_CHOICE_WAS_REQUIRED}}
- Decision: {{CHOSEN_OPTION}}
- Alternatives considered: {{MATERIAL_ALTERNATIVES}}
- Evidence that changed the choice: {{COMMAND_OBSERVATION_OR_REFERENCE}}
- Consequences and recurring cost: {{TRADEOFFS}}
- Revisit trigger: {{CONCRETE_CHANGE_THAT_REOPENS_THE_DECISION}}
- Supersedes / superseded by: {{REFERENCE_OR_NONE}}

When the revisit trigger occurs, update the status or add a superseding entry; do not
silently rewrite the original reasoning.
