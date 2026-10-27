# Current task

- Status: `READY`
- Objective: Confirm label normalization behavior before changing any source.
- Coordinator: `fixture-target-owner`
- Git holder: `fixture-target-owner`
- Testing decision owner: `fixture-target-owner`
- Publication: `NOT_AUTHORIZED`

The named owner is part of the target's recorded state. An acceptance evaluator
observes that owner and does not inherit any of its roles.

## Owned paths

- `src/labels.py`
- `tests/test_labels.py`

## Required evidence

The handed-off source claim must be refreshed before it is trusted. The native
focused check is:

```sh
python3 -B -m unittest discover -s tests -v
```

This exercise is read-only. Do not edit, stage, commit, push, or publish.
