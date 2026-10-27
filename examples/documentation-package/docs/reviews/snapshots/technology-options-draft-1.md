# Technology/options brief draft — `TECH-DRAFT-1`

- Status: `DRAFT_FOR_CHALLENGE`
- Synthetic teaching snapshot: invented reference shapes and receipts, not historical source retrieval.
- Synthesizer: `example-coordinator` (no lane research)
- Inputs: `CONTEXT-01`, `LANGUAGE-01`, `STACK-01`, `TOOLING-01`, `ARCH-01`, `TEST-01`

## Objective and criteria

Build a small package that normalizes human labels and demonstrates the documentation
package. Prefer an offline-capable, provider-neutral result with low recurring cost for
one maintainer. Compare options on Unicode normalization and caseless matching, local
execution, singular behavior ownership, appropriate reuse of target capabilities, maintenance cost, and
optional packaging.

## Options

- Shell has the smallest launch surface, but the required Unicode behavior would
  depend on external tools and locale/platform behavior.
- Python's standard library directly provides NFKC normalization, case folding, CLI
  parsing, and tests; Python 3.11+ is the proposed prerequisite.
- JavaScript/TypeScript is a possible CLI choice but adds a Node/tooling
  boundary with no accepted JS consumer.
- The invented service/application reference shapes or their combination are
  disproportionate for one pure CLI rule.
- A third-party Python framework adds dependency and installation tax without an
  accepted need.

## Draft recommendation and evidence boundary

Choose Python 3.11+, one pure normalization owner, a thin CLI, standard-library tests,
and `pyproject.toml`. A checkout should run tests and the module without runtime
dependencies. An editable install may be tried as a packaging smoke after behavior is
green.

Official Python version and Unicode documentation support the runtime and semantic
claims; PyPA documents `pyproject.toml` build requirements and metadata. This draft
makes no performance, Windows, provider-parity, or current-SOTA claim.
