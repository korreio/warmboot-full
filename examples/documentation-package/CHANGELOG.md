# Changelog — example only

This file records user-visible behavior and migrations, not internal documentation,
review, or agent mechanics. A version heading does not imply a Git tag, package
publication, hosted release, or deployment.

## Unreleased

No user-visible changes. The populated documentation-package expansion is recorded
in `TASK.md` and kickoff/review artifacts because it does not change the
comparison-key API or CLI.

## 0.1.0 — 2026-07-31

### Comparison-key normalization

- Added Unicode compatibility normalization, whitespace collapse, and Unicode-aware
  case folding behind one pure function.
- Added a thin `label-normalize` command-line entry that emits one key per input.
- Defined output as a destructive comparison key; callers retain display text.

### Availability boundary

- Added a no-install source/test path for Python 3.11+ projects.
- No registry package, Git tag, remote release, hosted CI, or deployment is claimed.
  Actual evidence used Python 3.14.2; Python 3.11 and installed entry execution remain
  `UNPROVED`.
