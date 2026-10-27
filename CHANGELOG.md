# Changelog

## Unreleased

- Release validation rejects malformed domain values and symlinked include ancestors
  with controlled errors before reading payload bytes.
- Provider-neutral core and routed instructions distinguish kickoff, routine work,
  handoff, independent review and explicit resource rotation.
- The Python helper previews, creates and checks a managed instruction bundle while
  preserving project-owned workspaces and refusing conflicting files.
- Optional documentation templates and twelve capability cards support selective
  adoption without installing packages or granting live-operation authority.

### 2026-10-27

- In a card or the index, the capability oracle rejects any `<scheme:...>` autolink, an
  inline link or image to any scheme even when its text is empty, and a one-line reference
  definition whose destination starts with a scheme of 2 to 32 characters. A local link
  with a quoted title resolves like one without.
- The handoff route asks for a handoff receipt with its Sender fields when the task
  artifact does not already carry that state.
- Every acceptance oracle reports a path through a symlink loop as a `FAIL` line on every
  supported Python version. Fixture preparation records each node's type, permission bits
  and content, so a preview that creates or removes a directory, a link or a pipe, or
  changes a mode, counts as a mutation, and it fails on anything it cannot read. The
  diagram check fails, naming the directory, when it cannot list one, and reports an error
  for a Markdown path that is a pipe, device or other special file, or a root that loops.
- The kickoff oracle fails when it cannot list or inspect anything in a package, or finds
  an entry that is neither a file nor a directory, instead of passing without it.
- The plan template and the documentation example let only lower-risk work merge the
  architecture and delivery research owners, as BOOTSTRAP and the kickoff oracle require.
- An upgrade of a manually reconciled target keeps the target's own loaders, replaces by
  hand the core and routes it copied, and removes copied routes the release no longer
  ships; `check` is not evidence there, because no manifest exists.

### 2026-10-26

- The capability oracle rejects, anywhere in a card or the index, a `scheme://` address, a
  scheme-relative `//host` link other than a single-label host with no path or port, a
  bare `www.` address, an email address, a mail, `tel:`, `javascript:` or `data:` link, and
  an inline link to any scheme; `docs/acceptance.md` lists the exact forms.
- BOOTSTRAP's role-decision, capability-card and project-standard rules sit directly under
  section 4, and "Existing agent instructions" covers only a target that already has
  `AGENTS.md` or `CLAUDE.md`. An upgrade reinstall first moves any project-owned loader
  content into a target-owned file. When the outgoing holder is absent, rotation
  continues from section 2, the independent replacement preflight.
- Minimum Python 3.11. CI tests Python 3.11 and 3.15 on Ubuntu and macOS, and runs the
  style check on 3.15.
- Every acceptance oracle reports a missing, unreadable or over-long path, or an
  undecodable file, as a `FAIL` line with its reason on every supported Python version,
  instead of a traceback. The release verifier fails on anything below an include that
  it cannot list or inspect, excluded or not, and the capability oracle on anything it
  scans, instead of passing without it.
- The kickoff oracle rejects an unknown `evidence_mode`, and its prompt tells a live run
  to cite only primary or official sources and to omit the fixture's synthetic mode,
  which proves schema only.

### 2026-10-25

- The five routes live in `routes/` beside `WARMBOOT.md`, and the core links each one
  relatively, so the same links resolve in this checkout and under `.agent-warmboot/`
  in an installed target. The installed layout is the same nine files; existing
  installations keep passing `check` and are not upgraded.
- The capability library has twelve decision cards. The two optional check scripts and
  their launcher were removed because they wrap a command the target already owns. The
  checkout loaders route an explicitly assigned capability audit to its route, and the
  outsider gate defines a material finding as a verifier-confirmed defect and allows one
  bounded replacement run. The outsider route and its prompt apply that rule to the
  verdict: `FINDING` claims a defect with `file:line` and a failure scenario, and design
  opinions are observations that do not change the verdict.
- The capability oracle reports array or object values where it expects a string as a
  `FAIL` line instead of a traceback.
- Every acceptance oracle reports JSON nested deeper than the decoder allows, or an
  integer longer than the interpreter's digit limit, as its own verification error
  instead of a traceback.

### 2026-10-24

- MIT licence for code, documentation, templates and examples; the installed core
  carries the full notice. The Unicode-derived range tables keep their notice in
  `NOTICE`.
- Rendered Mermaid diagrams with collapsed source, regenerated and checked by
  `tools/render_mermaid_docs.py` (`--check` verifies each wrapper's source digest, image
  and laptop readability).
- CI on Ubuntu and macOS with Python 3.10 and 3.13.
- `check` rejects a manifest with `NaN`, `Infinity`, `-Infinity` or nesting deep enough
  to exhaust the parser as invalid JSON, and no longer opens manifest entries outside
  the managed set.
- Both editions install the same edition-neutral loader text. Targets installed with
  the earlier Warmboot Full loader text fail `check` with `incompatible managed loader`
  until an accepted upgrade plan reinstalls the whole managed set (loaders, core, routes
  and manifest) from the new release, for example by removing the earlier managed files
  under that plan's authority and running `init <target> --apply`. Replacing only the
  loaders leaves the earlier manifest digests, so `check` still fails.

