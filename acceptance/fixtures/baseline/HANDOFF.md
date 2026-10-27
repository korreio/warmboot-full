# Handoff

- Evidence state: `INHERITED`
- Source path: `src/labels.py`
- Claimed SHA-256: `0000000000000000000000000000000000000000000000000000000000000000`
- Claimed check: `python3 -B -m unittest discover -s tests -v` passed

The claim is deliberately stale acceptance-fixture data. A fresh agent must
compare it with the current source identity and mark the affected evidence for
`RERUN_NOW`; it must not silently inherit the claimed pass.
