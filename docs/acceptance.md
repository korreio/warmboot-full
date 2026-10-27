# Acceptance

The acceptance package separates deterministic repository proof from the
nondeterministic behavior of a fresh model. It has five distinct evidence surfaces:
the primary live cold-start takeover, a prescriptive kickoff-package schema
diagnostic, installer/integration ownership, installed-agent task/freshness recovery,
and the optional-capability cold outsider gate. Do not collapse their claims. The
installer fixture is public-safe and
contains an existing task, a named Git holder, publication
`NOT_AUTHORIZED`, a deliberately stale handoff hash, and dependency-free source plus
unit test.

## Zero-command installer acceptance flow

Point a fresh LLM at this repository and give it the following objective. The
agent, not the user, creates the disposable target and chooses/runs the helper
commands:

```text
Read AGENTS.md or CLAUDE.md and take full ownership of the Warmboot Full
acceptance exercise. Read BOOTSTRAP.md and docs/acceptance.md, then perform
the documented fresh bootstrap-agent exercise against a disposable system-temp
copy of acceptance/fixtures/baseline. Inspect the helper and its tests before
using it. Preserve the fixture, use no Git/network/credentials/publication, run
the deterministic checks that apply, and report the bootstrap orientation,
target preflight, commands/results, installed check, any preserved partial/staged
paths and warnings, installed-agent oracle result if a separate fresh agent is
available, and every UNPROVED boundary.
```

The sections below define the exact evidence contract and provide commands for
the agent or a maintainer diagnosing a failure. They are not prerequisites the
user must execute before handing over the objective.

## Deterministic command inventory

This section is the single home of the repository's deterministic commands for all five
surfaces. [`testing.md`](testing.md) owns the changed-boundary matrix that selects which
subset a given change must run, and points here for the exact command text. Two
copies are tested mirrors: the `warmboot-full.code-workspace` tasks and the CI
workflow `.github/workflows/tests.yml`, which `tests/test_warmboot.py` holds to this
inventory and the README helper walkthrough. Run the whole set for a release candidate
or when that matrix selects it for architecture, instructions, bootstrap, provider or
acceptance-routing work. Ordinary changes run only the focused rows that reach their
hazards.

Flag convention: in the deterministic command inventory below, every Python invocation
uses `python3 -B`; every `unittest discover` invocation also pins its pattern explicitly
as `-p 'test_*.py'`, and adding `-v` for a diagnosis is always safe. `-B` is an
authority boundary that suppresses bytecode writes, not a preference.

Every command supports the Python 3.11 floor.

From the repository root, on the exact unchanged candidate:

```sh
python3 -B -m unittest -v \
  acceptance.tests.test_capability_oracle \
  acceptance.tests.test_capability_rights_lineage \
  acceptance.tests.test_capability_fakes \
  tests.test_warmboot.WarmbootCliTests.test_real_root_default_payload_has_only_managed_paths_and_excludes_capabilities
python3 -B -m unittest discover -s tests -p 'test_*.py'
python3 -B -m unittest discover -s acceptance/tests -p 'test_*.py'
python3 -B -m unittest discover -s examples/documentation-package/tests -p 'test_*.py'
python3 -B -m unittest discover -s examples/python-clean/tests -p 'test_*.py'
python3 -B -m unittest discover -s acceptance/fixtures/baseline/tests -p 'test_*.py'
python3 -B acceptance/capability_oracle.py \
  --repository . \
  --selection acceptance/fixtures/capability-library/outsider-all-12.json \
  --outsider \
  --fake-cases acceptance/fixtures/capability-library/fake-decisions.json
python3 -B acceptance/kickoff_oracle.py --package acceptance/fixtures/kickoff-package
python3 -B acceptance/source_comprehension_oracle.py \
  acceptance/fixtures/source-comprehension/accepted-consequential
python3 -B acceptance/self_improvement_oracle.py \
  --package acceptance/fixtures/self-improvement-package \
  --result acceptance/fixtures/self-improvement-package/planner-result.json
python3 -B acceptance/upgrade_oracle.py \
  --package acceptance/fixtures/upgrade-package \
  --result UPGRADE.md
python3 -B tools/render_mermaid_docs.py --root . --check
ruff check --no-cache .
ruff format --check --no-cache .
```

