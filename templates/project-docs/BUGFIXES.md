# Observed defect ledger

Template use: merge into an existing issue, incident or bug source when it already owns
recurrence history. For a coded project, adopt when no living owner records reproduced
defects and how recurrence is checked. This is not a speculative risk list: create an
entry only after a defect is reproduced. Replace every `{{MARKER}}` and delete this note.

- Ledger owner: {{DEFECT_LEDGER_OWNER}}
- Authority: records observed defects; grants no Git, package, network, credential,
  deployment, release, or publication permission.
- Evidence boundary: an entry proves only the reproduction and regression evidence it
  cites.
- Maintenance: update when a defect is reproduced, fixed, or recurs, or when its pin
  changes.
- Revisit or retire: apply each entry's retention rule and each pin's deletion
  condition below.

For a coded project this observed-defect/recurrence role has a named owner even before a
pin is earned. Merge into the existing issue/incident/history surface when it owns the
same facts; do not invent defects or keep decorative empty entries.

## {{DEFECT_ID}} — {{OBSERVED_BEHAVIOR_SUMMARY}}

**Shape of the bug.** {{OBSERVED_BEHAVIOR_EXPECTED_BEHAVIOR_AND_MINIMAL_REPRODUCTION}}

**Why it existed.** {{LOAD_BEARING_ASSUMPTION_MISSED_EDGE_OR_OWNER_SMELL}}

**Fix.** {{SMALLEST_CAUSAL_FIX_AND_BEHAVIOR_FIRST_REGRESSION_EVIDENCE}}

- First observed/fixed snapshot: {{SNAPSHOT}}
- Fix and recurrence owner: {{FIX_AND_RECURRENCE_OWNER}}
- Recurrence signal: {{WHAT_WILL_FAIL_OR_ALERT_A_MAINTAINER}}

Optional structural/configuration pin—omit this section when the behavior test is
sufficient:

- Pin and owner: `{{PIN_PATH_OR_CHECK}}` — {{PIN_OWNER}}
- Recurrence class: {{WIRING_CONFIGURATION_ORDER_OR_OWNER_ALIGNMENT}}
- Why behavior evidence is insufficient: {{OBSERVED_GAP}}
- Recurring cost: {{TIME_DEPENDENCY_OR_MAINTENANCE_COST}}
- Deletion condition: {{STRONGER_BEHAVIOR_OR_STRUCTURE_THAT_MAKES_PIN_REDUNDANT}}

Remove the pin when its deletion condition is met. Retain or archive the defect entry
only while it changes diagnosis, release communication, or recurrence ownership.
