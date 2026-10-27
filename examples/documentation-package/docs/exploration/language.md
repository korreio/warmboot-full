# Language lane evidence

- Owner: `language-owner`
- Scope: compare language choices against the required Unicode semantics and
  offline execution boundary; do not choose product architecture or portfolio
  stack composition.
- Status: `REPORTED / FROZEN` on 2026-07-31.

## Input snapshot

Snapshot `EX-LANGUAGE-INPUT-1` received `CONTEXT-01`, a host with `python3`
available, and three bounded candidates: a POSIX shell pipeline, Python, and
JavaScript/TypeScript. Required semantics were compatibility normalization,
whitespace collapse, and caseless comparison.

## Evidence

Illustrative source titles (synthetic; not retrieved for this example):

| Evidence | Decision-relevant fact | Limit |
|---|---|---|
| Python version status | Python 3.11 remained in security support; 3.13 and 3.14 were in bugfix support | support status is time-sensitive; the scenario illustrates 3.14.2; actual execution needs separate evidence |
| Python Unicode HOWTO | documents normalization for equivalent representations and `casefold()` for caseless matching, including `ß` to `ss` | does not prove keys remain byte-stable across future Unicode database changes |
| Python `unicodedata` | defines NFKC compatibility decomposition followed by canonical composition | proves availability/semantics, not performance superiority |

| Candidate | Fit conclusion |
|---|---|
| POSIX shell | would depend on external utilities and locale/platform behavior for the required Unicode rule |
| Python | directly exposes every required operation in its standard library and was already locally available |
| JavaScript/TypeScript | capable, but adds a Node/tooling boundary without an accepted JS consumer |

No cross-language benchmark was required because throughput was not an accepted
criterion. No “best language” or current-SOTA claim was made.

## Receipt

`LANGUAGE-01 — RECOMMEND PYTHON`: Use supported Python with a declared 3.11 floor
and a standard-library runtime. Record Python 3.11 execution and cross-version
Unicode-key stability as `UNPROVED`; validate the actual local interpreter.