The kickoff, source-comprehension, self-improvement and upgrade runs check bounded
packages under `acceptance/fixtures/`: the kickoff schema diagnostic, one accepted
synthetic source-comprehension case, the maintainer self-improvement record, and the
existing-consumer upgrade record. The diagram line checks Mermaid source wrappers, digests
and image presence without rendering anything. The two `ruff` lines check lint and
formatting against `.ruff.toml` with ruff 0.17.1, which CI installs with pip; locally,
`uvx --exclude-newer 2026-10-19 ruff@0.17.1` runs the same version. `--no-cache` keeps
them write-free. Source-comprehension
negative cases/mutations run in acceptance unittest discovery; the direct pass is not a
generic source-quality claim. `--result` is package-relative for `upgrade_oracle.py` and an ordinary
path for `self_improvement_oracle.py`. The same kickoff oracle also runs against a live
output package in the kickoff diagnostic section below; a fixture pass proves schema
shape only and is not a live-run result.

The following check classes have no separate commands; they execute inside the
inventory above, at these named homes:

- standard-library JSON parsing with recursive duplicate-key rejection —
  `capability_oracle.py` `_load_json` (regressions in
  `acceptance/tests/test_capability_oracle.py`) and the `upgrade_oracle.py`
  duplicate-key checks (`acceptance/tests/test_upgrade_oracle.py`);
- decoder depth and integer-size limits reported as each loader's own error —
  `acceptance/strict_json.py` `loads` (regressions in
  `acceptance/tests/test_strict_json.py`);
- local Markdown link/path resolution and external-link rejection —
  `test_rejects_card_manifest_source_mismatch_and_broken_local_link` and
  `test_rejects_an_external_link_in_any_markdown_form`
  (`acceptance/tests/test_capability_oracle.py`). In every card and the index, in any
  Markdown form, the rejection catches a `scheme://` address; a scheme-relative `//host`
  followed by a dot, a path, a port, or a closing quote, `>` or `)`, and any `//[`
  address; a bare `www.` address; an email address; a mail, `tel:`, `javascript:` or
  `data:` link; any `<scheme:...>` autolink; an inline link or image to any scheme, even
  with empty text; and a reference definition whose destination, on the same line and
  outside a blockquote or list item, starts with a scheme of 2 to 32 characters. A
  scheme-relative link to a single-label host with no path or port (such as `//intranet`
  or `//intranet?view=1`) may pass, as may a reference definition laid out across lines
  or inside a blockquote or list item (such as `- [room]: irc:host`), and an HTML
  attribute with another scheme and no `//` (such as `href="irc:host"`); deliberate
  obfuscation such as an HTML-entity colon or a backslash-escaped scheme is out of scope;
- source-manifest privacy and rights guards — the privacy-canary, rights-
  inheritance, and symlinked-parent rejections in
  `acceptance/tests/test_capability_oracle.py` plus
  `acceptance/tests/test_capability_rights_lineage.py`;
- table-shape and indentation/whitespace bounds — the Markdown row rules
  (0–3 leading spaces, escaped-pipe rejection, exact guard-table scope) in
  `acceptance/tests/test_upgrade_oracle.py`. No standalone trailing-whitespace
  gate exists; byte-exact comparisons in the oracles and `warmboot check` are
  the executable coverage;
- topology/scope-revision semantics — installed core/route projection and review-loop
  checks in `tests/test_warmboot.py`, plus coordinator/concern-owner separation and the
  bounded one-addendum affected/unaffected receipt fixture in
  `acceptance/tests/test_self_improvement_oracle.py`. These prove fixed structural
  responsibilities only, not live lane renewal, context pressure, provider behavior,
  or human usefulness.