### 2026-10-18

- Every human-authored code file gives immediate language-native orientation, and
  consequential choices keep their local why, invariants, units and failure semantics.
  A distinct non-author reads the complete changed source set; tests, unlinked ADRs and
  agent memory do not substitute. Coded projects keep a mergeable human-operability
  floor.
- Projects record target-owned maintainability, testing, documentation and architecture
  decisions. Locally calibrated size or complexity pressure is a review trigger, never a
  universal cap or quality proxy.
- Topology follows consequence: every code change gets at least one independent
  non-author reviewer, a recorded single-agent exception covers only tiny low-risk work
  that changes no code, and extra lanes are added only where independence adds value.
  Scope changes revise one task and preserve unaffected receipts.
- Review converges on the target-native `CLEAN` threshold: a separate writer fixes
  findings, affected evidence reruns, and a non-author rereviews the unchanged corrected
  bytes until no actionable finding remains or the review is `BLOCKED`.
- The coordinator verifies each finding before acting on it and gives reviewers a
  digest-bound target with its governing contract. One required round of a substantial
  code review uses a different model family where one is reachable.
- A behavior finding names its trigger, and a claim no user or caller can reach is
  refuted. A fix removes the cause at its owner; when a second fix of the same kind
  fails, a different writer redoes it from the state before those fixes. The task seed
  records one review-record line per round.
- Every bounded lane, reviewers included, reports its proved results and unfinished
  items before its limit; a lane that stops without a report is recovered as a dead
  lane.
- Release candidates finalize authored bytes before holder-owned revision, notes and
  manifest bytes, create an exact local candidate before clean proof, and reconcile
  release notes with the selected paths.
- `MAINTAINING.md` states which proof tiers are deterministic and which are live; an
  unavailable tier stays `UNPROVED`. Identical thin `AGENTS.md` and `CLAUDE.md` loaders
  route maintainers through `MAINTAINING.md` to the single active backlog.
- `bin/warmboot check` rejects a duplicate-key `manifest.json`, and installed manifest
  paths containing NUL or names the host cannot encode fail through controlled
  validation.
- Acceptance checks reject duplicate-key and non-canonical typed evidence, Unicode
  ignorable, compatibility and punctuation aliases, and unsafe control or unassigned
  characters. Markdown evidence accepts LF, CRLF and CR line endings while shell
  templates stay LF-only. Kickoff separation checks reject confusable identity aliases.
- Upgrade checks bind identities, native-owner records and distinct old and new
  annotated tags. Source-comprehension checks validate exact Java declarations,
  pre-lex escapes, rationale and ADR anchors. Acceptance preparation refuses workspaces
  that overlap the repository, including through a scratch-directory alias.

### 2026-08-09

- An opt-in engineering capability library adds thirteen decision cards and two inert
  target-native test-wrapper templates. It stays outside the default installed payload,
  grants no live authority, and has deterministic isolation, privacy and refusal checks.
- Capability checks shell-quote wrapper values and run one canonical absolute path
  through positional isolation. They reject duplicate JSON keys, symlinked parents and
  outside paths, require one canonical `Source IDs` list per card, and check inherited
  rights.
- The repository improves itself through a context-clean maintenance prompt, maintainer
  role and system routing, and a planning-only self-improvement acceptance oracle.
- Consumer releases use one annotated tag and its resolved commit, a compact manifest
  with one canonical include/exclude policy and payload aggregate, a separate post-commit
  tag and commit receipt, and clean reproduction.
- Existing-consumer upgrade planning produces one compact agent-owned `UPGRADE.md` with
  safety receipts, applicable disposition rows, migration guards and fail-closed cases.
- Closing evidence follows the changed boundary: ordinary changes use focused native
  proof, while release, architecture, instruction, bootstrap, provider and
  acceptance-routing changes earn the full deterministic and cold close.
- Bounded workers and reviewers may inspect local Git history through a pre-attested,
  optional-lock-disabled allowlist. One coordinator keeps every mutation, remote and
  credential action, and every `git diff` form stays excluded.
- Every fresh project leaves one usable target-owned VS Code workspace or an explicitly
  accepted replacement. The helper never owns workspace bytes and says its success is
  not bootstrap completion.
- Kickoff keeps all six attributed research concerns, at least two distinct
  non-coordinator research owners and a distinct challenger, without fixed staffing.
- Routine handoffs carry by-reference state and evidence only; rotation is reserved for
  an explicitly named replacement of an active Git or scarce-resource holder.
- The always-loaded core stays within an 800-word operating budget with one home per
  fact, and ordinary bootstrap routes maintainer history, examples and acceptance
  machinery only to bounded needs.
- Cold acceptance runs in Python no-bytecode mode, keeps prior results out of audit
  instructions, and separates ordinary card selection from the all-thirteen audit.

These entries describe behavior, not live-agent, release, hosted or platform-parity
proof; current results come from rerunning the
[command inventory](docs/acceptance.md#deterministic-command-inventory).
