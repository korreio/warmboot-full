# Tooling lane evidence

- Owner: `tooling-owner`
- Scope: choose local development, test, metadata, and workspace surfaces after
  language selection; do not grant package installation or network authority.
- Status: `REPORTED / FROZEN` on 2026-07-31.

## Input snapshot

Snapshot `EX-TOOLING-INPUT-1` received `LANGUAGE-01`, `STACK-01`, the requirement
for a clean no-install run, and a host exposing `python3`. The project needed one
library entry, one CLI entry, deterministic tests, and editor-neutral ownership.

## Evidence

| Need | Candidate/result | Evidence and cost judgment |
|---|---|---|
| behavior tests | standard-library `unittest` | supports unit and subprocess tests without another dependency or configuration surface |
| CLI | standard-library `argparse` | provides help/error handling while the adapter delegates behavior |
| syntax check | standard-library `compileall` | cheap import/syntax signal, explicitly not behavior proof |
| metadata | `pyproject.toml` | PyPA guidance defines build-system dependencies and project metadata in one surface |
| checkout run | `PYTHONPATH=src python3 -m label_normalizer` | avoids build-backend and package-index prerequisites |
| optional install | setuptools-backed entry point | useful only under a separate install grant; backend availability remains `UNPROVED` |
| editor/workspace | target-owned `label-normalizer.code-workspace` | the required named root and two no-install native tasks improve human/agent discovery without adding runtime dependencies; no launch entry is earned |

The package metadata describes an optional distribution surface. It neither
proves installation nor authorizes a package manager to resolve the build
backend.

## Receipt

`TOOLING-01 — STANDARD LIBRARY FIRST`: Use `unittest`, `argparse`, `compileall`,
source execution, and one `pyproject.toml`. Keep runtime dependencies empty.
Treat editable installation, build-backend acquisition, and index access as
separate, ungranted actions.