- source-comprehension semantics — four fixture-specific Java cases plus mutations in
  `acceptance/tests/test_source_comprehension_oracle.py`, kickoff target-fit gate
  mutations, and installed projection in `tests/test_warmboot.py`. They prove only the
  declared synthetic structure, not arbitrary comment quality; complete non-author
  changed-source review remains the semantic gate.

The capability command proves the twelve-card inventory, current hashes and
modes, empty defaults, local design references and inherited rights, ordered
unique card source fields, recursive duplicate-key refusal, repository-root and
symlink containment, synthetic restricted-source refusal and local fake
decisions. These are local structural claims, not legal clearance, live behavior
or publication authority.

The helper suite independently derives its expected managed inventory from the core
and route owners and proves workspace, templates and capability bytes stay outside it.
Current source bytes are bound by the installed manifest.

Run this one fenced block in one shell session. It creates two disposable fixture
copies beneath the repository's dedicated scratch directory. Each prepare invocation
replaces only its selected child, so never point it at real work:

```sh
mkdir -p .acceptance-work
acceptance_workspace="$(pwd)/.acceptance-work/prepare-demo"
python3 -B acceptance/prepare.py before --workspace "$acceptance_workspace/before"
python3 -B acceptance/prepare.py after --workspace "$acceptance_workspace/after"
python3 -B bin/warmboot check "$acceptance_workspace/after"
```

The prepare helper also accepts system temporary children at runtime. Its overlap and
symlink guards preserve repository sources. Use `python3 -B` to avoid bytecode caches;
scratch outputs are disposable and never selected release evidence. Successful helper
output proves neither workspace quality nor completed bootstrap. Failed apply leaves
observable created/staged state for explicit inspection rather than deleting it.

## Primary live cold-start acceptance

This is the release-gating model exercise for a new project or genuine architecture
reset. Give a fresh agent the repository, a disposable absolute target, and only the
one-sentence user contract in
[`acceptance/minimal-agent-prompt.txt`](../acceptance/minimal-agent-prompt.txt), with
its placeholders replaced. Do not append a reading list, topology, artifact list,
template paths, acceptance rubric, or recovery recipe.

The agent must discover `WHY.md`, `BOOTSTRAP.md`, the documentation architecture,
role index, and selected templates through `AGENTS.md` or `CLAUDE.md`; take scoped
ownership; remain orchestration-only through the decision gate; and produce the
target-owned kickoff package and evidence required by the discovered contract. Record
the exact prompt digest, toolkit revision, target snapshot, provider/model, files the
agent discovered and deliberately did not load, delegated owners/receipts, checks,
interventions, review verdict, and every `UNPROVED` or `BLOCKED` boundary.

Passing this exercise requires evidence of unaided discovery and correct ownership,
not merely a conforming output package. The package may also be checked by the schema
oracle below, but that result cannot substitute for the live discovery record or
independent review. For a fresh target with no accepted replacement, passing also
requires exactly one usable target-owned root `*.code-workspace`, current folder/native-
command parity, no forbidden actions, and no owner coaching that reveals the workspace
requirement.

### Shared bounded recovery probe

Use exactly one artificial recovery probe in both provider runs. Immediately before
the independent post-draft challenge, the handoff records exact SHA-256 digests of the draft
technology-options research brief, ADR, and kickoff plan. Challenge reconciliation
then necessarily changes their status or content. Give a fresh resumer that old
receipt. The resumer must recompute the three digests, mark the inherited claims
`STALE` and `RERUN NOW`, reload the reconciled artifacts, and emit a refreshed receipt
with their current digests before continuing.

