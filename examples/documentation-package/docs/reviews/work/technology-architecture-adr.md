# Reconciled ADR proposal — `ADR-0001-RECONCILED-1`

- Status: `PROPOSED_FOR_AUTHORIZATION`
- Decision owner: `example-coordinator`
- Challenge receipt: `WB-EX-CHALLENGE-001`
- Implementation authorization granted: `false`
- Installation authorization granted: `false`

Propose Python 3.11+, a pure `normalize_label(str) -> str` comparison-key owner, a thin
CLI, no runtime dependencies, and no-install source execution as required acceptance.
The original display value remains outside this package. Editable installation is an
optional, separately gated local tier; package-index/network access is a separate
external effect.

Validation is limited to the tested interpreter, behavior/CLI checks, compile, local
links, and metadata parsing. Python 3.11, editable installation, Windows, and
Claude-native execution remain `UNPROVED`. This proposal incorporates all challenge
findings but is not yet accepted and grants no implementation or installation
authority.
