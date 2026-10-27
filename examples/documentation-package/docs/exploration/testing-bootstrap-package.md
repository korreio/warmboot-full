# Testing, bootstrap, and package lane evidence

- Owner: `testing-bootstrap-package-owner`
- Scope: define prerequisites, deterministic before/after evidence, checkout
  bootstrap, package-install reproducibility boundary, and authority gates; do
  not grant implementation rights.
- Status: `REPORTED / FROZEN` on 2026-07-31.

## Input snapshot

Snapshot `EX-TEST-INPUT-1` received `CONTEXT-01`, `LANGUAGE-01`, `TOOLING-01`, and
`ARCH-01`. Initial authority allowed read-only inspection and local interpreter
queries only. Package installation, package-index/network access, Git, remotes,
publication, deployment, and destructive cleanup were not authorized.

## Evidence design

| Claim/hazard | Cheapest valid evidence | Boundary |
|---|---|---|
| tests can detect absent behavior | run the full suite after tests exist but before source exists | red is expected; it proves sensitivity, not correctness |
| normalization contract | unit cases for whitespace, compatibility form, case folding, empty input, and exact type error | tested interpreter only |
| CLI delegates | subprocess test plus direct source CLI smoke | local process; no installed console-script claim |
| Python sources import | `python3 -m compileall -q src tests` | syntax/import signal only |
| metadata parses | standard-library `tomllib` parse | no build or install claim |
| docs route correctly | local Markdown target resolver | local links only |
| editable installation is reproducible | isolated install smoke with locally present backend or separately authorized resolver access | `UNPROVED` unless package installation is explicitly granted |

Bootstrap acceptance is deliberately no-install:

```sh
python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m label_normalizer "  Warm   BOOT  "
```

An editable install is an optional later tier. Repository-write authority does
not imply permission to create an environment, invoke `pip`, fetch a build
backend, contact an index, or publish.

## Receipt

`TEST-01 — NO-INSTALL ACCEPTANCE`: Require Python 3.11+, red/green full tests,
compile, CLI, metadata, and local-link evidence. Record the actual interpreter.
Keep Python 3.11 execution and editable-install reproducibility `UNPROVED` until
run. Any implementation receipt must state install and network/index authority
separately.