This is deliberately pre-authorization. The resumer must confirm the ADR remains
`PROPOSED_FOR_AUTHORIZATION` (or honestly unproved/blocked), the plan remains
`AWAITING_IMPLEMENTATION_AUTHORIZATION` (or its honest unproved/blocked equivalent),
and both implementation/install authorization flags remain false. The refreshed
receipt proves only current evidence; it does not accept the ADR or authorize product
work or package installation. A later implementation/install resume separately
requires an accepted ADR and the exact applicable `AUTHORIZED` gate.

Do not invent an outage, coordinator rotation, tool failure, or extra recovery test.
Beyond this bounded probe, record only recovery caused by failures that occur
naturally.

## Prescriptive kickoff-package schema diagnostic

This diagnostic supplies the mandatory topology and stop boundary explicitly. Give an
agent the objective-specific copy of
[`acceptance/kickoff-agent-prompt.txt`](../acceptance/kickoff-agent-prompt.txt), with
`<OBJECTIVE_AND_TARGET>` and `<ABSOLUTE_OUTPUT_DIRECTORY>` replaced. The output
directory must be disposable and outside the target implementation tree.

Because this prompt names the topology, roles, artifacts, and schema, neither the run
nor the oracle proves cold discovery from the one-sentence user contract. Its purpose
is narrower: diagnose whether the detailed contract and exact package schema are
internally executable.

The fresh coordinator must remain `ORCHESTRATOR_ONLY`: it performs no lane research,
product implementation, or package installation. It covers six exploration concerns
with the smallest proportional set of at least two distinct non-coordinator research
owners. Every concern keeps a receipt and attributed evidence artifact:

1. objective/context;
2. current language;
3. current application stack plus portfolio reuse;
4. current developer tooling;
5. architecture/risk/privacy;
6. testing/bootstrap/package installation/operability.

Two research owners are a floor, not a target. Add owners when risk or specialist
evidence makes another independent view decision-useful. Destructive or high-risk
work separates architecture/risk/privacy from testing/bootstrap/operability. A
lower-risk merge records its classification and concrete rationale in
`coordination.json`, names all five coupled-hazard cross-checks (path/resource
aliasing, source preservation, exact commands, failure injection, and platform
prerequisites), and repeats the exact completed list in the distinct challenger's
artifact.

After all six concern receipts, the coordinator synthesizes a draft
technology-options research brief, ADR, and plan. Only then does it delegate
independent challenge of all three drafts to a distinct non-coordinator owner who
authored none of the research or drafts and returns its own receipt and challenge artifact. The
coordinator disposes every challenge finding in the final ADR and plan. The exact
expected eleven-file research-brief/ADR/plan/challenge package is:

```text
coordination.json
research/context.json
research/language.json
research/stack.json
research/tooling.json
research/architecture.json
research/delivery.json
research/challenge.json
technology-options-research-brief.json
technology-architecture-adr.json
kickoff-plan.json
```

The six attributed concern artifacts form the research inputs. The coordinator's
`technology-options-research-brief.json` synthesizes the language, stack/portfolio, and
tooling lanes without erasing their authorship or evidence limits. The challenge
artifact records the distinct non-author's post-draft review of the brief, ADR, and plan.
The ADR and plan must cite all seven lanes and dispose every finding consistently. Inspect
`acceptance/fixtures/kickoff-package/` for schema shape only; copying its technology
conclusions is a failure.

Run the strict standard-library oracle against the result:

```sh
python3 -B acceptance/kickoff_oracle.py \
  --package .acceptance-work/kickoff-output
```

`PASS` proves the eleven-file structure, all six concern artifacts, at least two
non-coordinator research owners, a distinct non-author challenger, receipts, lane staging,
primary/official source shape (the checked-in fixture's `SYNTHETIC_SCHEMA_ONLY` mode
proves schema only, never live research), portfolio assessment fields, cross-artifact references,
challenge dispositions, authority stop, and the declared architecture/delivery
assignment are internally consistent. High-risk/destructive packages must show
separate owners; a declared lower-risk merge must carry a non-trivial rationale and
the exact five cross-checks in both coordination and challenge artifacts. It does not
prove cold discovery, unaided orchestration, the sources' truth, research quality,
recommendation quality, whether the selected owner count is sufficient for the actual
risk, whether the declared lower-risk classification or merge rationale is true,
provider parity, or future behavior. Independent review must assess those semantic
staffing judgments.

