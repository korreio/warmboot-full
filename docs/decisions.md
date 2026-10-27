# Current decisions

| Decision | Reason and owning contract |
|---|---|
| One repository, separate consumer and maintainer planes | A consumer needs the small core, not toolkit maintenance ceremony. [ADR 0001](adr/0001-single-repository-self-hosting-and-release-boundary.md) |
| Explicit ownership and authority | Parallel work must not collide or infer permission from a role. [Core](../WARMBOOT.md) |
| Create-only helper | A failed installation preserves inspectable state instead of overwriting or deleting target work. [README](../README.md) |
| Local manifests are structural evidence | Self-declared hashes cannot authenticate their own source. [Release contract](release.md) |
| Optional capability cards | Reuse useful decisions while native tooling remains authoritative. [Capability rationale](capability-design.md) |
| Small routed context | Load a rule when its boundary matters. [Context route](../routes/context.md) |
| Two editions, maintained separately | ADR 0001 governs this repository's own maintenance. Warmboot Light is a separately maintained edition with its own evidence, not a copied documentation tree. The parts shared with Warmboot Light are the same bytes in both editions: `bin/warmboot` (including the installed loader text), the five routes under `routes/`, the text of `WARMBOOT.md` outside its marked edition block, `LICENSE`, `templates/TASK.md` and `templates/HANDOFF.md`, the three shared README pictures (session loop, stale evidence, edition), the "Which edition?" text, the shared part of BOOTSTRAP's "Existing agent instructions", the README section headings, `tools/render_mermaid_docs.py` with `tests/test_render_mermaid_docs.py`, `.ruff.toml`, `.editorconfig`, `.gitattributes`, and `.github/SECURITY.md`, `.github/CONTRIBUTING.md` and `.github/ISSUE_TEMPLATE/`. They are aligned by hand and compared byte for byte: the core after removing its edition block, the rendered PNGs by hash after a clean render. The remaining differences are each core's edition block, Full's extra tooling and documents, and each edition's own BOOTSTRAP sections, tests, ledgers and changelogs. [ADR 0001](adr/0001-single-repository-self-hosting-and-release-boundary.md) |
| Explicit licence and required notices | Publication needs one deliberate licence grant and every required third-party notice. [Licence map](../LICENSING.md) |

[ADRs](adr/) are numbered. IDs are permanent and never reused; retired records leave gaps.

The current task records work in progress. This document preserves reasons that affect
future choices, rather than a transcript of past agent sessions. Update a decision when
its tradeoff changes; retain one authoritative owner per fact.

Bounded history inspection follows `routes/context.md`; every `git diff`
form remains excluded and no source lesson grants Git mutation authority.
