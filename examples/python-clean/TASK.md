# Current task

- Status: `READY`
- Objective: Add a hyphenated slug helper while preserving the existing label normalizer.
- Coordinator: `example-coordinator`
- Git holder: `example-coordinator`
- Publication: `NOT_AUTHORIZED`

## Owned paths

- `src/label_tools.py`
- `tests/test_label_tools.py`

## Acceptance

- Keep the project Python-standard-library-only.
- Start with the focused unit test below.
- Do not commit or publish; the named coordinator owns Git.

```sh
python3 -m unittest discover -s tests -v
```