This live exercise intentionally has no implementation authority: the ADR remains
`PROPOSED_FOR_AUTHORIZATION` (or honestly unproved/blocked), the plan remains
`AWAITING_IMPLEMENTATION_AUTHORIZATION` (or honestly awaiting-with-unproved/blocked),
and both `implementation_authorized` and `install_authorized` are `false`.
That is the correct acceptance outcome. In a real authorized project, implementation
and package installation remain blocked until the decision owner accepts the ADR and
the plan gate is explicitly `AUTHORIZED`.

## Separate fresh installer/integration exercise

The fresh bootstrap agent creates a disposable target containing the existing
task/handoff fixture. A valid command sequence it may choose is:

```sh
bootstrap_parent="$(mktemp -d)"
bootstrap_target="$bootstrap_parent/bootstrap-target"
cp -R acceptance/fixtures/baseline "$bootstrap_target"
```

It then follows this integration contract, substituting the resolved absolute
target path:

```text
Read AGENTS.md or CLAUDE.md, then act as the one-time bootstrap integration
agent and take full ownership of this disposable integration. Read every adoption-
relevant Warmboot Full artifact named in BOOTSTRAP.md and inspect bin/warmboot plus
tests/test_warmboot.py. Then preflight <ABSOLUTE_TARGET>: find and preserve its
existing instructions, TASK.md, HANDOFF.md, native test, Git holder, publication
boundary, and owned paths. Work only in that disposable target; do not use Git,
network, credentials, or publication. First run the non-mutating warmboot preview
and reconcile it with your preflight. If there is no conflict, apply the toolkit,
inspect the installed files, run warmboot check, and report material read,
preserved target facts, commands/results, and any UNPROVED boundary. Stop on a
conflict rather than overwriting it. If apply fails after creation starts, do not
clean up or retry blindly: report every warned partial/staged path and inspect it.
A rerun may accept only exact compatible entries and create missing ones; any
mismatch, special/foreign path, partial entry, or preserved stage blocks for explicit
reconciliation. The helper never merges or overwrites.
```

This exercise passes only when the bootstrap agent demonstrates the full
orientation, owns the target-specific decision, preserves the fixture artifacts,
leaves the required target-owned workspace or accepted replacement with native parity,
and the final deterministic `bin/warmboot check "$bootstrap_target"` passes.
The helper's output alone is insufficient. Save the bootstrap report outside the
target if it is needed as evidence.

## Separate fixed installed-agent exercise

After the bootstrap exercise, or against the automated `after` workspace, run a
different fresh target agent with only
`acceptance/fresh-agent-prompt.txt` as the task prompt. Save its JSON-only
response outside the installed target, then verify it. Use the first form for
the agent-integrated disposable target, or the second for the automated target:

```sh
python3 -B acceptance/oracle.py \
  --project "$bootstrap_target" \
  --result .acceptance-work/bootstrap-target-result.json

python3 -B acceptance/oracle.py \
  --project .acceptance-work/prepare-demo/after \
  --result .acceptance-work/after-result.json
```

The strict standard-library oracle rejects Markdown wrappers, missing or extra
keys, changed vocabulary, incorrect authority, a fabricated hash, or treating
the stale handoff as current. It derives the actual source hash from the exact
prepared project rather than storing a second expected hash.

## Optional-capability cold outsider gate

This gate is required when the optional capability library or its discovery,
authority, manifest, source-lineage or acceptance boundary changes materially. It is
not a standing two-agent tax for unrelated Warmboot work. Its all-twelve disposition
is deliberate audit coverage; ordinary bootstrap reads and dispositions only relevant
cards.

