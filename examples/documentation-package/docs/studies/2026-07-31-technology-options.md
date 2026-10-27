# Technology and options study — 2026-07-31

This is a synthetic teaching synthesis for the example project. Its date, lane
receipts and decisions illustrate a kickoff workflow; they are not evidence of a
historical agent team, source retrieval or current test results. The concrete decision
is deliberately narrow, not a generally best language or stack.

## Illustrative owner evidence

| Lane evidence | Example receipt | What the synthesis uses |
|---|---|---|
| [Context](../exploration/context.md) | `CONTEXT-01` | Comparison-key outcome, no-install usability, display preservation and non-goals |
| [Language](../exploration/language.md) | `LANGUAGE-01` | Unicode behavior and bounded language comparison |
| [Stack comparison](../exploration/stack-portfolio.md) | `STACK-01` | Invented reference shapes, objective fit and recurring cost |
| [Tooling](../exploration/tooling.md) | `TOOLING-01` | Standard-library tools, metadata boundary and editor-neutral setup |
| [Architecture, risk and privacy](../exploration/architecture-risk-privacy.md) | `ARCH-01` | One pure owner, thin adapter, destructive-output risk and no-retention boundary |
| [Testing and bootstrap](../exploration/testing-bootstrap-package.md) | `TEST-01` | Native checks, prerequisites and separate installation/network gates |

These records demonstrate how independently owned concerns inform one decision.
Their statuses do not prove live exploration. Ordinary feature work reads only the
roles relevant to its current decision.

## Decision to support

Choose a small language, stack boundary and local toolchain for deterministic
Unicode-aware comparison keys through a command line. The result should remain
understandable to one maintainer and run from a checkout without package installation
or network access.

Decision criteria, in priority order:

1. testable normalization and caseless matching;
2. offline source execution with locally available tools;
3. one behavior owner and a thin adapter;
4. reuse of existing target capability where it fits;
5. low learning, upgrade, security, operations and removal cost;
6. optional packaging kept outside required acceptance.

## Language comparison

| Option | Fit | Cost or unresolved boundary | Example disposition |
|---|---|---|---|
| POSIX shell pipeline | Small launch surface | Unicode behavior would depend on utilities, locale and platform; matching the required semantics needs separate proof | Reject for this objective |
| Python | Standard-library normalization, case folding, argument parsing and tests | Interpreter prerequisite; Unicode database behavior can change with interpreter versions | Choose |
| JavaScript/TypeScript | Can implement a CLI | Adds a Node/tooling boundary without an accepted interface, service or shared-library caller | Reject for this objective, not globally |

Python exposes normalization through `unicodedata.normalize` and caseless matching
through `str.casefold()`. The example uses NFKC compatibility normalization and the
`ß` to `ss` case-folding behavior. Native tests must establish the selected behavior;
this comparison is not a cross-language benchmark.

## Stack comparison from `STACK-01`

The reference shapes in the sibling [stack comparison](../exploration/stack-portfolio.md)
are illustrative. They describe possible architectural boundaries.

| Invented reference shape | Objective fit | Hypothetical upkeep | Example disposition |
|---|---|---|---|
| `REFERENCE_SERVICE` | No remote caller or persistence requirement | Service and runtime separation would need maintenance without a caller | Do not import |
| `REFERENCE_APP` | No interactive interface or data requirement | Interface, browser and database boundaries would add unused upkeep | Do not import |
| `SMALL_COMBINATION` | Selecting pieces is possible, but no larger boundary is required | Cross-runtime composition still needs an accepted caller | Do not compose |
| Python standard-library slice | Matches one offline text function and a CLI | Interpreter lifecycle; optional packaging remains separate | Choose |

The lesson is to select a boundary for the accepted outcome.

## Tooling comparison

| Need | Example choice | Reason and limit |
|---|---|---|
| Behavior tests | `unittest` | Standard-library tests for the small API and subprocess CLI |
| CLI parsing | `argparse` | Keeps the adapter thin |
| Syntax/import check | `compileall` | A local syntax signal, not behavior proof |
| Metadata | `pyproject.toml` | Parsing does not prove installation |
| Bootstrap | Source execution through `PYTHONPATH=src` | No dependency or build-backend installation required |
| Optional console entry point | Setuptools build backend | Separate authorized installation tier; backend availability remains unproved |
| Human workspace | `label-normalizer.code-workspace` | Named root and native tasks; no additional launch or runtime dependency is needed |

## Technical concepts illustrated

The Python Unicode HOWTO and `unicodedata` documentation explain case folding and
normalization. PyPA's guidance on `pyproject.toml` distinguishes build dependencies
from project metadata. These source titles orient the example's technical concepts;
this synthetic record does not assert a fresh retrieval, a runtime support-lifecycle
check or an observed execution on a particular Python version.

## Decision and dispositions

Choose Python 3.11 or later as the example's declared floor, with a standard-library
runtime, one pure normalization owner, a thin `argparse` CLI, `unittest` and optional
packaging metadata. Acceptance uses source execution. [ADR 0001](../adr/0001-python-standard-library-core.md)
owns the example decision; the [adoption record](../adoption-disposition.md) shows how
to adopt, merge, cite or omit useful techniques without creating duplicate authority.

The selected boundary serves the CLI outcome without an invented service, interface,
database or deployment need. A real target must establish applicability and authority
from its own evidence; the teaching dispositions grant neither implementation nor
installation permission.

## Evidence limits and re-evaluation

The records illustrate checks and recovery relationships. Actual results for current
bytes belong to the toolkit's current task; these receipts prove no live agent team,
provider parity, platform matrix or package installation. Execution on the declared
Python floor and stable keys across interpreter/Unicode database upgrades require
separate evidence. No performance, memory or cross-language benchmark is claimed.

Revisit the decision when an accepted requirement needs stable serialized keys across
upgrades, a non-Python caller, locale-specific collation, high-volume performance,
a third-party dependency or installation as required acceptance. Refresh only the
evidence that can change that choice.
