"""Exercise Warmboot Full helper, projection, documentation, and safety contracts."""

from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from acceptance.unicode_policy import (
    NON_MARKDOWN_LINE_SEPARATORS,
    split_markdown_lines,
    split_markdown_table_cells,
)
from acceptance.upgrade_oracle import release_note_summary_classification

SOURCE_SCRIPT = Path(__file__).resolve().parents[1] / "bin" / "warmboot"
ROOT = SOURCE_SCRIPT.parent.parent


def load_cli_module():
    loader = importlib.machinery.SourceFileLoader("warmboot_cli_under_test", str(SOURCE_SCRIPT))
    specification = importlib.util.spec_from_loader(loader.name, loader)
    if specification is None:
        raise RuntimeError("could not load warmboot CLI for unit testing")
    module = importlib.util.module_from_spec(specification)
    loader.exec_module(module)
    return module


CLI_MODULE = load_cli_module()

CANONICAL_GIT_ALLOWLIST_HOME = "routes/context.md"
# The six commands the canonical home's allowlist block defines by extension. The
# contract test re-derives them from that block and pins the derivation against this
# tuple, which the discovery pass below then reuses.
CANONICAL_GIT_COMMANDS = (
    "git --no-pager blame",
    "git --no-pager log",
    "git --no-pager log --follow",
    "git --no-pager show --no-ext-diff",
    "git rev-parse --verify",
    "git status --short --untracked-files=all",
)
GIT_BACKTICK_PATTERN = re.compile(r"`(git\b[^`]*)`")
# Neither token can be read as an allowlisted command: every `git diff` form is named
# by these documents only to exclude it, and `git --no-optional-locks` is the
# lock-avoidance prefix an allowed invocation carries, not an invocation.
NON_COMMAND_GIT_TOKENS = frozenset({"git --no-optional-locks"})
GIT_DIFF_EXCLUSION_PATTERN = re.compile(
    r"(?:exclud\w*|forbid\w*|reject\w*|outside)\s+(?:every|all)\s+`git diff`\s+form"
    r"|(?:every|all)\s+(?:`git diff`\s+form|form\s+of\s+`git diff`)"
    r"[^.]{0,200}?(?:exclud|forbid|reject|outside|never)",
    re.IGNORECASE,
)
# Backticked ALL-CAPS status tokens; filenames carry a dot and never match.
STATUS_TOKEN_PATTERN = re.compile(r"`([A-Z][A-Z _/-]{2,})`")
# Two backticked git tokens belong to one command list when only list punctuation,
# bullet hyphens, whitespace, or "and"/"or" separate them. Any other word — "including",
# "are eligible;", "is excluded" — ends the list, which is what keeps every current
# `git diff` exclusion sentence out of the enumerations below.
GIT_ENUMERATION_JOINER = re.compile(r"^(?:[\s,;/-]|and|or)*$")


def git_commands_in(text: str) -> set[str]:
    """Every backticked git string in `text` that could be read as a command."""
    commands = set()
    for raw in GIT_BACKTICK_PATTERN.findall(text):
        command = " ".join(raw.split())
        if command.startswith("git diff") or command in NON_COMMAND_GIT_TOKENS:
            continue
        commands.add(command)
    return commands


def git_command_enumerations(text: str) -> list[list[str]]:
    """Maximal runs of two or more backticked git tokens joined as one command list.

    A run of adjacent backticked commands *is* an allowlist however the surrounding
    prose labels it. Nothing is filtered here — unlike `git_commands_in`, which must
    forgive `git diff` because every home names it in order to exclude it. That
    amnesty is why set equality alone cannot see a `git diff` form smuggled into a
    command list, so the raw runs are read separately.
    """
    flat = " ".join(text.split())
    tokens = list(GIT_BACKTICK_PATTERN.finditer(flat))
    runs: list[list[str]] = []
    current: list[re.Match[str]] = []
    for index, token in enumerate(tokens):
        if current and GIT_ENUMERATION_JOINER.match(flat[tokens[index - 1].end() : token.start()]):
            current.append(token)
            continue
        if len(current) > 1:
            runs.append([" ".join(match.group(1).split()) for match in current])
        current = [token]
    if len(current) > 1:
        runs.append([" ".join(match.group(1).split()) for match in current])
    return runs


# The checker suite is repository-owned text but is not a git-command-authority home:
# it may not be *discovered* as a git-command restatement home. It remains subject to
# the repository-wide `git diff` ban, so the diff-ban pass re-includes it — a git-diff
# enumeration smuggled into it must still be caught.
DISCOVERY_EXCLUDED_HOMES = frozenset(
    {
        "tests/test_warmboot.py",
    }
)


def repository_text_files(root: Path = ROOT, include_excluded_homes: bool = False) -> list[str]:
    """Repository-owned text files, newest state on disk, as POSIX relatives.

    By default the checker suite is omitted: it is not a git-command restatement home
    and must never be discovered as one. Pass
    `include_excluded_homes=True` for the repository-wide `git diff` ban, which must
    reach every repository-owned text file — the checker included — so a forbidden
    git-diff enumeration cannot hide in a discovery-excluded file. All retained
    authored source is eligible for the prohibition scan.
    """
    found = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if not path.is_file() or path.is_symlink():
            continue
        # Repository-relative parts: what is hidden inside the tree, never whatever
        # the absolute prefix of the checkout (or a temporary replay root) happens
        # to be called.
        if any(part.startswith(".") or part == "__pycache__" for part in relative.split("/")):
            continue
        # The checker is excluded from restatement-home DISCOVERY but not from the
        # git-diff ban (include_excluded_homes re-adds it).
        if relative in DISCOVERY_EXCLUDED_HOMES and not include_excluded_homes:
            continue
        try:
            path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        found.append(relative)
    return found


def scan_git_command_homes(
    root: Path = ROOT, canonical: tuple[str, ...] = CANONICAL_GIT_COMMANDS
) -> tuple[set[str], list[tuple[str, str]]]:
    """Discovered allowlist homes, plus `git diff` offenders over every owned file.

    Discovery is by content and uniform — any file restating two or more canonical
    commands is a restatement home and must be registered. It runs over the discovery
    set, which omits the checker suite (not a command-authority home). The second
    return value is the repository-wide ban: nowhere may a `git diff` form sit inside a
    command enumeration, so it is computed for *every* repository-owned text file,
    including the discovery-excluded checker — a `git diff` enumeration hidden there
    must still be caught. Offenders are
    returned as `(relative, command)` so a failure names the file.
    """
    canonical_set = set(canonical)
    discovered: set[str] = set()
    for relative in repository_text_files(root):
        text = (root / relative).read_text(encoding="utf-8")
        if len(git_commands_in(text) & canonical_set) >= 2:
            discovered.add(relative)
    diff_offenders: list[tuple[str, str]] = []
    for relative in repository_text_files(root, include_excluded_homes=True):
        text = (root / relative).read_text(encoding="utf-8")
        for enumeration in git_command_enumerations(text):
            diff_offenders.extend(
                (relative, command) for command in enumeration if command.startswith("git diff")
            )
    return discovered, diff_offenders


WORKFLOW_PATH = ROOT / ".github" / "workflows" / "tests.yml"
WORKFLOW_RUN_KEY = re.compile(r"^(?P<indent>\s*)(?:-\s+)?run:\s*(?P<value>.*)$")
# Workflow lines that check a README claim rather than restate a command. The file
# count pins README's statement that the installed bundle is nine files; the direct
# call runs `bin/warmboot` through its own `#!` entry point on the target that the
# README walkthrough has just checked through the interpreter.
WORKFLOW_ONLY_ASSERTIONS = frozenset(
    {
        'test "$(find "$readme_target" -type f | wc -l)" -eq 9',
        './bin/warmboot check "$readme_target"',
    }
)
# Workflow lines that provision the pinned style tool the inventory's `ruff` lines use.
WORKFLOW_TOOL_SETUP = frozenset({"python -m pip install --disable-pip-version-check ruff==0.17.1"})
# Inventory commands the workflow deliberately does not run, each with its reason.
WORKFLOW_INVENTORY_OMISSIONS = {
    "python3 -B -m unittest -v acceptance.tests.test_capability_oracle "
    "acceptance.tests.test_capability_rights_lineage acceptance.tests.test_capability_fakes "
    "tests.test_warmboot.WarmbootCliTests."
    "test_real_root_default_payload_has_only_managed_paths_and_excludes_capabilities": "The workflow's helper and acceptance suites already run every test it selects.",
}


def shell_logical_lines(block: str) -> list[str]:
    """Dedent a shell block and join backslash continuations into one line each."""
    logical: list[str] = []
    pending: list[str] = []
    for raw in textwrap.dedent(block).splitlines():
        text = raw.strip()
        if text.endswith("\\"):
            pending.append(text[:-1].rstrip())
            continue
        line = " ".join(part for part in (*pending, text) if part)
        pending = []
        if line:
            logical.append(line)
    if pending:
        logical.append(" ".join(pending))
    return logical


def fenced_shell_blocks(text: str) -> list[str]:
    """Bodies of the ```sh fences in `text`."""
    return re.findall(r"^```sh\n(.*?)^```", text, flags=re.MULTILINE | re.DOTALL)


def workflow_run_lines(workflow: str) -> list[str]:
    """Logical shell lines of every workflow `run` step.

    Only plain one-line values and `|` literal blocks are read; any other YAML scalar
    form fails loudly instead of being skipped.
    """
    lines = workflow.splitlines()
    commands: list[str] = []
    index = 0
    while index < len(lines):
        match = WORKFLOW_RUN_KEY.match(lines[index])
        index += 1
        if match is None:
            continue
        value = match.group("value").strip()
        if value == "|":
            indent = len(match.group("indent"))
            body: list[str] = []
            while index < len(lines) and (
                not lines[index].strip() or len(lines[index]) - len(lines[index].lstrip()) > indent
            ):
                body.append(lines[index])
                index += 1
            commands.extend(shell_logical_lines("\n".join(body)))
        elif value and value[0] not in "|>'\"&*!":
            commands.extend(shell_logical_lines(value))
        else:
            raise AssertionError(f"unsupported workflow run value: {value!r}")
    return commands


class WarmbootCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.toolkit = root / "toolkit"
        self.target = root / "target"
        (self.toolkit / "bin").mkdir(parents=True)
        (self.toolkit / "routes").mkdir(parents=True)
        self.target.mkdir()
        shutil.copy2(SOURCE_SCRIPT, self.toolkit / "bin" / "warmboot")
        (self.toolkit / "WARMBOOT.md").write_text("# Test core\n", encoding="utf-8")
        (self.toolkit / "SOURCE_REVISION").write_text("test-revision\n", encoding="utf-8")
        (self.toolkit / "routes" / "review.md").write_text("# Review route\n", encoding="utf-8")
        (self.toolkit / "routes" / "work.md").write_text("# Work route\n", encoding="utf-8")
        self.script = self.toolkit / "bin" / "warmboot"

    def run_cli(self, *arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(self.script), *arguments],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )

    def apply(self) -> subprocess.CompletedProcess[str]:
        return self.run_cli("init", str(self.target), "--apply")

    def assert_workspace_commands_have_single_authority(
        self, workspace: dict, testing: str, acceptance: str
    ) -> None:
        self.assertIn("[`acceptance.md`](acceptance.md)", testing)
        self.assertIn("## Deterministic command inventory", acceptance)
        inventory = acceptance.split("## Deterministic command inventory", 1)[1].split("\n## ", 1)[
            0
        ]
        for task in workspace["tasks"]["tasks"]:
            command = task["command"]
            # Editor tasks use the inventory's no-bytecode form verbatim.
            self.assertTrue(command.startswith("python3 -B "), command)
            self.assertIn(command, inventory, command)
            self.assertNotIn(command, testing, command)

    def assert_workflow_is_pinned_and_read_only(self, workflow: str) -> None:
        """Actions pin full commit SHAs, checkout keeps no credentials, the token is read-only."""
        self.assertIn("\npermissions:\n  contents: read\n", workflow)
        self.assertEqual(workflow.count("permissions:"), 1)
        lines = workflow.splitlines()
        actions = 0
        for index, line in enumerate(lines):
            step = re.match(r"(\s*(?:- )?)uses: (\S+)", line)
            if step is None:
                continue
            actions += 1
            self.assertRegex(step.group(2), r"^[\w.-]+/[\w.-]+@[0-9a-f]{40}$")
            if step.group(2).startswith("actions/checkout@"):
                # The step's keys start in the `uses` column; a shallower line ends it.
                column = len(step.group(1))
                body = []
                for following in lines[index + 1 :]:
                    if following.strip() and len(following) - len(following.lstrip()) < column:
                        break
                    body.append(following.strip())
                self.assertIn("persist-credentials: false", body)
        self.assertGreater(actions, 0)

    def assert_workflow_commands_have_single_authority(
        self, workflow: str, acceptance: str, readme: str
    ) -> None:
        """CI restates only inventory or walkthrough commands and runs the whole inventory.

        Every command in the inventory's first block must run in the workflow unless
        `WORKFLOW_INVENTORY_OMISSIONS` names it with a reason.
        """
        self.assertIn("## Deterministic command inventory", acceptance)
        inventory = acceptance.split("## Deterministic command inventory", 1)[1].split("\n## ", 1)[
            0
        ]
        walkthrough_heading = "\n## Try it\n"
        self.assertIn(walkthrough_heading, readme)
        walkthrough = readme.split(walkthrough_heading, 1)[1].split("\n## ", 1)[0]
        homes: set[str] = set()
        for block in fenced_shell_blocks(inventory) + fenced_shell_blocks(walkthrough):
            homes.update(shell_logical_lines(block))
        run_lines = workflow_run_lines(workflow)
        self.assertTrue(run_lines)
        for line in run_lines:
            if line in WORKFLOW_ONLY_ASSERTIONS or line in WORKFLOW_TOOL_SETUP:
                continue
            self.assertIn(line, homes, line)

        required = shell_logical_lines(fenced_shell_blocks(inventory)[0])
        for omitted in WORKFLOW_INVENTORY_OMISSIONS:
            self.assertIn(omitted, required, "stale workflow omission")
        missing = [
            line
            for line in required
            if line not in WORKFLOW_INVENTORY_OMISSIONS and line not in run_lines
        ]
        self.assertEqual(missing, [], "inventory commands missing from the workflow")

    def assert_exact_compatibility_legend_entries(self, identity: str) -> None:
        for token in (".agent-warmboot/manifest.json", "AGENTS.md", "CLAUDE.md", "bin/warmboot"):
            self.assertIn(token, identity)

    def assert_active_backlog_contract(self, plan: str) -> None:
        self.assertIn("SOLE CURRENT BACKLOG", plan)
        self.assertNotIn("https" + "://", plan)

    @staticmethod
    def normalized_markdown(text: str) -> str:
        """Compare bounded prose without Markdown emphasis, whitespace, or case noise."""
        return " ".join(re.sub(r"[*_`]", "", text).split()).casefold()

    def assert_release_evidence_workspace_contract(
        self, acceptance: str, release: str, testing: str
    ) -> None:
        """Runnable inventory and release ordering carry the evidence contract."""
        self.assertIn("## Deterministic command inventory", acceptance)
        self.assertIn("python3 -B acceptance/prepare.py", acceptance)
        self.assertIn("python3 -B bin/warmboot check", acceptance)
        self.assertIn(".acceptance-work/", acceptance)
        self.assertIn("independently frozen", release)
        self.assertIn("unchanged", release)
        self.assertIn("UNPROVED", testing)

    def test_real_root_default_payload_has_only_managed_paths_and_excludes_capabilities(
        self,
    ) -> None:
        target = ROOT / ".acceptance-work" / "inventory-target"
        observed_payload = CLI_MODULE.expected_install(ROOT, target)
        observed_files = [
            {"path": path, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            for path, data in observed_payload.items()
        ]
        expected_paths = {
            "AGENTS.md",
            "CLAUDE.md",
            ".agent-warmboot/core.md",
            ".agent-warmboot/manifest.json",
        }
        expected_paths.update(
            ".agent-warmboot/routes/" + path.name for path in (ROOT / "routes").glob("*.md")
        )
        self.assertEqual(set(observed_payload), expected_paths)
        self.assertFalse(any(item["path"].endswith(".code-workspace") for item in observed_files))

        managed_manifest = json.loads(observed_payload[".agent-warmboot/manifest.json"])
        self.assertEqual(
            set(managed_manifest["files"]),
            set(observed_payload) - {".agent-warmboot/manifest.json"},
        )
        capability_manifest = json.loads(
            (ROOT / "templates" / "capabilities" / "MANIFEST.json").read_text(encoding="utf-8")
        )
        managed_text = b"\n".join(observed_payload.values())
        for entry in capability_manifest["files"]:
            capability_id = entry.get("module_id")
            if capability_id:
                self.assertNotIn(capability_id.encode("utf-8"), managed_text)
            capability_bytes = (ROOT / "templates" / "capabilities" / entry["path"]).read_bytes()
            self.assertNotIn(capability_bytes, managed_text)

    def test_repository_workspace_is_target_owned_and_matches_testing_authority(self) -> None:
        """Editor tasks are bound to the one command home routed by testing policy."""
        workspace_path = ROOT / "warmboot-full.code-workspace"
        workspace = json.loads(workspace_path.read_text(encoding="utf-8"))
        seed = json.loads(
            (ROOT / "templates" / "project.code-workspace").read_text(encoding="utf-8")
        )
        testing = (ROOT / "docs" / "testing.md").read_text(encoding="utf-8")
        acceptance = (ROOT / "docs" / "acceptance.md").read_text(encoding="utf-8")
        self.assert_workspace_commands_have_single_authority(workspace, testing, acceptance)

        self.assertNotEqual(workspace, seed)
        self.assertNotIn("launch", workspace)
        self.assertEqual(len(workspace["folders"]), 1)
        folder = workspace["folders"][0]
        self.assertEqual(folder, {"name": "Warmboot Full", "path": "."})
        self.assertTrue((workspace_path.parent / folder["path"]).resolve().is_dir())

        tasks = workspace["tasks"]["tasks"]
        self.assertGreaterEqual(len(tasks), 1)
        for task in tasks:
            command = task["command"]
            self.assertEqual(task["options"]["cwd"], "${workspaceFolder}")
            self.assertFalse(
                any(
                    token in command.lower()
                    for token in (
                        " pip install",
                        "npm install",
                        "git ",
                        "curl ",
                        "deploy",
                        "publish",
                    )
                )
            )
        recommendations = workspace["extensions"]["recommendations"]
        self.assertTrue(recommendations)
        self.assertTrue(all(isinstance(item, str) and item for item in recommendations))

    def test_workspace_authority_rejects_testing_guide_command_copy(self) -> None:
        workspace = json.loads((ROOT / "warmboot-full.code-workspace").read_text(encoding="utf-8"))
        testing = (ROOT / "docs" / "testing.md").read_text(encoding="utf-8")
        acceptance = (ROOT / "docs" / "acceptance.md").read_text(encoding="utf-8")
        duplicated = testing + "\n" + workspace["tasks"]["tasks"][0]["command"] + "\n"
        with self.assertRaises(AssertionError):
            self.assert_workspace_commands_have_single_authority(workspace, duplicated, acceptance)

    def test_ci_workflow_restates_only_inventory_and_walkthrough_commands(self) -> None:
        self.assert_workflow_commands_have_single_authority(
            WORKFLOW_PATH.read_text(encoding="utf-8"),
            (ROOT / "docs" / "acceptance.md").read_text(encoding="utf-8"),
            (ROOT / "README.md").read_text(encoding="utf-8"),
        )

    def test_workflow_authority_rejects_drifted_commands(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        acceptance = (ROOT / "docs" / "acceptance.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        command = "python3 -B -m unittest discover -s acceptance/tests -p 'test_*.py'"
        continued = "--result UPGRADE.md"
        diagram_step = (
            "      - name: Diagram wrappers\n"
            "        run: python3 -B tools/render_mermaid_docs.py --root . --check\n"
        )
        for original in (command, continued, diagram_step):
            self.assertEqual(workflow.count(original), 1, original)
        for drifted in (
            workflow.replace(command, command.replace(" -B", "", 1)),
            workflow.replace(continued, "--result OTHER.md"),
            workflow.replace(diagram_step, ""),
        ):
            with self.assertRaises(AssertionError):
                self.assert_workflow_commands_have_single_authority(drifted, acceptance, readme)

    def test_workflow_pins_actions_and_keeps_no_credentials(self) -> None:
        self.assert_workflow_is_pinned_and_read_only(WORKFLOW_PATH.read_text(encoding="utf-8"))

    def test_workflow_pinning_rejects_tags_kept_credentials_and_write_tokens(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        checkout = re.search(r"actions/checkout@[0-9a-f]{40}", workflow)
        setup = re.search(r"- uses: (actions/setup-python@[0-9a-f]{40})", workflow)
        self.assertIsNotNone(checkout)
        self.assertIsNotNone(setup)
        for drifted in (
            workflow.replace(checkout.group(0), "actions/checkout@v7", 1),
            workflow.replace(
                setup.group(0), "- name: Python\n        uses: actions/setup-python@v7", 1
            ),
            workflow.replace("          persist-credentials: false\n", "", 1),
            workflow.replace("  contents: read\n", "  contents: write\n"),
            workflow.replace(
                "  style:\n", "  style:\n    permissions:\n      contents: write\n", 1
            ),
        ):
            with self.assertRaises(AssertionError):
                self.assert_workflow_is_pinned_and_read_only(drifted)

    def test_python_floor_is_stated_and_tested_as_3_11(self) -> None:
        readme, helper, acceptance = (
            self.normalized_markdown(path.read_text(encoding="utf-8"))
            for path in (ROOT / "README.md", SOURCE_SCRIPT, ROOT / "docs" / "acceptance.md")
        )
        self.assertIn("python 3.11 or newer", readme)
        self.assertIn("python 3.11+ standard library", helper)
        self.assertIn("every command supports the python 3.11 floor.", acceptance)
        self.assertIn('target-version = "py311"', (ROOT / ".ruff.toml").read_text(encoding="utf-8"))
        self.assertIn('python: ["3.11", "3.15"]', WORKFLOW_PATH.read_text(encoding="utf-8"))

    def test_identity_policy_rejects_removed_exact_compatibility_entries(self) -> None:
        identity = (ROOT / "docs/identity.md").read_text()
        self.assert_exact_compatibility_legend_entries(identity)
        with self.assertRaises(AssertionError):
            self.assert_exact_compatibility_legend_entries(
                identity.replace(".agent-warmboot/manifest.json", "")
            )

    def test_living_identity_is_separate_from_compatibility_and_history(self) -> None:
        identity = (ROOT / "docs/identity.md").read_text()
        self.assert_exact_compatibility_legend_entries(identity)
        self.assertIn("UNRELEASED-development", identity)
        self.assertEqual((ROOT / "SOURCE_REVISION").read_text(), "UNRELEASED-development\n")
        self.assertFalse((ROOT / "release-manifest.json").exists())
        self.assertIn('TOOLKIT_NAME = "agent-warmboot"', SOURCE_SCRIPT.read_text())
        schema = json.loads((ROOT / "docs/releases/release-manifest.schema.json").read_text())
        self.assertEqual(schema["x-schema-vocabulary"], "JSON Schema Draft 2020-12")
        self.assertNotIn("$id", schema)

    def test_candidate_release_note_summaries_are_not_bounded_state_only_shapes(self) -> None:
        fixture = ROOT / "acceptance/fixtures/upgrade-package/new-release-notes.json"
        notes = json.loads(fixture.read_text())
        for change in notes["changes"]:
            self.assertEqual(release_note_summary_classification(change["summary"]), "MATERIAL")

    def test_maintainer_loaders_are_equivalent_and_route_to_the_active_backlog(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertEqual(agents, claude)
        self.assertEqual(
            agents,
            "# Agent loader\n\n"
            "Read `WARMBOOT.md` first. It is the single provider-neutral core; load only the route\n"
            "it selects. For an explicitly assigned optional-capability acceptance audit, continue\n"
            "to `acceptance/capability-outsider.md`. For Warmboot Full maintenance, follow that\n"
            "route to `MAINTAINING.md`; the active backlog is `docs/plans/warmboot-build-plan.md`.\n"
            "This file adds no policy.\n",
        )

    def test_active_backlog_and_decisions_have_current_authority_routes(self) -> None:
        plan = (ROOT / "docs/plans/warmboot-build-plan.md").read_text()
        self.assert_active_backlog_contract(plan)
        role_index = (ROOT / "ROLE-INDEX.md").read_text()
        self.assertIn("docs/plans/warmboot-build-plan.md", role_index)
        self.assertIn("docs/decisions.md", role_index)

    def test_repository_owned_markdown_relative_links_resolve(self) -> None:
        """Resolve local links; repository-owned Markdown carries no outside URL at all."""
        link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
        outside_url_pattern = re.compile(r"\b(?:https?://|mailto:)\S*", re.IGNORECASE)
        checked = 0
        broken: list[tuple[str, str]] = []
        for path in sorted(ROOT.rglob("*.md")):
            relative = path.relative_to(ROOT).as_posix()
            if any(part.startswith(".") or part == "__pycache__" for part in relative.split("/")):
                continue
            text = path.read_text(encoding="utf-8")
            broken.extend(
                (relative, match.group(0)) for match in outside_url_pattern.finditer(text)
            )
            for raw_target in link_pattern.findall(text):
                target = raw_target.strip()
                if target.startswith(("http" + "://", "https" + "://", "mailto:")):
                    broken.append((relative, target))
                    continue
                if target.startswith("#"):  # pure in-page fragment
                    continue
                if "{{" in target:  # template placeholder, not a real path
                    continue
                if target.startswith("/"):
                    broken.append((relative, target))
                    continue
                path_part = target.split("#", 1)[0].split("?", 1)[0].strip()
                # Drop an optional Markdown link title: `(target "title")`.
                title_match = re.match(r"""^(\S+)\s+["'(].*$""", path_part)
                if title_match:
                    path_part = title_match.group(1)
                if not path_part:
                    continue
                checked += 1
                resolved = (path.parent / path_part).resolve()
                if not resolved.is_relative_to(ROOT) or not (
                    resolved.exists() or resolved.is_symlink()
                ):
                    broken.append((relative, target))
        self.assertEqual(
            broken, [], f"outside URL(s) or unresolved repo-relative Markdown link(s): {broken}"
        )
        self.assertGreater(checked, 0)

    def test_release_evidence_uses_external_no_bytecode_workspaces(self) -> None:
        self.assert_release_evidence_workspace_contract(
            (ROOT / "docs/acceptance.md").read_text(),
            (ROOT / "docs/release.md").read_text(),
            (ROOT / "docs/testing.md").read_text(),
        )

    def test_maintenance_authorities_point_to_current_release_state(self) -> None:
        self.assertFalse((ROOT / "release-manifest.json").exists())
        self.assertIn("UNRELEASED", (ROOT / "SOURCE_REVISION").read_text())
        self.assertIn("current task", (ROOT / "docs/release.md").read_text().lower())
        self.assertIn("warmboot-build-plan.md", (ROOT / "MAINTAINING.md").read_text())

    def test_workspace_seed_is_inert_and_outside_managed_payload(self) -> None:
        seed = json.loads(
            (ROOT / "templates" / "project.code-workspace").read_text(encoding="utf-8")
        )
        self.assertEqual(seed, {"folders": [{"path": "."}]})
        payload = CLI_MODULE.expected_install(
            ROOT, (ROOT / ".acceptance-work" / "workspace-contract-target")
        )
        self.assertFalse(any(path.endswith(".code-workspace") for path in payload))

    def test_routine_handoff_and_exceptional_rotation_are_semantically_separate(self) -> None:
        handoff = (ROOT / "routes" / "handoff.md").read_text(encoding="utf-8")
        rotation = (ROOT / "routes" / "rotation.md").read_text(encoding="utf-8")
        template = (ROOT / "templates" / "HANDOFF.md").read_text(encoding="utf-8")

        for routine in (handoff, template):
            self.assertIn("state and evidence", routine)
            self.assertNotIn("RELINQUISHED", routine)
            self.assertNotIn("Decision: `ACCEPTED", routine)
        self.assertIn("session change, provider change", handoff)
        self.assertIn("explicitly named replacement", rotation)
        self.assertIn("RELINQUISHED", rotation)
        self.assertIn("`ACCEPTED`", rotation)
        self.assertIn("provider change", rotation)

    def test_installed_topology_contract_preserves_proportional_role_separation(self) -> None:
        core = (ROOT / "WARMBOOT.md").read_text(encoding="utf-8")
        route = (ROOT / "routes" / "context.md").read_text(encoding="utf-8")
        task = (ROOT / "templates" / "TASK.md").read_text(encoding="utf-8")
        installed = CLI_MODULE.expected_install(
            ROOT, (ROOT / ".acceptance-work" / "topology-contract-target")
        )

        self.assertEqual(installed[".agent-warmboot/core.md"].decode(), core)
        self.assertEqual(installed[".agent-warmboot/routes/context.md"].decode(), route)
        core_flat = " ".join(core.lower().split())
        self.assertIn("independent non-author reviewer", core_flat)
        for text in (core, route, task):
            flat = " ".join(text.lower().split())
            self.assertIn("material", flat)
            self.assertIn("independent", flat)
            self.assertIn("single", flat)
        route_flat = " ".join(route.lower().split())
        self.assertIn("orchestration-only", route_flat)
        self.assertIn("unavoidable", route_flat)
        self.assertIn("unaffected", route_flat)
        self.assertIn("remaining outcome", route_flat)
        self.assertNotRegex(route_flat, r"\b\d+\s+(?:token|turn)s?\b")

    def test_review_contract_converges_on_unchanged_non_author_scope(self) -> None:
        route = (ROOT / "routes" / "review.md").read_text(encoding="utf-8")
        template = (ROOT / "templates" / "project-docs" / "review-brief.md").read_text(
            encoding="utf-8"
        )
        for text in (route, template):
            flat = " ".join(text.lower().split())
            self.assertIn("separate writer", flat)
            self.assertIn("affected evidence", flat)
            self.assertIn("unchanged", flat)
            self.assertIn("expires", flat)
            self.assertIn("no actionable finding", flat)
            self.assertNotRegex(flat, r"exactly [a-z0-9-]+ (?:review|clean)")

        route_flat = " ".join(route.lower().split())
        self.assertIn("digest-bound disposable target", route_flat)
        self.assertIn("governing primary contract", route_flat)
        self.assertIn("unverified claim is not a finding", route_flat)
        self.assertIn("adds no round, stop, or authority", route_flat)
        self.assertNotIn("second review round", route_flat)

    def test_review_release_and_backlog_candidate_contracts_stay_aligned(self) -> None:
        release = (ROOT / "docs/release.md").read_text()
        sequence = release.split("## Freeze and release sequence", 1)[1].split(
            "## External release states", 1
        )[0]
        for earlier, later in (
            ("Finalize all ordinary authored bytes", "writes `SOURCE_REVISION`"),
            ("generates the compact manifest", "exact local `CANDIDATE` commit"),
            ("exact local `CANDIDATE` commit", "dedicated clean verifier checkout"),
            ("dedicated clean verifier checkout", "Independently review"),
        ):
            self.assertLess(sequence.index(earlier), sequence.index(later))
        self.assertIn("self-reference", release)
        self.assertIn(
            "changed selected paths equal note paths",
            " ".join((ROOT / "UPGRADING.md").read_text().split()),
        )
        self.assert_active_backlog_contract(
            (ROOT / "docs/plans/warmboot-build-plan.md").read_text()
        )

    def test_source_comprehension_rule_projects_and_blocks_green_test_substitution(self) -> None:
        """The installed contract and fresh target surfaces carry the operating gate."""

        core = (ROOT / "WARMBOOT.md").read_text(encoding="utf-8")
        bootstrap = (ROOT / "BOOTSTRAP.md").read_text(encoding="utf-8")
        review = (ROOT / "routes" / "review.md").read_text(encoding="utf-8")
        standards = (ROOT / "templates" / "project-docs" / "engineering-standards.md").read_text(
            encoding="utf-8"
        )
        example_source = (
            ROOT / "examples" / "documentation-package" / "src" / "label_normalizer" / "core.py"
        ).read_text(encoding="utf-8")

        installed = CLI_MODULE.expected_install(
            ROOT, (ROOT / ".acceptance-work" / "source-comprehension-contract-target")
        )
        self.assertEqual(installed[".agent-warmboot/core.md"].decode(), core)
        self.assertEqual(installed[".agent-warmboot/routes/review.md"].decode(), review)

        core_flat = " ".join(core.lower().split())
        bootstrap_flat = " ".join(bootstrap.lower().split())
        review_flat = " ".join(review.lower().split())
        standards_flat = " ".join(standards.lower().split())
        for text in (core_flat, bootstrap_flat, standards_flat):
            self.assertIn("every human-authored code file", text)
            self.assertIn("one", text)
            self.assertIn("sentence", text)
        for text in (bootstrap_flat, standards_flat):
            self.assertIn("tests", text)
            self.assertIn("do not substitute", text)
            self.assertIn("non-author", text)
        self.assertIn("every changed", bootstrap_flat)
        self.assertIn("every changed", review_flat)
        self.assertIn("complete set", standards_flat)
        self.assertIn("exact adr", bootstrap_flat)
        self.assertIn("generated", bootstrap_flat)
        self.assertIn("quality-control loop", bootstrap_flat)
        coded_floor = bootstrap.split("### Coded-project operating floor", 1)[1]
        coded_floor = coded_floor.split("\n## ", 1)[0]
        for role in (
            "README",
            "source/test/docs layout",
            "source/engineering rules",
            "testing/evidence commands",
            "component/ownership map",
            "change history",
            "observed-defect/recurrence owner",
            "current task or plan",
            "blocking non-author review gate",
        ):
            self.assertIn(role, coded_floor)
        self.assertIn("NOT APPLICABLE — NO HUMAN-AUTHORED CODE", coded_floor)
        self.assertIn("Merge them into existing credible surfaces", coded_floor)
        self.assertNotIn("capability cards", coded_floor)
        self.assertIn("normalization-order", example_source)

    def test_bounded_worker_git_history_contract_is_consistent_and_installed(self) -> None:
        def load(relative: str) -> str:
            return (ROOT / relative).read_text(encoding="utf-8")

        route = load("routes/context.md")
        core = load("WARMBOOT.md")
        bootstrap = load("BOOTSTRAP.md")
        route_flat = " ".join(route.split())

        allowlist_block = route.split("current bounded allowlist is:", 1)[1].split(
            "Record every exact command", 1
        )[0]
        for allowed in (
            "`git rev-parse --verify`",
            "`git status --short --untracked-files=all`",
            "`git --no-pager log`",
            "`git --no-pager log --follow`",
            "`git --no-pager show --no-ext-diff`",
            "`git --no-pager blame`",
        ):
            self.assertIn(allowed, allowlist_block)
        self.assertNotIn("`git diff", allowlist_block)

        # The canonical home defines the allowlist by extension: exactly these six
        # commands, no seventh smuggled into the block.
        canonical_commands = tuple(
            sorted(GIT_BACKTICK_PATTERN.findall(" ".join(allowlist_block.split())))
        )
        self.assertEqual(canonical_commands, CANONICAL_GIT_COMMANDS)
        canonical_set = set(canonical_commands)
        # Outside its own allowlist block the canonical home names only the
        # compare-with-`git show`-instead pointer.
        self.assertEqual(
            git_commands_in(route) - canonical_set,
            {"git show"},
        )

        denylist_block = route.split("No unlisted Git command is allowed.", 1)[1]
        for forbidden in (
            "config",
            "`-c`",
            "fetch/pull",
            "worktree administration",
            "branch",
            "add",
            "commit",
            "push",
            "remote/network",
            "credential",
        ):
            self.assertIn(forbidden, denylist_block)
        self.assertIn(
            "or any other index/ref/worktree mutation",
            " ".join(denylist_block.split()),
        )
        self.assertIn("Every form of `git diff` is excluded", route_flat)
        self.assertIn("initial lane assignment", route_flat)
        self.assertIn("exact absolute local repository", route_flat)
        self.assertIn("frozen ref/object identities and allowed ancestry", route_flat)
        self.assertIn("exact pathspecs", route_flat)
        self.assertIn("GIT_OPTIONAL_LOCKS=0", route)
        self.assertIn("git --no-optional-locks", route)

        routed_authorities = (
            "WARMBOOT.md",
            "BOOTSTRAP.md",
            "MAINTAINING.md",
            "WHY.md",
            "docs/engineering-standards.md",
            "docs/maintainer-system-map.md",
            "docs/documentation-architecture.md",
            "docs/source-refresh.md",
            "docs/decisions.md",
            "templates/TASK.md",
        )
        for relative in routed_authorities:
            authority_flat = " ".join(load(relative).split())
            self.assertIn("context.md", authority_flat, relative)
            self.assertIn("`git diff`", authority_flat, relative)
            # Pointer-only: routing to the canonical home, never a partial copy.
            self.assertEqual(git_commands_in(authority_flat), set(), relative)

        standalone_authorities = (
            "routes/context.md",
            "docs/invariants.md",
            "templates/project-docs/AGENTS.md",
            "templates/project-docs/engineering-standards.md",
            "examples/documentation-package/AGENTS.md",
            "examples/documentation-package/docs/engineering-standards.md",
        )
        contradictory_worker_git = re.compile(
            r"\bworkers?(?:\s+and\s+reviewers)?\b.{0,180}\bnever\s+Git\b|"
            r"\bworkers?\b.{0,120}\bnever\s+(?:run|use|operate|touch)\s+Git\b",
            re.IGNORECASE,
        )
        for relative in standalone_authorities:
            authority = load(relative)
            authority_flat = " ".join(authority.split())
            self.assertIn("GIT_OPTIONAL_LOCKS=0", authority_flat, relative)
            self.assertIn("git --no-optional-locks", authority_flat, relative)
            for command in canonical_commands:
                self.assertIn(f"`{command}`", authority_flat, relative)
            self.assertIn("`git diff`", authority_flat, relative)
            self.assertTrue(
                "sole Git mutator" in authority_flat
                or "only Git mutator" in authority_flat
                or "coordinator alone mutates Git" in authority_flat,
                relative,
            )
            self.assertIsNone(contradictory_worker_git.search(authority_flat), relative)

        # Command-list equality: discover every remaining restatement home by
        # content, not by hope. A file that restates two or more of the canonical
        # commands is a home and must be registered above; a drifted copy — an extra
        # command, a dropped command, a lost `git diff` exclusion — fails here.
        restatement_homes = tuple(
            relative
            for relative in standalone_authorities
            if relative != CANONICAL_GIT_ALLOWLIST_HOME
        )
        discovered, diff_offenders = scan_git_command_homes(canonical=canonical_commands)
        # Nowhere in the repository may a `git diff` form sit inside a command
        # list. Set equality cannot catch this on its own: `git_commands_in`
        # forgives every `git diff` token, so a home could both state the
        # exclusion and enumerate `git diff --no-ext-diff --stat` as eligible,
        # which WB-016 forbids.
        self.assertEqual(diff_offenders, [])
        self.assertEqual(discovered, set(standalone_authorities))
        for relative in restatement_homes:
            home_flat = " ".join(load(relative).split())
            home_commands = git_commands_in(home_flat)
            self.assertEqual(home_commands - canonical_set, set(), relative)
            self.assertEqual(home_commands, canonical_set, relative)
            self.assertIsNotNone(GIT_DIFF_EXCLUSION_PATTERN.search(home_flat), relative)

        # On the governed surface the rule is absolute rather than `git diff`-shaped:
        # every command a pointer-only or restatement home enumerates must be one of
        # the canonical six, so no seventh command of any name reaches an allowlist.
        for relative in routed_authorities + standalone_authorities:
            for enumeration in git_command_enumerations(load(relative)):
                self.assertEqual(
                    [command for command in enumeration if command not in canonical_set],
                    [],
                    relative,
                )

        for relative in routed_authorities + standalone_authorities:
            self.assertIsNone(
                contradictory_worker_git.search(" ".join(load(relative).split())), relative
            )
        task_flat = " ".join(load("templates/TASK.md").split())
        self.assertIn("initial assignment", task_flat)
        self.assertIn("sole Git mutator", task_flat)
        self.assertIn("attested allowlist in `.agent-warmboot/routes/context.md`", task_flat)
        self.assertIn("every `git diff` form excluded", task_flat)
        for command in canonical_commands:
            self.assertNotIn(f"`{command}`", task_flat)
        self.assertIn(
            "Bounded worker/reviewer local Git history inspection: `NOT REQUIRED`",
            load("examples/documentation-package/TASK.md"),
        )
        self.assertIn("independently refreshes authoritative", core)
        self.assertIn("independently refreshes", bootstrap)

        installed = CLI_MODULE.expected_install(
            ROOT, (ROOT / ".acceptance-work" / "git-history-contract-target")
        )
        installed_core = installed[".agent-warmboot/core.md"].decode("utf-8")
        installed_route = installed[".agent-warmboot/routes/context.md"].decode("utf-8")
        self.assertEqual(installed_core, core)
        self.assertEqual(installed_route, route)
        self.assertIn("sole Git mutator", installed_core)
        installed_route_flat = " ".join(installed_route.split())
        self.assertIn("Every form of `git diff` is excluded", installed_route_flat)
        for command in canonical_commands:
            self.assertIn(f"`{command}`", installed_route_flat)
        self.assertIn("GIT_OPTIONAL_LOCKS=0", installed_route_flat)
        self.assertIn("git --no-optional-locks", installed_route_flat)

    def test_installed_status_vocabulary_is_defined_in_the_installed_files(self) -> None:
        """Every backticked ALL-CAPS status label on the installed surface is defined there.

        Permitted set, all defined in installed files (the install-boundary rule —
        a term used in installed files is defined in installed files, or not used
        there): `ACCEPTED`, `BLOCKED`, `CLEAN`, `CONFIRMED`, `DOWNGRADED`,
        `FINDING`, `INHERITED`, `NOT REQUIRED`, `PROVED`, `REFUTED`, `REJECTED`,
        `RELINQUISHED`, `RERUN NOW`, `UNPROVED`. Each token's defining home is
        pinned below. A new undefined label entering the installed payload fails
        this test.
        """
        sources = {"WARMBOOT.md": (ROOT / "WARMBOOT.md").read_text(encoding="utf-8")}
        for route in sorted((ROOT / "routes").glob("*.md")):
            sources[route.name] = route.read_text(encoding="utf-8")
        self.assertEqual(
            set(sources),
            {
                "WARMBOOT.md",
                "context.md",
                "evidence.md",
                "handoff.md",
                "review.md",
                "rotation.md",
            },
        )
        installed = CLI_MODULE.expected_install(
            ROOT, (ROOT / ".acceptance-work" / "vocabulary-target")
        )
        self.assertEqual(
            installed[".agent-warmboot/core.md"].decode("utf-8"), sources["WARMBOOT.md"]
        )
        for name, text in sources.items():
            if name == "WARMBOOT.md":
                continue
            self.assertEqual(
                installed[f".agent-warmboot/routes/{name}"].decode("utf-8"), text, name
            )

        defining_home = {
            "ACCEPTED": "rotation.md",
            "BLOCKED": "evidence.md",
            "CLEAN": "review.md",
            "CONFIRMED": "review.md",
            "DOWNGRADED": "review.md",
            "FINDING": "review.md",
            "INHERITED": "handoff.md",
            "NOT REQUIRED": "WARMBOOT.md",
            "PROVED": "evidence.md",
            "REFUTED": "review.md",
            "REJECTED": "rotation.md",
            "RELINQUISHED": "rotation.md",
            "RERUN NOW": "handoff.md",
            "UNPROVED": "evidence.md",
        }
        collected: set[str] = set()
        for text in sources.values():
            for token in STATUS_TOKEN_PATTERN.findall(text):
                if token.endswith(".md") or "." in token:
                    continue
                collected.add(token)
        undefined = sorted(collected - set(defining_home))
        self.assertEqual(undefined, [], f"undefined installed label(s): {undefined}")
        unused = sorted(set(defining_home) - collected)
        self.assertEqual(unused, [], f"permitted label(s) no longer used: {unused}")
        for token, home in defining_home.items():
            self.assertIn(f"`{token}`", sources[home], token)

        def is_glossed(text: str, token: str) -> bool:
            flat = " ".join(text.split())
            return bool(
                re.search(
                    rf"`{re.escape(token)}`\s*(?:\(|means\b|—)",
                    flat,
                )
            )

        evidence = sources["evidence.md"]
        for token in ("PROVED", "UNPROVED", "BLOCKED"):
            self.assertTrue(is_glossed(evidence, token), token)
        self.assertTrue(is_glossed(sources["handoff.md"], "RERUN NOW"))
        self.assertTrue(is_glossed(sources["rotation.md"], "REJECTED"))

    def test_template_pack_membership_is_derived_from_the_role_selection_table(self) -> None:
        """`templates/project-docs/` membership equals the role-selection table's samples.

        The sample set is derived from `docs/documentation-architecture.md`'s
        role-selection table rather than hand-kept. A sample added without a table
        row, or a row naming a missing sample, fails here.
        """
        header = "| Need in the target | Sample | Common merge destination | Omit when |"
        first_row = (
            "| Provider-neutral safety core and task router | `AGENTS.md` | "
            "Existing root/provider instructions | Managed loaders suffice, or an "
            "existing router owns the role |"
        )

        def referenced_samples(document: str) -> list[str]:
            lines = split_markdown_lines(document)
            self.assertIn(header, lines)
            start = lines.index(header)
            rows = []
            for line in lines[start + 1 :]:
                if not line.startswith("|"):
                    break
                cells = split_markdown_table_cells(line)
                if all(set(cell) <= {"-", ":"} and cell for cell in cells):
                    continue
                self.assertEqual(len(cells), 4, line)
                rows.append(cells)
            self.assertTrue(rows)

            referenced = []
            for cells in rows:
                match = re.fullmatch(r"`([^`]+\.md)`", cells[1])
                self.assertIsNotNone(match, cells[1])
                referenced.append(match.group(1))
            return referenced

        architecture = (ROOT / "docs" / "documentation-architecture.md").read_text(encoding="utf-8")
        self.assertIn(first_row, architecture)
        referenced = referenced_samples(architecture)
        self.assertEqual(len(referenced), len(set(referenced)), referenced)

        pack = {path.name for path in (ROOT / "templates" / "project-docs").glob("*.md")}
        self.assertEqual(set(referenced), pack)
        self.assertEqual(
            {path.name for path in (ROOT / "templates" / "project-docs").iterdir()},
            pack,
        )
        self.assertEqual(split_markdown_table_cells("| one | two |"), ["one", "two"])
        self.assertEqual(split_markdown_table_cells("one | two"), ["one", "two"])
        repeated_pipe_rows = (
            ("doubled leading", "|" + first_row),
            ("doubled trailing", first_row + "|"),
            ("both edges", "|" + first_row + "|"),
            (
                "internal empty cell",
                first_row.replace("| `AGENTS.md` |", "| `AGENTS.md` ||", 1),
            ),
        )
        for name, replacement in repeated_pipe_rows:
            with self.subTest(pipe_shape=name), self.assertRaises(AssertionError):
                referenced_samples(architecture.replace(first_row, replacement, 1))

        for separator_name, separator in NON_MARKDOWN_LINE_SEPARATORS:
            with self.subTest(separator=separator_name):
                row_boundary = "\n" + first_row
                self.assertIn(row_boundary, architecture)
                malformed = architecture.replace(row_boundary, separator + first_row, 1)
                with self.assertRaises(AssertionError):
                    referenced_samples(malformed)
            with self.subTest(separator=separator_name, position="sample cell edge"):
                sample_cell = "| `AGENTS.md` |"
                self.assertIn(sample_cell, architecture)
                malformed = architecture.replace(sample_cell, f"| {separator}`AGENTS.md` |", 1)
                with self.assertRaises(AssertionError):
                    referenced_samples(malformed)
        for name, line_ending in (("LF", "\n"), ("CRLF", "\r\n"), ("CR", "\r")):
            with self.subTest(line_ending=name):
                self.assertEqual(
                    referenced_samples(architecture.replace("\n", line_ending)),
                    referenced,
                )

    def test_core_and_rotation_route_carry_the_exact_review_authority_and_absence_rules(
        self,
    ) -> None:
        """Each sentence is pinned whole: dropping one qualifier must fail this test."""
        core = " ".join((ROOT / "WARMBOOT.md").read_text(encoding="utf-8").split())
        rotation = " ".join((ROOT / "routes/rotation.md").read_text(encoding="utf-8").split())
        for sentence in (
            "Every code change, however small, gets an independent non-author reviewer",
            "and an independent non-author reviewer repeats that reconciliation",
            (
                "Only an agent granted the work may append itself as coordinator when none is"
                " recorded or the coordinator is demonstrably absent, recording why; a delegated"
                " lane never does. Other holders change only by rotation"
            ),
            (
                "installing packages, and other external effects need separate explicit user"
                " authorization"
            ),
        ):
            with self.subTest(sentence=sentence[:40]):
                self.assertIn(sentence, core)
        self.assertEqual(core.count("independent non-author reviewer"), 2)
        self.assertIn(
            "When the outgoing holder is demonstrably absent and cannot freeze, the"
            " coordinator records the absence, the evidence for it, and the user's direction"
            " in place of this step; the replacement then continues from section 2, the"
            " independent replacement preflight. Nothing the absent holder left is discarded"
            " without inspection.",
            rotation,
        )

    def test_installed_core_stays_within_budget_and_carries_no_maintainer_residue(self) -> None:
        core = (ROOT / "WARMBOOT.md").read_text(encoding="utf-8")
        installed = CLI_MODULE.expected_install(
            ROOT, (ROOT / ".acceptance-work" / "core-budget-target")
        )
        installed_core = installed[".agent-warmboot/core.md"].decode("utf-8")

        self.assertEqual(installed_core, core)
        licence = (ROOT / "LICENSE").read_text(encoding="utf-8")
        legal_footer = "\n## License\n\n" + licence
        self.assertTrue(core.endswith(legal_footer))
        # Legal terms travel with copies; keep the operating-policy budget separate.
        self.assertLessEqual(len(core.removesuffix(legal_footer).split()), 800)
        # Maintainer-only records stay out of the installed core, which routes
        # toolkit maintenance to MAINTAINING.md instead.
        for residue in ("docs/plans/", "BUGFIXES.md", "CHANGELOG.md", "acceptance/"):
            self.assertNotIn(residue, installed_core, residue)
        self.assertIn("MAINTAINING.md", installed_core)

    def assert_final_structure_race_is_preserved(
        self, inject, expected_failure: str, expected_check: str
    ) -> None:
        original_create = CLI_MODULE.atomic_create
        injected = False
        warnings = io.StringIO()
        output = io.StringIO()

        def inject_after_last_create(destination: Path, data: bytes, parent_handle=None):
            nonlocal injected
            receipt = original_create(destination, data, parent_handle)
            if destination.name == "CLAUDE.md":
                inject()
                injected = True
            return receipt

        with (
            mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit),
            mock.patch.object(CLI_MODULE, "atomic_create", side_effect=inject_after_last_create),
            mock.patch.object(
                CLI_MODULE.os, "unlink", side_effect=AssertionError("unlink forbidden")
            ) as unlink,
            mock.patch.object(
                CLI_MODULE.os, "rmdir", side_effect=AssertionError("rmdir forbidden")
            ) as rmdir,
            redirect_stderr(warnings),
            redirect_stdout(output),
        ):
            with self.assertRaises(CLI_MODULE.WarmbootError) as caught:
                CLI_MODULE.init_command(str(self.target), apply=True)

        self.assertTrue(injected)
        self.assertIn(expected_failure, str(caught.exception))
        self.assertNotIn("APPLIED", output.getvalue())
        self.assertIn("install stopped without rollback", warnings.getvalue())
        self.assertIn(expected_failure, warnings.getvalue())
        unlink.assert_not_called()
        rmdir.assert_not_called()

        checked = io.StringIO()
        with redirect_stdout(checked):
            self.assertEqual(CLI_MODULE.check_command(str(self.target)), 1)
        self.assertIn(expected_check, checked.getvalue())

    def test_preview_lists_exact_changes_without_mutation(self) -> None:
        result = self.run_cli("init", str(self.target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                f"PREVIEW {self.target.resolve()} (agent review required; target semantics not inferred)",
                "CREATE-DIR .agent-warmboot",
                "CREATE-DIR .agent-warmboot/routes",
                "CREATE-FILE .agent-warmboot/core.md",
                "CREATE-FILE .agent-warmboot/manifest.json",
                "CREATE-FILE .agent-warmboot/routes/review.md",
                "CREATE-FILE .agent-warmboot/routes/work.md",
                "CREATE-FILE AGENTS.md",
                "CREATE-FILE CLAUDE.md",
                CLI_MODULE.WORKSPACE_NOTICE,
            ],
        )
        self.assertEqual(list(self.target.iterdir()), [])

    def test_apply_installs_core_routes_loaders_and_manifest(self) -> None:
        source_core = (ROOT / "WARMBOOT.md").read_bytes()
        (self.toolkit / "WARMBOOT.md").write_bytes(source_core)
        result = self.apply()
        self.assertEqual(result.returncode, 0, result.stderr)
        installed_core = (self.target / ".agent-warmboot" / "core.md").read_bytes()
        self.assertEqual(installed_core, source_core)
        self.assertIn((ROOT / "LICENSE").read_bytes(), installed_core)
        self.assertEqual(
            (self.target / ".agent-warmboot" / "routes" / "review.md").read_text(encoding="utf-8"),
            "# Review route\n",
        )
        self.assertEqual(
            (self.target / "AGENTS.md").read_bytes(),
            (self.target / "CLAUDE.md").read_bytes(),
        )
        self.assertFalse((self.target / "target.code-workspace").exists())
        manifest = json.loads(
            (self.target / ".agent-warmboot" / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["schema"], 1)
        self.assertEqual(manifest["toolkit"], "agent-warmboot")
        self.assertEqual(manifest["source_revision"], "test-revision")
        core = (self.target / ".agent-warmboot" / "core.md").read_bytes()
        self.assertEqual(
            manifest["files"][".agent-warmboot/core.md"], hashlib.sha256(core).hexdigest()
        )
        self.assertFalse(any(path.endswith(".code-workspace") for path in manifest["files"]))
        self.assertIn(CLI_MODULE.WORKSPACE_NOTICE, result.stdout)

    def test_installed_loaders_carry_the_shared_protocol_identity(self) -> None:
        # Pinned as a literal, not read back from the helper: `check` compares installed
        # loaders against the running helper's text, so a change here makes every
        # existing install fail `check` under the changed helper.
        expected = (
            b"# Warmboot Loader\n"
            b"\n"
            b"Read `.agent-warmboot/core.md` before starting work. Use its routing rules to load\n"
            b"only the relevant files from `.agent-warmboot/routes/` for the current task.\n"
            b"\n"
            b"This loader is managed by agent-warmboot. Keep `AGENTS.md` and `CLAUDE.md`\n"
            b"identical so either provider enters through the same neutral contract.\n"
        )
        self.assertEqual(CLI_MODULE.TOOLKIT_NAME, "agent-warmboot")
        self.assertEqual(CLI_MODULE.MANAGED_DIR, ".agent-warmboot")
        self.assertEqual(self.apply().returncode, 0)
        for loader in ("AGENTS.md", "CLAUDE.md"):
            with self.subTest(loader=loader):
                self.assertEqual((self.target / loader).read_bytes(), expected)
        checked = self.run_cli("check", str(self.target))
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_source_revision_absence_never_calls_subprocess_or_git(self) -> None:
        (self.toolkit / "SOURCE_REVISION").unlink()
        with mock.patch("subprocess.run", side_effect=AssertionError("subprocess forbidden")):
            self.assertEqual(CLI_MODULE.source_revision(self.toolkit), "UNCOMMITTED")

    def test_source_revision_rejects_unsafe_format(self) -> None:
        for value in ("embedded\tcontrol\n", "x" * 257 + "\n"):
            with self.subTest(value_length=len(value)):
                (self.toolkit / "SOURCE_REVISION").write_text(value, encoding="utf-8")
                with self.assertRaisesRegex(
                    CLI_MODULE.WarmbootError, "one non-empty printable line"
                ):
                    CLI_MODULE.source_revision(self.toolkit)

    def test_check_passes_after_apply(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        result = self.run_cli("check", str(self.target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("manifest-declared content and structure matched", result.stdout)
        self.assertIn("frozen file(s) plus the manifest;", result.stdout)
        self.assertIn(
            "source_revision is informational/self-declared, not authenticated", result.stdout
        )
        self.assertIn(CLI_MODULE.WORKSPACE_NOTICE, result.stdout)

    def test_check_uses_frozen_manifest_after_source_revision_changes(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        (self.toolkit / "SOURCE_REVISION").write_text("later-revision\n", encoding="utf-8")
        (self.toolkit / "WARMBOOT.md").write_text("# Later source core\n", encoding="utf-8")
        result = self.run_cli("check", str(self.target))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_check_does_not_authenticate_manifest_declared_source_revision(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        manifest_path = self.target / ".agent-warmboot" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["source_revision"] = "coherently-tampered-metadata"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        result = self.run_cli("check", str(self.target))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("manifest-declared content and structure matched", result.stdout)
        self.assertIn("informational/self-declared, not authenticated", result.stdout)
        self.assertNotIn("provenance", result.stdout.lower())

    def test_check_rejects_boolean_manifest_schema(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        manifest_path = self.target / ".agent-warmboot" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["schema"] = True
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        result = self.run_cli("check", str(self.target))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("manifest.json: unsupported schema", result.stdout)

    def test_check_rejects_duplicate_key_manifest(self) -> None:
        """Installed-state duplicate-key manifests must fail closed, not last-wins.

        WB-046: the import-free CLI parses `manifest.json` itself, so a repeated object
        key — top-level or nested — must be rejected at parse rather than silently
        resolved to its last value (WB-017's rule, applied to the installed-state gate).
        A bogus first block (a 0*64 digest for a frozen path) shadowed by the real block
        would otherwise let a tampered install pass `check` at exit 0. `json.dumps`
        cannot emit a repeated key, so each manifest is assembled as raw text.
        """
        self.assertEqual(self.apply().returncode, 0)
        manifest_path = self.target / ".agent-warmboot" / "manifest.json"
        real = json.loads(manifest_path.read_text(encoding="utf-8"))
        frozen_path = min(real["files"])

        def render(pairs: list, indent: int) -> str:
            pad = " " * indent
            body = ",\n".join(f"{pad}{json.dumps(key)}: {value}" for key, value in pairs)
            return "{\n" + body + "\n" + " " * (indent - 2) + "}"

        bogus_files = {
            path: ("0" * 64 if path == frozen_path else digest)
            for path, digest in real["files"].items()
        }
        nested_files = render(
            [(frozen_path, json.dumps("0" * 64))]
            + [(path, json.dumps(digest)) for path, digest in sorted(real["files"].items())],
            4,
        )
        scalars = [
            ("schema", json.dumps(real["schema"])),
            ("source_revision", json.dumps(real["source_revision"])),
            ("toolkit", json.dumps(real["toolkit"])),
        ]
        duplicate_manifests = {
            "top-level duplicate files key": render(
                [
                    ("files", json.dumps(bogus_files, sort_keys=True)),
                    ("files", json.dumps(real["files"], sort_keys=True)),
                    *scalars,
                ],
                2,
            ),
            "nested duplicate managed-file key": render([("files", nested_files), *scalars], 2),
        }
        for name, raw in sorted(duplicate_manifests.items()):
            with self.subTest(manifest=name):
                manifest_path.write_text(raw + "\n", encoding="utf-8")
                result = self.run_cli("check", str(self.target))
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("manifest.json: invalid JSON", result.stdout)

    def test_check_rejects_deeply_nested_manifest_as_invalid_json(self) -> None:
        """Nesting deep enough to exhaust the decoder's recursion must fail as invalid JSON.

        WB-052: the decoder raises RecursionError, which is not a ValueError, so `check`
        catches it explicitly and reports a clean FAIL line rather than a traceback.
        """
        self.assertEqual(self.apply().returncode, 0)
        manifest_path = self.target / ".agent-warmboot" / "manifest.json"
        manifest_path.write_text("[" * 200000 + "]" * 200000 + "\n", encoding="utf-8")

        result = self.run_cli("check", str(self.target))

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("manifest.json: invalid JSON", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_check_rejects_non_json_numeric_constants(self) -> None:
        """`NaN`, `Infinity` and `-Infinity` are not JSON and must fail as invalid JSON.

        WB-053: the standard decoder accepts these tokens by default, and other JSON
        readers reject them, so `check` rejects them too.
        """
        self.assertEqual(self.apply().returncode, 0)
        manifest_path = self.target / ".agent-warmboot" / "manifest.json"
        original = manifest_path.read_text(encoding="utf-8")
        self.assertIn('"schema": 1', original)
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                manifest_path.write_text(
                    original.replace('"schema": 1', f'"schema": {token}', 1),
                    encoding="utf-8",
                )
                result = self.run_cli("check", str(self.target))
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("manifest.json: invalid JSON", result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_apply_is_idempotent(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        before = {
            path.relative_to(self.target): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.target.rglob("*")
            if path.is_file()
        }
        second = self.apply()
        after = {
            path.relative_to(self.target): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.target.rglob("*")
            if path.is_file()
        }
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("0 file(s) created", second.stdout)
        self.assertEqual(before, after)

    def test_loader_conflict_fails_before_any_mutation(self) -> None:
        (self.target / "AGENTS.md").write_text(
            "# Project-specific instructions\n", encoding="utf-8"
        )
        result = self.apply()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("is not the Warmboot loader", result.stderr)
        self.assertIn("BOOTSTRAP.md#existing-agent-instructions", result.stderr)
        self.assertFalse((self.target / ".agent-warmboot").exists())
        self.assertFalse((self.target / "CLAUDE.md").exists())
        self.assertEqual(
            (self.target / "AGENTS.md").read_text(encoding="utf-8"),
            "# Project-specific instructions\n",
        )

    def test_target_named_workspace_is_unmanaged_and_preserved(self) -> None:
        workspace = self.target / "target.code-workspace"
        sentinel = b'{"folders": [], "settings": {"sentinel": true}}\n'
        workspace.write_bytes(sentinel)
        result = self.apply()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(workspace.read_bytes(), sentinel)
        check = self.run_cli("check", str(self.target))
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        self.assertEqual(workspace.read_bytes(), sentinel)

    def test_preexisting_binary_under_managed_root_fails_before_mutation(self) -> None:
        managed = self.target / ".agent-warmboot"
        managed.mkdir()
        preexisting = managed / "preexisting.bin"
        preexisting.write_bytes(b"preserve me\x00")

        result = self.apply()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected managed path(s): .agent-warmboot/preexisting.bin", result.stderr)
        self.assertEqual(preexisting.read_bytes(), b"preserve me\x00")
        self.assertEqual(sorted(path.name for path in managed.iterdir()), ["preexisting.bin"])
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertFalse((self.target / "CLAUDE.md").exists())
        self.assertFalse((self.target / "target.code-workspace").exists())

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO creation is unavailable")
    def test_fifo_under_managed_root_is_always_unexpected(self) -> None:
        managed = self.target / ".agent-warmboot"
        managed.mkdir()
        fifo = managed / "preexisting.fifo"
        os.mkfifo(fifo)

        refused = self.apply()

        self.assertNotEqual(refused.returncode, 0)
        self.assertIn(
            "unexpected managed path(s): .agent-warmboot/preexisting.fifo", refused.stderr
        )
        self.assertFalse((self.target / "AGENTS.md").exists())
        fifo.unlink()
        self.assertEqual(self.apply().returncode, 0)
        extra_fifo = managed / "unexpected.fifo"
        os.mkfifo(extra_fifo)

        checked = self.run_cli("check", str(self.target))

        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("unexpected managed path(s): .agent-warmboot/unexpected.fifo", checked.stdout)

    def test_unexpected_managed_directory_and_symlink_fail_before_mutation(self) -> None:
        routes = self.target / ".agent-warmboot" / "routes"
        routes.mkdir(parents=True)
        unexpected_directory = self.target / ".agent-warmboot" / "cache"
        unexpected_directory.mkdir()
        (unexpected_directory / "state.bin").write_bytes(b"state")
        sentinel = self.target / "sentinel.txt"
        sentinel.write_text("keep\n", encoding="utf-8")
        unexpected_symlink = self.target / ".agent-warmboot" / "sentinel-link"
        unexpected_symlink.symlink_to("../sentinel.txt")

        result = self.apply()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(".agent-warmboot/cache", result.stderr)
        self.assertIn(".agent-warmboot/sentinel-link", result.stderr)
        self.assertTrue(unexpected_directory.is_dir())
        self.assertEqual((unexpected_directory / "state.bin").read_bytes(), b"state")
        self.assertTrue(unexpected_symlink.is_symlink())
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")
        self.assertEqual(list(routes.iterdir()), [])
        self.assertFalse((self.target / ".agent-warmboot" / "core.md").exists())
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertFalse((self.target / "CLAUDE.md").exists())
        self.assertFalse((self.target / "target.code-workspace").exists())

    def test_empty_expected_managed_parent_directories_are_preserved(self) -> None:
        routes = self.target / ".agent-warmboot" / "routes"
        routes.mkdir(parents=True)
        managed_identity = (routes.parent.stat().st_dev, routes.parent.stat().st_ino)
        routes_identity = (routes.stat().st_dev, routes.stat().st_ino)

        result = self.apply()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(routes.is_dir())
        self.assertEqual(
            (routes.parent.stat().st_dev, routes.parent.stat().st_ino), managed_identity
        )
        self.assertEqual((routes.stat().st_dev, routes.stat().st_ino), routes_identity)
        check = self.run_cli("check", str(self.target))
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_differently_named_workspace_survives_preview_apply_rerun_and_check(self) -> None:
        other = self.target / "existing.code-workspace"
        sentinel = (
            b'{"folders": [{"path": "existing"}], "settings": {"sentinel": true}, '
            b'"tasks": {"version": "2.0.0", "tasks": []}}\n'
        )
        other.write_bytes(sentinel)

        preview = self.run_cli("init", str(self.target))
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertEqual(other.read_bytes(), sentinel)

        applied = self.apply()
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(other.read_bytes(), sentinel)
        rerun = self.apply()
        self.assertEqual(rerun.returncode, 0, rerun.stderr)
        self.assertEqual(other.read_bytes(), sentinel)
        check = self.run_cli("check", str(self.target))
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        self.assertEqual(other.read_bytes(), sentinel)
        self.assertFalse((self.target / "target.code-workspace").exists())

    def test_multiple_invalid_and_symlink_workspaces_are_unmanaged_and_preserved(self) -> None:
        backing = self.target / "workspace-source.json"
        backing.write_text('{"folders": []}\n', encoding="utf-8")
        invalid = self.target / "target.code-workspace"
        invalid_bytes = b"not-json\n"
        invalid.write_bytes(invalid_bytes)
        workspace = self.target / "linked.code-workspace"
        workspace.symlink_to(backing.name)
        result = self.apply()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(invalid.read_bytes(), invalid_bytes)
        self.assertTrue(workspace.is_symlink())
        self.assertEqual(os.readlink(workspace), backing.name)
        check = self.run_cli("check", str(self.target))
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        self.assertEqual(invalid.read_bytes(), invalid_bytes)
        self.assertTrue(workspace.is_symlink())

    def test_workspace_edit_after_apply_does_not_fail_managed_check(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        workspace = self.target / "target.code-workspace"
        workspace.write_text('{"folders": [{"path": ".", "name": "Target"}]}\n', encoding="utf-8")
        first = self.run_cli("check", str(self.target))
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        workspace.write_text(
            '{"folders": [{"path": ".", "name": "Target project"}], '
            '"settings": {"editor.formatOnSave": true}}\n',
            encoding="utf-8",
        )
        second = self.run_cli("check", str(self.target))
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn(CLI_MODULE.WORKSPACE_NOTICE, second.stdout)

    def test_final_rescan_rejects_concurrent_unexpected_managed_path(self) -> None:
        extra = self.target / ".agent-warmboot" / "concurrent-extra.bin"

        self.assert_final_structure_race_is_preserved(
            lambda: extra.write_bytes(b"concurrent managed content\n"),
            "unexpected managed path(s): .agent-warmboot/concurrent-extra.bin",
            "unexpected managed path(s): .agent-warmboot/concurrent-extra.bin",
        )

        self.assertEqual(extra.read_bytes(), b"concurrent managed content\n")
        self.assertTrue((self.target / ".agent-warmboot" / "manifest.json").is_file())

    def test_final_rescan_rejects_concurrent_root_stage(self) -> None:
        stage_name = f".{CLI_MODULE.MANAGED_DIR}.{'0' * 24}.create"
        stage = self.target / stage_name

        self.assert_final_structure_race_is_preserved(
            stage.mkdir,
            f"preserved staged path(s) require inspection: {stage_name}",
            f"preserved staged path(s) require inspection: {stage_name}",
        )

        self.assertTrue(stage.is_dir())
        self.assertTrue((self.target / "CLAUDE.md").is_file())

    def test_create_failure_preserves_compatible_progress_for_rerun(self) -> None:
        sentinel = self.target / "TASK.md"
        sentinel.write_bytes(b"existing task\n")
        original_create = CLI_MODULE.atomic_create
        call_count = 0
        warnings = io.StringIO()

        def fail_on_second_create(destination: Path, data: bytes, parent_handle=None):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise OSError("injected second-create failure")
            return original_create(destination, data, parent_handle)

        with (
            mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit),
            mock.patch.object(CLI_MODULE, "atomic_create", side_effect=fail_on_second_create),
            redirect_stderr(warnings),
        ):
            with self.assertRaisesRegex(OSError, "injected second-create failure"):
                CLI_MODULE.init_command(str(self.target), apply=True)

        core = self.target / ".agent-warmboot" / "core.md"
        self.assertEqual(sentinel.read_bytes(), b"existing task\n")
        self.assertEqual(core.read_bytes(), b"# Test core\n")
        self.assertTrue((self.target / ".agent-warmboot" / "routes").is_dir())
        self.assertFalse((self.target / ".agent-warmboot" / "manifest.json").exists())
        self.assertIn("install stopped without rollback", warnings.getvalue())
        self.assertIn(str(core), warnings.getvalue())

        recovered = self.apply()
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        self.assertEqual(core.read_bytes(), b"# Test core\n")
        self.assertEqual(self.run_cli("check", str(self.target)).returncode, 0)

    def test_managed_parent_symlink_swap_cannot_redirect_creation(self) -> None:
        managed = self.target / ".agent-warmboot"
        routes = managed / "routes"
        routes.mkdir(parents=True)
        detached = self.target / "detached-managed"
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        original_create = CLI_MODULE.atomic_create
        swapped = False
        warnings = io.StringIO()

        def swap_then_create(destination: Path, data: bytes, parent_handle=None):
            nonlocal swapped
            if CLI_MODULE.MANAGED_DIR in destination.parts and not swapped:
                managed.rename(detached)
                managed.symlink_to(outside, target_is_directory=True)
                swapped = True
            return original_create(destination, data, parent_handle)

        with (
            mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit),
            mock.patch.object(CLI_MODULE, "atomic_create", side_effect=swap_then_create),
            redirect_stderr(warnings),
        ):
            with self.assertRaisesRegex(
                CLI_MODULE.WarmbootError, "directory containment changed during install"
            ):
                CLI_MODULE.init_command(str(self.target), apply=True)

        self.assertTrue(swapped)
        self.assertTrue(managed.is_symlink())
        self.assertEqual(list(outside.iterdir()), [])
        self.assertEqual([routes for routes in detached.rglob("*") if routes.is_file()], [])
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertFalse((self.target / "CLAUDE.md").exists())
        self.assertFalse((self.target / "target.code-workspace").exists())
        self.assertIn("preserved observed state", warnings.getvalue())

    def test_target_replacement_after_preflight_cannot_receive_install(self) -> None:
        sentinel = self.target / "TASK.md"
        sentinel.write_bytes(b"original target\n")
        detached = self.target.parent / "detached-original"
        original_preflight = CLI_MODULE.preflight_install
        swapped = False
        warnings = io.StringIO()

        def replace_target_after_preflight(target, expected, handles=None):
            nonlocal swapped
            creates = original_preflight(target, expected, handles)
            target.rename(detached)
            target.mkdir()
            swapped = True
            return creates

        with (
            mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit),
            mock.patch.object(
                CLI_MODULE,
                "preflight_install",
                side_effect=replace_target_after_preflight,
            ),
            redirect_stderr(warnings),
        ):
            with self.assertRaisesRegex(
                CLI_MODULE.WarmbootError, "directory containment changed during install"
            ):
                CLI_MODULE.init_command(str(self.target), apply=True)

        self.assertTrue(swapped)
        self.assertEqual(list(self.target.iterdir()), [])
        self.assertEqual((detached / "TASK.md").read_bytes(), b"original target\n")
        self.assertFalse((detached / ".agent-warmboot").exists())
        self.assertFalse((detached / "AGENTS.md").exists())
        self.assertIn("preserved observed state", warnings.getvalue())

    def test_created_managed_root_replacement_is_not_adopted(self) -> None:
        managed = self.target / CLI_MODULE.MANAGED_DIR
        original_mkdir = CLI_MODULE.os.mkdir
        replacement_inode: int | None = None
        injected = False
        warnings = io.StringIO()

        def inject_final_after_staged_mkdir(path, *args, **kwargs):
            nonlocal replacement_inode, injected
            result = original_mkdir(path, *args, **kwargs)
            if str(path).startswith("..agent-warmboot.") and not injected:
                original_mkdir(CLI_MODULE.MANAGED_DIR, dir_fd=kwargs["dir_fd"])
                (managed / "replacement.txt").write_bytes(b"preserve replacement\n")
                replacement_inode = managed.stat().st_ino
                injected = True
            return result

        with (
            mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit),
            mock.patch.object(CLI_MODULE.os, "mkdir", side_effect=inject_final_after_staged_mkdir),
            redirect_stderr(warnings),
        ):
            with self.assertRaisesRegex(
                CLI_MODULE.WarmbootError,
                "could not publish created directory safely: .agent-warmboot",
            ):
                CLI_MODULE.init_command(str(self.target), apply=True)

        staged = list(self.target.glob("..agent-warmboot.*.create"))
        self.assertTrue(injected)
        self.assertEqual(managed.stat().st_ino, replacement_inode)
        self.assertEqual((managed / "replacement.txt").read_bytes(), b"preserve replacement\n")
        self.assertEqual(len(staged), 1)
        self.assertEqual(CLI_MODULE.stat.S_IMODE(staged[0].stat().st_mode), 0o700)
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertIn("staged directory publication is uncertain", warnings.getvalue())

    def test_staged_directory_fails_closed_when_no_replace_is_unavailable(self) -> None:
        parent = CLI_MODULE.open_directory_handle(self.target)
        warnings = io.StringIO()
        try:
            with (
                mock.patch.object(CLI_MODULE.sys, "platform", "unsupported-platform"),
                redirect_stderr(warnings),
            ):
                with self.assertRaisesRegex(
                    CLI_MODULE.WarmbootError,
                    "could not publish created directory safely: .agent-warmboot",
                ):
                    CLI_MODULE.create_staged_directory(
                        self.target,
                        CLI_MODULE.MANAGED_DIR,
                        parent,
                        CLI_MODULE.MANAGED_DIR,
                    )
        finally:
            CLI_MODULE.close_directory_handles([parent])

        staged = list(self.target.glob("..agent-warmboot.*.create"))
        self.assertEqual(len(staged), 1)
        self.assertFalse((self.target / CLI_MODULE.MANAGED_DIR).exists())
        self.assertIn("atomic no-replace rename is unavailable", warnings.getvalue())
        self.assertIn("preserved final/staged state", warnings.getvalue())

        with mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit):
            with self.assertRaisesRegex(
                CLI_MODULE.WarmbootError,
                "preserved staged path.*require inspection before install",
            ):
                CLI_MODULE.init_command(str(self.target), apply=True)
        checked = io.StringIO()
        with redirect_stdout(checked):
            self.assertEqual(CLI_MODULE.check_command(str(self.target)), 1)
        self.assertIn("preserved staged path(s) require inspection", checked.getvalue())

    def test_created_routes_replacement_is_not_adopted(self) -> None:
        original_mkdir = CLI_MODULE.os.mkdir
        replacement_inode: int | None = None
        injected = False
        warnings = io.StringIO()

        def inject_final_after_staged_mkdir(path, *args, **kwargs):
            nonlocal replacement_inode, injected
            result = original_mkdir(path, *args, **kwargs)
            if str(path).startswith(".routes.") and not injected:
                original_mkdir("routes", dir_fd=kwargs["dir_fd"])
                managed = self.target / CLI_MODULE.MANAGED_DIR
                routes = managed / "routes"
                (routes / "replacement.txt").write_bytes(b"preserve replacement\n")
                replacement_inode = routes.stat().st_ino
                injected = True
            return result

        with (
            mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit),
            mock.patch.object(CLI_MODULE.os, "mkdir", side_effect=inject_final_after_staged_mkdir),
            redirect_stderr(warnings),
        ):
            with self.assertRaisesRegex(
                CLI_MODULE.WarmbootError,
                "could not publish created directory safely: .agent-warmboot/routes",
            ):
                CLI_MODULE.init_command(str(self.target), apply=True)

        managed = self.target / CLI_MODULE.MANAGED_DIR
        routes = managed / "routes"
        self.assertTrue(injected)
        self.assertTrue(managed.is_dir())
        self.assertEqual(routes.stat().st_ino, replacement_inode)
        self.assertEqual(
            (routes / "replacement.txt").read_bytes(),
            b"preserve replacement\n",
        )
        staged = list(managed.glob(".routes.*.create"))
        self.assertEqual(len(staged), 1)
        self.assertEqual(CLI_MODULE.stat.S_IMODE(staged[0].stat().st_mode), 0o700)
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertIn("staged directory publication is uncertain", warnings.getvalue())
        self.assertIn("install stopped without rollback", warnings.getvalue())

    def test_created_managed_root_inspection_failure_is_reported_and_preserved(self) -> None:
        original_mkdir = CLI_MODULE.os.mkdir
        original_stat = CLI_MODULE.os.stat
        staged_name: str | None = None
        failed = False
        warnings = io.StringIO()

        def record_mkdir(path, *args, **kwargs):
            nonlocal staged_name
            result = original_mkdir(path, *args, **kwargs)
            if str(path).startswith("..agent-warmboot."):
                staged_name = str(path)
            return result

        def fail_created_stat(path, *args, **kwargs):
            nonlocal failed
            if path == staged_name and kwargs.get("dir_fd") is not None and not failed:
                failed = True
                raise OSError("injected managed identity failure")
            return original_stat(path, *args, **kwargs)

        with (
            mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit),
            mock.patch.object(CLI_MODULE.os, "mkdir", side_effect=record_mkdir),
            mock.patch.object(CLI_MODULE.os, "stat", side_effect=fail_created_stat),
            redirect_stderr(warnings),
        ):
            with self.assertRaisesRegex(
                CLI_MODULE.WarmbootError,
                "could not publish created directory safely: .agent-warmboot",
            ):
                CLI_MODULE.init_command(str(self.target), apply=True)

        self.assertTrue(failed)
        staged = list(self.target.glob("..agent-warmboot.*.create"))
        self.assertEqual(len(staged), 1)
        self.assertEqual(CLI_MODULE.stat.S_IMODE(staged[0].stat().st_mode), 0o700)
        self.assertFalse((self.target / CLI_MODULE.MANAGED_DIR).exists())
        self.assertIn("injected managed identity failure", warnings.getvalue())
        self.assertIn("preserved final/staged state", warnings.getvalue())

    def test_created_routes_inspection_failure_is_reported_and_preserved(self) -> None:
        original_mkdir = CLI_MODULE.os.mkdir
        original_stat = CLI_MODULE.os.stat
        staged_name: str | None = None
        failed = False
        warnings = io.StringIO()

        def record_mkdir(path, *args, **kwargs):
            nonlocal staged_name
            result = original_mkdir(path, *args, **kwargs)
            if str(path).startswith(".routes."):
                staged_name = str(path)
            return result

        def fail_created_stat(path, *args, **kwargs):
            nonlocal failed
            if path == staged_name and kwargs.get("dir_fd") is not None and not failed:
                failed = True
                raise OSError("injected routes identity failure")
            return original_stat(path, *args, **kwargs)

        with (
            mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit),
            mock.patch.object(CLI_MODULE.os, "mkdir", side_effect=record_mkdir),
            mock.patch.object(CLI_MODULE.os, "stat", side_effect=fail_created_stat),
            redirect_stderr(warnings),
        ):
            with self.assertRaisesRegex(
                CLI_MODULE.WarmbootError,
                "could not publish created directory safely: .agent-warmboot/routes",
            ):
                CLI_MODULE.init_command(str(self.target), apply=True)

        managed = self.target / CLI_MODULE.MANAGED_DIR
        self.assertTrue(failed)
        self.assertTrue(managed.is_dir())
        staged = list(managed.glob(".routes.*.create"))
        self.assertEqual(len(staged), 1)
        self.assertEqual(CLI_MODULE.stat.S_IMODE(staged[0].stat().st_mode), 0o700)
        self.assertFalse((managed / "routes").exists())
        self.assertIn("injected routes identity failure", warnings.getvalue())
        self.assertIn("preserved final/staged state", warnings.getvalue())
        self.assertIn("install stopped without rollback", warnings.getvalue())

    def test_existing_leaf_symlink_swap_after_preflight_prevents_applied(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        (self.target / "CLAUDE.md").unlink()
        outside = self.target.parent / "outside-loader.md"
        outside.write_bytes(b"outside\n")
        original_preflight = CLI_MODULE.preflight_install
        swapped = False
        warnings = io.StringIO()

        def swap_loader_after_preflight(target, expected, handles=None):
            nonlocal swapped
            creates = original_preflight(target, expected, handles)
            agents = target / "AGENTS.md"
            agents.unlink()
            agents.symlink_to(outside)
            swapped = True
            return creates

        with (
            mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit),
            mock.patch.object(
                CLI_MODULE,
                "preflight_install",
                side_effect=swap_loader_after_preflight,
            ),
            redirect_stderr(warnings),
        ):
            with self.assertRaisesRegex(
                CLI_MODULE.WarmbootError, "install result changed before completion"
            ):
                CLI_MODULE.init_command(str(self.target), apply=True)

        self.assertTrue(swapped)
        self.assertTrue((self.target / "AGENTS.md").is_symlink())
        self.assertEqual(outside.read_bytes(), b"outside\n")
        self.assertEqual(
            (self.target / "CLAUDE.md").read_bytes(), CLI_MODULE.LOADER.encode("utf-8")
        )
        self.assertIn(str(self.target / "CLAUDE.md"), warnings.getvalue())
        rerun = self.apply()
        self.assertNotEqual(rerun.returncode, 0)
        self.assertIn("AGENTS.md is a symlink", rerun.stderr)
        self.assertTrue((self.target / "AGENTS.md").is_symlink())

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO creation is unavailable")
    def test_preflight_fifo_swap_is_rejected_without_blocking(self) -> None:
        agents = self.target / "AGENTS.md"
        agents.write_bytes(CLI_MODULE.LOADER.encode("utf-8"))
        original_open = CLI_MODULE.os.open
        swapped = False

        def swap_to_fifo_before_open(path, flags, *args, **kwargs):
            nonlocal swapped
            if path == "AGENTS.md" and kwargs.get("dir_fd") is not None and not swapped:
                agents.unlink()
                os.mkfifo(agents)
                swapped = True
            return original_open(path, flags, *args, **kwargs)

        with (
            mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit),
            mock.patch.object(CLI_MODULE.os, "open", side_effect=swap_to_fifo_before_open),
        ):
            with self.assertRaisesRegex(CLI_MODULE.WarmbootError, "file changed"):
                CLI_MODULE.init_command(str(self.target), apply=True)

        self.assertTrue(swapped)
        self.assertTrue(CLI_MODULE.stat.S_ISFIFO(agents.stat(follow_symlinks=False).st_mode))
        self.assertFalse((self.target / ".agent-warmboot").exists())

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO creation is unavailable")
    def test_check_fifo_swap_is_rejected_without_pass(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        agents = self.target.resolve() / "AGENTS.md"
        original_open = CLI_MODULE.os.open
        swapped = False

        def swap_to_fifo_before_open(path, flags, *args, **kwargs):
            nonlocal swapped
            if path == "AGENTS.md" and kwargs.get("dir_fd") is not None and not swapped:
                agents.unlink()
                os.mkfifo(agents)
                swapped = True
            return original_open(path, flags, *args, **kwargs)

        with mock.patch.object(CLI_MODULE.os, "open", side_effect=swap_to_fifo_before_open):
            with self.assertRaisesRegex(CLI_MODULE.WarmbootError, "file changed"):
                CLI_MODULE.check_command(str(self.target))

        self.assertTrue(swapped)
        self.assertTrue(CLI_MODULE.stat.S_ISFIFO(agents.stat(follow_symlinks=False).st_mode))

    def test_atomic_create_uses_final_name_without_any_delete_boundary(self) -> None:
        destination = self.target / "direct-final.txt"

        with (
            mock.patch.object(
                CLI_MODULE.os, "unlink", side_effect=AssertionError("unlink forbidden")
            ) as unlink,
            mock.patch.object(
                CLI_MODULE.os, "rmdir", side_effect=AssertionError("rmdir forbidden")
            ) as rmdir,
        ):
            receipt = CLI_MODULE.atomic_create(destination, b"direct content\n")

        self.assertEqual(receipt.path, destination)
        self.assertEqual(receipt.inode, destination.stat().st_ino)
        self.assertEqual(destination.read_bytes(), b"direct content\n")
        self.assertEqual(list(self.target.iterdir()), [destination])
        unlink.assert_not_called()
        rmdir.assert_not_called()

    def test_atomic_create_never_overwrites_an_existing_final_path(self) -> None:
        destination = self.target / "existing-final.txt"
        destination.write_bytes(b"concurrent content\n")

        with self.assertRaisesRegex(
            CLI_MODULE.WarmbootError, "destination appeared during install"
        ):
            CLI_MODULE.atomic_create(destination, b"managed content\n")

        self.assertEqual(destination.read_bytes(), b"concurrent content\n")

    def test_atomic_create_preserves_final_file_after_receipt_failure(self) -> None:
        destination = self.target / "receipt-failure.txt"
        warnings = io.StringIO()

        with (
            mock.patch.object(
                CLI_MODULE, "sha256", side_effect=OSError("injected receipt hash failure")
            ),
            mock.patch.object(
                CLI_MODULE.os, "unlink", side_effect=AssertionError("unlink forbidden")
            ) as unlink,
            mock.patch.object(
                CLI_MODULE.os, "rmdir", side_effect=AssertionError("rmdir forbidden")
            ) as rmdir,
            redirect_stderr(warnings),
        ):
            with self.assertRaisesRegex(OSError, "injected receipt hash failure"):
                CLI_MODULE.atomic_create(destination, b"new content\n")

        self.assertEqual(destination.read_bytes(), b"new content\n")
        self.assertIn(str(destination), warnings.getvalue())
        self.assertIn("preserved the final path without cleanup", warnings.getvalue())
        unlink.assert_not_called()
        rmdir.assert_not_called()

    def test_atomic_create_preserves_replacement_after_postflight_failure(self) -> None:
        destination = self.target / "replaced-before-receipt.txt"
        original_stat = CLI_MODULE.os.stat
        replaced = False
        warnings = io.StringIO()

        def replace_then_fail(path, *args, **kwargs):
            nonlocal replaced
            result = original_stat(path, *args, **kwargs)
            if path == destination.name and kwargs.get("dir_fd") is not None and not replaced:
                destination.unlink()
                destination.write_bytes(b"replacement content\n")
                replaced = True
                raise OSError("injected receipt stat failure")
            return result

        with (
            mock.patch.object(CLI_MODULE.os, "stat", new=replace_then_fail),
            redirect_stderr(warnings),
        ):
            with self.assertRaisesRegex(OSError, "injected receipt stat failure"):
                CLI_MODULE.atomic_create(destination, b"original content\n")

        self.assertTrue(replaced)
        self.assertEqual(destination.read_bytes(), b"replacement content\n")
        self.assertIn("preserved the final path without cleanup", warnings.getvalue())

    def test_atomic_create_preserves_modified_inode_after_postflight_failure(self) -> None:
        destination = self.target / "modified-before-receipt.txt"
        original_stat = CLI_MODULE.os.stat
        modified_inode: int | None = None
        warnings = io.StringIO()

        def modify_then_fail(path, *args, **kwargs):
            nonlocal modified_inode
            result = original_stat(path, *args, **kwargs)
            if (
                path == destination.name
                and kwargs.get("dir_fd") is not None
                and modified_inode is None
            ):
                modified_inode = result.st_ino
                destination.write_bytes(b"modified content\n")
                raise OSError("injected receipt stat failure")
            return result

        with (
            mock.patch.object(CLI_MODULE.os, "stat", new=modify_then_fail),
            redirect_stderr(warnings),
        ):
            with self.assertRaisesRegex(OSError, "injected receipt stat failure"):
                CLI_MODULE.atomic_create(destination, b"original content\n")

        self.assertIsNotNone(modified_inode)
        self.assertEqual(destination.stat().st_ino, modified_inode)
        self.assertEqual(destination.read_bytes(), b"modified content\n")
        self.assertIn("preserved the final path without cleanup", warnings.getvalue())

    def test_partial_final_file_is_preserved_without_delete_and_blocks_rerun(self) -> None:
        original_write = CLI_MODULE.os.write
        write_calls = 0
        warnings = io.StringIO()
        output = io.StringIO()

        def fail_after_partial_write(descriptor, data):
            nonlocal write_calls
            write_calls += 1
            if write_calls == 1:
                return original_write(descriptor, data[:1])
            raise OSError("injected write failure")

        with (
            mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit),
            mock.patch.object(CLI_MODULE.os, "write", side_effect=fail_after_partial_write),
            mock.patch.object(
                CLI_MODULE.os, "unlink", side_effect=AssertionError("unlink forbidden")
            ) as unlink,
            mock.patch.object(
                CLI_MODULE.os, "rmdir", side_effect=AssertionError("rmdir forbidden")
            ) as rmdir,
            redirect_stderr(warnings),
            redirect_stdout(output),
        ):
            with self.assertRaisesRegex(OSError, "injected write failure"):
                CLI_MODULE.init_command(str(self.target), apply=True)

        partial = self.target / ".agent-warmboot" / "core.md"
        self.assertEqual(partial.read_bytes(), b"#")
        self.assertTrue((self.target / ".agent-warmboot" / "routes").is_dir())
        self.assertIn(str(partial), warnings.getvalue())
        self.assertIn("preserved the final path without cleanup", warnings.getvalue())
        self.assertNotIn("APPLIED", output.getvalue())
        unlink.assert_not_called()
        rmdir.assert_not_called()

        with mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit):
            with self.assertRaisesRegex(
                CLI_MODULE.WarmbootError,
                r"\.agent-warmboot/core\.md differs from the managed content",
            ):
                CLI_MODULE.init_command(str(self.target), apply=True)
        self.assertEqual(partial.read_bytes(), b"#")
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_install_source_has_no_destructive_cleanup_path(self) -> None:
        source = SOURCE_SCRIPT.read_text(encoding="utf-8")

        self.assertNotIn("os.unlink(", source)
        self.assertNotIn("os.rmdir(", source)
        self.assertNotIn("def rollback_", source)
        self.assertNotIn("Quarantine", source)
        self.assertNotIn(".tmp", source)

    def test_check_detects_tampering(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        (self.target / ".agent-warmboot" / "core.md").write_text("# Tampered\n", encoding="utf-8")
        result = self.run_cli("check", str(self.target))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("content/hash mismatch", result.stdout)

    def test_late_parent_rename_preserves_inode_and_warns_paths_may_have_moved(self) -> None:
        # Earlier swap tests run before atomic_create's validation. This chooses the
        # later syscall window, proving the warning rather than promising containment
        # across hostile renames. Real descriptor-relative creation remains in use.
        managed = self.target.resolve() / ".agent-warmboot"
        moved = self.target.resolve().parent / "moved-original"
        original_open = os.open
        original_identity = None
        injected = False

        def move_before_create(name, flags, *args, **kwargs):
            nonlocal original_identity, injected
            if name == "core.md" and flags & os.O_CREAT and not injected:
                identity = managed.stat()
                original_identity = (identity.st_dev, identity.st_ino)
                managed.rename(moved)
                managed.mkdir()
                injected = True
            return original_open(name, flags, *args, **kwargs)

        output, warnings = io.StringIO(), io.StringIO()
        with (
            mock.patch.object(CLI_MODULE, "toolkit_root", return_value=self.toolkit),
            mock.patch.object(CLI_MODULE.os, "open", side_effect=move_before_create),
            redirect_stdout(output),
            redirect_stderr(warnings),
        ):
            result = CLI_MODULE.main(["init", str(self.target), "--apply"])

        self.assertTrue(injected)
        self.assertEqual(result, 1)
        self.assertNotIn("APPLIED", output.getvalue())
        self.assertEqual(original_identity, (moved.stat().st_dev, moved.stat().st_ino))
        self.assertEqual(list(managed.iterdir()), [])
        # This outside write is the preserved limitation, not behavior being fixed.
        self.assertEqual((moved / "core.md").read_bytes(), b"# Test core\n")
        self.assertIn("preservation", warnings.getvalue())
        self.assertIn("recorded paths may have moved", warnings.getvalue())

    def test_check_rejects_unrepresentable_manifest_paths_without_mutation(self) -> None:
        """Malformed route keys must reach controlled validation, not host I/O.

        Existing route directories prevent a missing parent from masking NUL or
        encoding failures. This checks local rejection, not every host filesystem.
        """
        self.assertEqual(self.apply().returncode, 0)
        manifest_path = self.target / ".agent-warmboot" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for name in ("nul\x00.md", "unencodable\ud800.md"):
            with self.subTest(name=repr(name)):
                malformed = dict(manifest, files=dict(manifest["files"]))
                malformed["files"][f".agent-warmboot/routes/{name}"] = "0" * 64
                manifest_path.write_text(json.dumps(malformed) + "\n", encoding="utf-8")
                before = {
                    path.relative_to(self.target): path.read_bytes()
                    for path in self.target.rglob("*")
                    if path.is_file()
                }
                result = self.run_cli("check", str(self.target))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("invalid managed file entry", result.stdout)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(
                    {
                        path.relative_to(self.target): path.read_bytes()
                        for path in self.target.rglob("*")
                        if path.is_file()
                    },
                    before,
                )

    def test_check_preserves_host_representable_manifest_paths(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        manifest_path = self.target / ".agent-warmboot" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        relative = ".agent-warmboot/routes/café.md"
        content = b"# Host-representable route\n"
        (self.target / relative).write_bytes(content)
        manifest["files"][relative] = hashlib.sha256(content).hexdigest()
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        result = self.run_cli("check", str(self.target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("manifest-declared content and structure matched", result.stdout)

    def test_check_reports_surrogateescape_path_on_strict_utf8_stdout(self) -> None:
        """Encoding acceptance does not promise the filesystem can store the name.

        An absent surrogateescape route exercises controlled inspection failure and
        strict-output diagnostics without creating host-forbidden filename bytes.
        """
        self.assertEqual(self.apply().returncode, 0)
        manifest_path = self.target / ".agent-warmboot" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        relative = ".agent-warmboot/routes/" + os.fsdecode(b"escaped-\xff.md")
        manifest["files"][relative] = "0" * 64
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        before = {
            path.relative_to(self.target): path.read_bytes()
            for path in self.target.rglob("*")
            if path.is_file()
        }
        result = subprocess.run(
            [sys.executable, "-B", str(self.script), "check", str(self.target)],
            env={**os.environ, "PYTHONIOENCODING": "utf-8:strict"},
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("invalid managed file entry", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("escaped-", result.stdout)
        self.assertEqual(
            {
                path.relative_to(self.target): path.read_bytes()
                for path in self.target.rglob("*")
                if path.is_file()
            },
            before,
        )

    def test_check_detects_missing_and_extra_managed_routes(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        routes = self.target / ".agent-warmboot" / "routes"
        (routes / "extra.md").write_text("# Extra\n", encoding="utf-8")
        (routes / "review.md").unlink()
        result = self.run_cli("check", str(self.target))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected managed path(s): .agent-warmboot/routes/extra.md", result.stdout)
        self.assertIn("missing managed path(s): .agent-warmboot/routes/review.md", result.stdout)

    def test_check_reports_unexpected_manifest_entry_without_opening_it(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        unmanaged = self.target / "unmanaged.txt"
        sentinel = b"harmless project-owned content\n"
        unmanaged.write_bytes(sentinel)
        manifest_path = self.target / ".agent-warmboot" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        # A correct hash makes allowlist membership, not a content mismatch, the
        # reason for refusal. Observe real os.open without replacing filesystem I/O.
        manifest["files"]["unmanaged.txt"] = hashlib.sha256(sentinel).hexdigest()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        before = {
            path.relative_to(self.target): path.read_bytes()
            for path in self.target.rglob("*")
            if path.is_file()
        }
        output = io.StringIO()
        with (
            mock.patch.object(CLI_MODULE.os, "open", wraps=os.open) as opened,
            redirect_stdout(output),
        ):
            result = CLI_MODULE.main(["check", str(self.target)])

        self.assertEqual(result, 1)
        self.assertIn("unexpected entries: unmanaged.txt", output.getvalue())
        self.assertFalse(any(call.args[0] == "unmanaged.txt" for call in opened.call_args_list))
        self.assertEqual(
            before,
            {
                path.relative_to(self.target): path.read_bytes()
                for path in self.target.rglob("*")
                if path.is_file()
            },
        )

    # Each pair is a raw name tail and the escaped form the output must show instead:
    # a newline that would start a forged line, and a carriage return plus a terminal
    # erase-line sequence that would visually overwrite the real line on a terminal.
    FORGED_TAILS = (
        ("\nPASS forged", "\\nPASS forged"),
        ("\r\x1b[2KPASS forged", "\\r\\x1b[2KPASS forged"),
    )

    def assert_output_lines_are_unforgeable(
        self, output: str, first_word: str, *escaped_lines: str
    ) -> None:
        """Every line stays printable, so no raw name can start or overwrite a line."""
        self.assertTrue(output.startswith(first_word), ascii(output))
        lines = output.split("\n")
        self.assertEqual(lines[-1], "", ascii(output))
        self.assertTrue(all(line.isprintable() for line in lines), ascii(output))
        self.assertFalse(
            [line for line in output.splitlines() if line.startswith(("PASS", "APPLIED"))],
            ascii(output),
        )
        for line in escaped_lines:
            self.assertIn(line, lines, ascii(output))

    def test_printable_path_escapes_only_what_could_forge_or_blur_a_line(self) -> None:
        cases = {
            ".agent-warmboot/routes/café.md": ".agent-warmboot/routes/café.md",
            "a\nb": "a\\nb",
            "a\rb": "a\\rb",
            "a\tb": "a\\tb",
            "a\x1b[2Kb": "a\\x1b[2Kb",
            "a\x85b": "a\\x85b",
            "a b": "a\\u2028b",
            "a" + os.fsdecode(b"\xff") + "b": "a\\udcffb",
            # A literal backslash is doubled, so it never reads like an escape.
            "a\\nb": "a\\\\nb",
        }
        for raw, shown in cases.items():
            with self.subTest(raw=ascii(raw)):
                self.assertEqual(CLI_MODULE.printable_path(raw), shown)
                self.assertTrue(CLI_MODULE.printable_path(raw).isprintable())
        self.assertEqual(CLI_MODULE.printable_path(Path("/tmp") / "x\ny"), "/tmp/x\\ny")

    def test_check_output_cannot_be_forged_by_a_newline_in_a_manifest_key(self) -> None:
        """A manifest key is printed escaped in every failure family that carries it."""
        self.assertEqual(self.apply().returncode, 0)
        manifest_path = self.target / ".agent-warmboot" / "manifest.json"
        original = json.loads(manifest_path.read_text(encoding="utf-8"))
        tails = (
            (
                "\nPASS " + str(self.target) + ": forged",
                "\\nPASS " + str(self.target) + ": forged",
            ),
            *self.FORGED_TAILS,
        )
        for raw, escaped in tails:
            with self.subTest(tail=ascii(raw)):
                # The key's parent is not the routes directory, so it is both an
                # unexpected manifest entry and a missing managed path.
                manifest = dict(original, files=dict(original["files"]))
                manifest["files"][".agent-warmboot/routes/x.md" + raw] = "0" * 64
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

                result = self.run_cli("check", str(self.target))

                self.assertEqual(result.returncode, 1, ascii(result.stdout + result.stderr))
                shown = ".agent-warmboot/routes/x.md" + escaped
                self.assert_output_lines_are_unforgeable(
                    result.stdout,
                    "FAIL ",
                    f"- .agent-warmboot/manifest.json: unexpected entries: {shown}",
                    f"- missing managed path(s): {shown}",
                )

    def test_check_escapes_manifest_route_keys_in_missing_path_failures(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        manifest_path = self.target / ".agent-warmboot" / "manifest.json"
        original = json.loads(manifest_path.read_text(encoding="utf-8"))
        for raw, escaped in self.FORGED_TAILS:
            with self.subTest(tail=ascii(raw)):
                # A declared route that is absent reaches both the structure and the
                # per-file content failure.
                manifest = dict(original, files=dict(original["files"]))
                manifest["files"][f".agent-warmboot/routes/x{raw}.md"] = "0" * 64
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

                result = self.run_cli("check", str(self.target))

                self.assertEqual(result.returncode, 1, ascii(result.stdout + result.stderr))
                shown = f".agent-warmboot/routes/x{escaped}.md"
                self.assert_output_lines_are_unforgeable(
                    result.stdout,
                    "FAIL ",
                    f"- missing managed path(s): {shown}",
                    f"- {shown}: missing or not a regular file",
                )

    def test_check_escapes_filesystem_names_in_unexpected_managed_paths(self) -> None:
        self.assertEqual(self.apply().returncode, 0)
        managed = self.target / ".agent-warmboot"
        for raw, escaped in self.FORGED_TAILS:
            with self.subTest(tail=ascii(raw)):
                (managed / f"x{raw}").write_text("planted\n", encoding="utf-8")
                (managed / f"d{raw}").mkdir()
                try:
                    result = self.run_cli("check", str(self.target))
                finally:
                    (managed / f"x{raw}").unlink()
                    (managed / f"d{raw}").rmdir()

                self.assertEqual(result.returncode, 1, ascii(result.stdout + result.stderr))
                self.assert_output_lines_are_unforgeable(
                    result.stdout,
                    "FAIL ",
                    f"- unexpected managed path(s): .agent-warmboot/x{escaped}",
                    f"- unexpected managed directory(s): .agent-warmboot/d{escaped}",
                )

    def test_check_escapes_the_target_path_in_its_verdict_line(self) -> None:
        for index, (raw, escaped) in enumerate(self.FORGED_TAILS):
            with self.subTest(tail=ascii(raw)):
                target = Path(self.temporary.name) / f"t{index}{raw}"
                target.mkdir()
                applied = self.run_cli("init", str(target), "--apply")
                self.assertEqual(applied.returncode, 0, ascii(applied.stdout + applied.stderr))
                (target / ".agent-warmboot" / "routes" / "review.md").unlink()

                result = self.run_cli("check", str(target))

                self.assertEqual(result.returncode, 1, ascii(result.stdout + result.stderr))
                self.assert_output_lines_are_unforgeable(
                    result.stdout,
                    "FAIL ",
                    f"FAIL {target.parent.resolve()}/t{index}{escaped}",
                )

    def test_init_escapes_filesystem_and_route_names_in_output(self) -> None:
        for raw, escaped in self.FORGED_TAILS:
            with self.subTest(tail=ascii(raw), command="refused apply"):
                planted = self.target / ".agent-warmboot" / f"x{raw}"
                planted.parent.mkdir(exist_ok=True)
                planted.write_text("planted\n", encoding="utf-8")
                try:
                    result = self.apply()
                finally:
                    planted.unlink()

                self.assertEqual(result.returncode, 1, ascii(result.stdout + result.stderr))
                self.assertEqual(result.stdout, "")
                self.assertFalse((self.target / "AGENTS.md").exists())
                self.assert_output_lines_are_unforgeable(
                    result.stderr,
                    "FAIL: ",
                    f"FAIL: unexpected managed path(s): .agent-warmboot/x{escaped}",
                )
        (self.target / ".agent-warmboot").rmdir()

        for raw, escaped in self.FORGED_TAILS:
            with self.subTest(tail=ascii(raw), command="preview"):
                route = self.toolkit / "routes" / f"x{raw}.md"
                route.write_text("# Planted route\n", encoding="utf-8")
                try:
                    result = self.run_cli("init", str(self.target))
                finally:
                    route.unlink()

                self.assertEqual(result.returncode, 0, ascii(result.stdout + result.stderr))
                self.assertEqual(list(self.target.iterdir()), [])
                self.assert_output_lines_are_unforgeable(
                    result.stdout,
                    "PREVIEW ",
                    f"CREATE-FILE .agent-warmboot/routes/x{escaped}.md",
                )

    def test_relative_target_is_refused(self) -> None:
        result = self.run_cli("init", "target", "--apply", cwd=Path(self.temporary.name))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be absolute", result.stderr)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_existing_task_file_is_preserved(self) -> None:
        task = self.target / "TASK.md"
        task.write_text("keep this task\n", encoding="utf-8")
        result = self.apply()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(task.read_text(encoding="utf-8"), "keep this task\n")
        self.assertFalse((self.target / "HANDOFF.md").exists())


if __name__ == "__main__":
    unittest.main()