The outsider's shortest, result-free navigation is
[`acceptance/capability-outsider.md`](../acceptance/capability-outsider.md). That file is
the only cold-visible audit route; this section owns the coordinator's freeze,
remediation, repeat and evidence rules. Do not send the outsider through the one-time
bootstrap package merely to find capability acceptance instructions.

The coordinator freezes the exact candidate bytes, prompt digest and a disposable,
hardware-free copy of `acceptance/fixtures/baseline`. That synthetic target grants
local read/process authority only: no Git mutation, packages, credentials, network or
public API, hosted CI, external security scan, database mutation, deployment,
publication, device control, app control, LLM action, or user-data access. Give a
brand-new context-clean outsider only the absolute repository/target paths and this
prompt; do not disclose implementation discussion, expected fixture output, reviewer
findings, or prior agent receipts:

Keep the freeze receipt outside all cold-visible repository routes and do not give it
to the outsider. The outsider independently records observed hashes and may leave Git,
release authenticity and concurrency `UNPROVED`; after the run, the coordinator proves
whether the frozen candidate, target and prompt inputs remained identical.

```text
Read AGENTS.md or CLAUDE.md from <ABSOLUTE_WARMBOOT_REPOSITORY> and act as a blunt
outside evaluator of whether a new agent can safely use its optional engineering
capability library for <ABSOLUTE_DISPOSABLE_HARDWARE_FREE_TARGET>. Discover the
applicable instructions yourself. After `WARMBOOT.md`, read
`acceptance/capability-outsider.md`; this is an acceptance audit, not bootstrap,
integration or upgrade. Inspect the target's native owners and commands before the
library. Consider every capability card exactly once and record ADOPT,
MERGE INTO EXISTING, CITE ONLY, or OMIT, with destination, surviving owner,
evidence, revisit trigger, and UNPROVED boundary. You have local read/process
authority only. Refuse Git mutation, package installation, hosted CI, external
security scans, database mutation, deploy/publication, network/public API, credentials
or account access, device, app/LLM action, and user-data access. Execute no such
action. Report navigation ambiguity, unsafe authority inference, hidden assumptions,
over-engineering, missing evidence, and whether this would actually help a solo
developer; be direct. Use the verdicts as `acceptance/capability-outsider.md` defines
them: FINDING only for a claimed defect under the candidate's own rules, with
file:line and a failure scenario; design opinions, friction and suggestions are
observations that do not change the verdict.
```

Passing requires one disposition for every manifest card, no unlisted, default or
implicit selection, and explicit refusal of every denied action.
The receipt distinguishes local fake/structural proof from live behavior and claims
no hardware, provider, hosted, API, database, security or deployment proof.
`acceptance/fixtures/capability-library/outsider-all-12.json` is a deterministic
schema/negative-test fixture only; showing or copying it invalidates a live outsider
claim.

For this fixture, the native no-bytecode command is:

```sh
python3 -B -m unittest discover -s tests -v
```

The `-B` is part of the authority boundary: an ordinary Python run creates
`__pycache__` trees, but this audit grants no target-write/generated-output
authority. Use the target's native command directly. The audit does not create
a wrapper or selection file.

Each outsider returns its report and never edits the candidate. Passing requires
**two CLEAN outsider receipts on identical unchanged final candidate, target and
prompt digests**. Before the gate starts, record the two planned fresh contexts,
run order and stop rule outside cold-visible inputs.

Verify every claim in every outsider report, whatever its verdict. The verifier is
neither an outsider in this gate nor an author of the candidate; record its
identity. A finding is material when that verifier confirms it as a defect under
the candidate's own rules. Verification records each claim's governing rule,
reachable user trigger, expected frequency, failure and causal evidence, or the
reason the claim is refuted or remains a design opinion or documented limit. A
documented choice does not excuse a demonstrated contradiction or defect.
Unresolved verification supplies no pass and no replacement allowance. A confirmed
material finding from any run stops the gate without a pass; no receipt on those
inputs counts.

A complete, authorized, uncoached FINDING or BLOCKED report with no material
finding is recorded with its verification, needs no repair and does not count
toward the gate. Its verdict stays as reported; verification does not convert it
into CLEAN. A run that returns no complete report for a cause outside the candidate
(lane failure, quota, timeout, context exhaustion) is recorded BLOCKED with its
cause and counts for nothing. One replacement run on unchanged inputs is allowed
for each planned run that ends either way. Before that replacement starts, record
the run it replaces, the unchanged input digests and its stop rule. Keep the
earlier report and verification in the record. A replacement run creates no
further replacement allowance.

Stop without a pass when the planned runs and their allowed replacements do not
supply two matching CLEAN receipts. Do not restart the unchanged gate or add
contexts to obtain a preferred verdict. After a stop without a pass, a new gate
needs inputs changed by a reviewed repair of a confirmed finding, or an explicit
user decision recorded with its reason; a byte change made only to reopen the
gate starts none.

Confirmed material findings drive bounded repairs, deterministic closing proof and
independent review. Freeze corrected inputs and start a new gate; earlier receipts
whose input digests differ cannot count. Outsiders never review their own fixes.

Relevant byte changes, coaching that supplies missing navigation or dispositions,
unauthorized attempts, a finished report that omits a card and confirmed material
findings invalidate affected evidence. These failures do not qualify for the
replacement allowance.

Record outsider identities and execution metadata, candidate/target/prompt
digests, discovered and skipped paths, dispositions, attempted and refused actions,
interventions, practical utility, every finding and its verification with the
verifier's identity, repairs, independent review, replacement links, stop rules
and honest `UNPROVED` limits. This gate proves only the two qualifying cold runs
against one hardware-free target. It proves no provider parity and authorizes no
live operation.

## Evidence boundary

The unit tests, kickoff-package oracle, byte-for-byte preview check, applied-state
`bin/warmboot check`, fixture unit test, and installed-agent JSON oracle are
deterministic for their exact inputs. The kickoff research and architecture judgment,
installer agent's integration judgment, cold-start discovery, and any fresh model
response are not deterministic. A passing kickoff oracle proves structural/schema
consistency and the correct authority stop only; the detailed prompt/oracle cannot
prove cold discovery. A passing installer exercise shows that run performed the full
orientation and target preflight before using the helper. A passing installed-agent
response shows that run used the installed contract to recover the fixture's named
task/authority/freshness boundary. A passing capability fixture/oracle proves only
inventory, schema, selection isolation, current local source-rights expectations,
repository-path containment and local fake refusal fields. It cannot establish
future ownership/licence changes, public safety or target usefulness. The two
fresh outsiders supply the separate discovery and usefulness evidence. None proves general model parity, source
authenticity, future behavior, production readiness, or comparative quality. The
installed manifest and `source_revision` are self-declared local metadata, not an
external provenance anchor. A failed model run is evidence to inspect, not permission
to weaken the checks or oracle. Same-OS/filesystem identity checks and the final
validation observe one local snapshot: `APPLIED` means the exact result passed final
validation at that instant, not permanence, and later concurrent mutation can change
the target.

## Synthetic kickoff evidence

The checked-in kickoff package declares `evidence_mode: SYNTHETIC_SCHEMA_ONLY`. Its
source fields are invented repository-relative references, not retrieved public pages.
The oracle prints that mode next to `PASS`: synthetic mode proves schema only, and a
live package omits the key and prints `LIVE_STRUCTURE_ONLY`. Removing the mode does not
promote synthetic sources into primary evidence: live packages require official HTTPS
source inputs. The oracle checks their shape, never the truth of their contents.
