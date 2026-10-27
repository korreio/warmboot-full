"""Exercise the compact upgrade-oracle fail-closed fixture boundary."""

import contextlib
import copy
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path

from acceptance.release_manifest import (
    ReleaseManifestVerificationError,
    selected_records,
    verify_illustrative_manifest,
    verify_release_manifest,
)
from acceptance.unicode_policy import (
    NON_MARKDOWN_LINE_SEPARATORS,
    is_default_ignorable_code_point,
    is_synthetic_ignorable,
    is_unsafe_evidence_character,
    nfkc_casefold,
)
from acceptance.upgrade_oracle import (
    DISPOSITIONS,
    ROLLBACK_SCOPE,
    UpgradeVerificationError,
    _member,
    main,
    parse_upgrade_record,
    preflight,
    release_note_summary_classification,
    resumer_receipt,
    verify,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "acceptance" / "fixtures" / "upgrade-package"
# Consolidated Unicode-derived reference data; Unicode-3.0 terms: root NOTICE.
EXPECTED_DEFAULT_IGNORABLE_RANGES = (
    (0x00AD, 0x00AD),
    (0x034F, 0x034F),
    (0x061C, 0x061C),
    (0x115F, 0x1160),
    (0x17B4, 0x17B5),
    (0x180B, 0x180F),
    (0x200B, 0x200F),
    (0x202A, 0x202E),
    (0x2060, 0x206F),
    (0x3164, 0x3164),
    (0xFE00, 0xFE0F),
    (0xFEFF, 0xFEFF),
    (0xFFA0, 0xFFA0),
    (0xFFF0, 0xFFF8),
    (0x1BCA0, 0x1BCA3),
    (0x1D173, 0x1D17A),
    (0xE0000, 0xE0FFF),
)


def _expected_default_ignorable(codepoint: int) -> bool:
    return any(start <= codepoint <= end for start, end in EXPECTED_DEFAULT_IGNORABLE_RANGES)


def _fullwidth_ascii(value: str) -> str:
    return "".join(
        chr(ord(character) + 0xFEE0) if "!" <= character <= "~" else character
        for character in value
    )


def _record(package: Path = FIXTURE) -> str:
    return (package / "UPGRADE.md").read_text(encoding="utf-8")


def _rebind_target(package: Path) -> None:
    workspace_path = package / "consumer.code-workspace"
    workspace_sha = hashlib.sha256(workspace_path.read_bytes()).hexdigest()

    authorities_path = package / "native-authorities.json"
    authorities = json.loads(authorities_path.read_text(encoding="utf-8"))
    workspace_authority = next(
        item for item in authorities["authorities"] if item["role"] == "WORKSPACE"
    )
    workspace_authority["sha256"] = workspace_sha
    authorities_path.write_text(json.dumps(authorities, indent=2) + "\n", encoding="utf-8")
    target_sha = hashlib.sha256(authorities_path.read_bytes()).hexdigest()

    adoption_path = package / "adoption-receipt.json"
    adoption = json.loads(adoption_path.read_text(encoding="utf-8"))
    adoption["target_identity"] = target_sha
    adoption_path.write_text(json.dumps(adoption, indent=2) + "\n", encoding="utf-8")

    request_path = package / "request.json"
    request = json.loads(request_path.read_text(encoding="utf-8"))
    request["target"].update(
        {
            "identity": target_sha,
            "native_authorities_sha256": target_sha,
            "adoption_receipt_sha256": hashlib.sha256(adoption_path.read_bytes()).hexdigest(),
            "workspace_sha256": workspace_sha,
        }
    )
    request_path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")


def _rebind_release_notes(package: Path, release: str) -> None:
    request_path = package / "request.json"
    request = json.loads(request_path.read_text(encoding="utf-8"))
    notes_path = package / request[release]["release_notes_path"]
    request[release]["release_notes_sha256"] = hashlib.sha256(notes_path.read_bytes()).hexdigest()
    request_path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")


class UpgradeOracleTests(unittest.TestCase):
    def test_accepts_compact_agent_owned_planning_record(self) -> None:
        text = _record()
        verify(FIXTURE, text)
        parsed = parse_upgrade_record(text)
        self.assertEqual(len(parsed["safety"]), 11)
        self.assertEqual(parsed["safety"]["verdict"], "BLOCKED_BEFORE_MUTATION")
        self.assertFalse(parsed["safety"]["may_edit"])
        self.assertEqual(set(parsed["dispositions"]), {"U01", "U02", "U03"})
        self.assertNotIn("U04", parsed["dispositions"])

    def test_preserves_exact_destinations_and_inspected_only_u04(self) -> None:
        parsed = parse_upgrade_record(_record())
        self.assertEqual(
            {
                change: (row["disposition"], row["destination"])
                for change, row in parsed["dispositions"].items()
            },
            DISPOSITIONS,
        )
        self.assertIn("U04", parsed["text"])
        self.assertIn("no target disposition", parsed["text"])
        self.assertNotIn("U05", parsed["text"])

    def test_preflight_binds_compact_releases_workspace_dirt_and_adoption(self) -> None:
        context = preflight(FIXTURE)
        self.assertEqual(
            context["old"],
            "agent-warmboot-v1.0.0@1111111111111111111111111111111111111111#"
            "5a26cdf7cc41f665d76ab13f490c712f51bf8235bfb5541b3f4651f1610ca963",
        )
        self.assertEqual(
            context["new"],
            "agent-warmboot-v2.0.0@2222222222222222222222222222222222222222#"
            "e1ee2316ed120251fb7129fe05ccaa83c8851022a9d6c59a17163da98d9ade6a",
        )
        self.assertEqual(context["target"]["workspace_path"], "consumer.code-workspace")
        self.assertEqual(
            {item["path"] for item in context["target"]["dirt"]},
            {"notes/unrelated-owner.txt", "scratch/local-analysis.txt"},
        )

    def test_upgrade_role_identities_reject_padding_or_synthetic_ignorables(self) -> None:
        """Every raw request role is canonical and excludes DICP/runtime-Cf controls."""
        roles = (
            "coordinator",
            "git_holder",
            "warmboot_release_holder",
            "challenger",
        )
        mutations = (
            ("padded", lambda value: f" {value} ", "canonical non-empty"),
            ("CGJ", lambda value: f"{value}\u034f", "synthetic Unicode ignorables"),
            ("runtime Cf", lambda value: f"{value}\u0600", "synthetic Unicode ignorables"),
        )
        for role in roles:
            for name, mutate, error in mutations:
                with (
                    self.subTest(role=role, mutation=name),
                    tempfile.TemporaryDirectory() as directory,
                ):
                    package = Path(directory) / "package"
                    shutil.copytree(FIXTURE, package)
                    path = package / "request.json"
                    request = json.loads(path.read_text(encoding="utf-8"))
                    request[role] = mutate(request[role])
                    path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
                    with self.assertRaisesRegex(UpgradeVerificationError, error):
                        preflight(package)

        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(FIXTURE, package)
            path = package / "request.json"
            request = json.loads(path.read_text(encoding="utf-8"))
            request["objective"] += "\u034f"
            path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
            preflight(package)

        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(FIXTURE, package)
            path = package / "request.json"
            request = json.loads(path.read_text(encoding="utf-8"))
            request["objective"] = f" {request['objective']} "
            path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(UpgradeVerificationError, "objective.*canonical"):
                preflight(package)

    def test_upgrade_role_alias_keys_enforce_sameness_and_independence(self) -> None:
        """Compatibility aliases preserve sameness but cannot manufacture independence."""
        sameness_cases = (
            ("coordinator case", "coordinator", str.upper),
            ("coordinator fullwidth", "coordinator", _fullwidth_ascii),
            ("Git case", "git_holder", str.upper),
            ("Git fullwidth", "git_holder", _fullwidth_ascii),
            ("release distinct case", "warmboot_release_holder", str.upper),
            ("release distinct fullwidth", "warmboot_release_holder", _fullwidth_ascii),
            ("challenger distinct case", "challenger", str.upper),
            ("challenger distinct fullwidth", "challenger", _fullwidth_ascii),
        )
        for name, role, transform in sameness_cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                path = package / "request.json"
                request = json.loads(path.read_text(encoding="utf-8"))
                request[role] = transform(request[role])
                path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
                preflight(package)

        independence_cases = (
            ("release case-aliases Git", "git_holder", str.upper),
            ("release fullwidth-aliases Git", "git_holder", _fullwidth_ascii),
            ("release case-aliases challenger", "challenger", str.upper),
            ("release fullwidth-aliases challenger", "challenger", _fullwidth_ascii),
        )
        for name, source_role, transform in independence_cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                path = package / "request.json"
                request = json.loads(path.read_text(encoding="utf-8"))
                request["warmboot_release_holder"] = transform(request[source_role])
                path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
                with self.assertRaisesRegex(UpgradeVerificationError, "independence"):
                    preflight(package)

        challenger_aliases = (
            ("exact", lambda value: value),
            ("case", str.upper),
            ("fullwidth", _fullwidth_ascii),
        )
        for name, transform in challenger_aliases:
            with self.subTest(challenger_alias=name), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                path = package / "request.json"
                request = json.loads(path.read_text(encoding="utf-8"))
                request["challenger"] = transform(request["coordinator"])
                path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
                with self.assertRaisesRegex(
                    UpgradeVerificationError, "challenger must be distinct"
                ):
                    preflight(package)

    def test_unsafe_unicode_evidence_characters_reject_identity_and_summary(self) -> None:
        """Unsafe Unicode categories fail before identity keys or summary views."""
        unsafe = ("\x00", "\x07", "\x7f", "\x85", "\ud800", "\ue000", "\u0378")
        for role in (
            "coordinator",
            "git_holder",
            "warmboot_release_holder",
            "challenger",
        ):
            for character in unsafe:
                with (
                    self.subTest(role=role, codepoint=f"U+{ord(character):04X}"),
                    tempfile.TemporaryDirectory() as directory,
                ):
                    package = Path(directory) / "package"
                    shutil.copytree(FIXTURE, package)
                    request_path = package / "request.json"
                    request = json.loads(request_path.read_text(encoding="utf-8"))
                    request[role] = f"{request[role]}{character}unsafe"
                    request_path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
                    with self.assertRaisesRegex(
                        UpgradeVerificationError,
                        "unsafe Unicode evidence characters",
                    ):
                        preflight(package)

        for character in unsafe:
            with (
                self.subTest(native_owner=f"U+{ord(character):04X}"),
                tempfile.TemporaryDirectory() as directory,
            ):
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                path = package / "native-authorities.json"
                inventory = json.loads(path.read_text(encoding="utf-8"))
                inventory["authorities"][0]["owner"] += f"{character}unsafe"
                path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
                _rebind_target(package)
                with self.assertRaisesRegex(
                    UpgradeVerificationError,
                    "unsafe Unicode evidence characters",
                ):
                    preflight(package)

        for character in unsafe:
            summary = f"Changed routing{character} ownership."
            with self.subTest(summary=f"U+{ord(character):04X}"):
                self.assertEqual(release_note_summary_classification(summary), "UNSAFE")
                with tempfile.TemporaryDirectory() as directory:
                    package = Path(directory) / "package"
                    shutil.copytree(FIXTURE, package)
                    path = package / "new-release-notes.json"
                    notes = json.loads(path.read_text(encoding="utf-8"))
                    notes["changes"][0]["summary"] = summary
                    path.write_text(json.dumps(notes, indent=2) + "\n", encoding="utf-8")
                    _rebind_release_notes(package, "new_release")
                    with self.assertRaisesRegex(
                        UpgradeVerificationError,
                        "release-note summary contains unsafe Unicode evidence characters",
                    ):
                        preflight(package)

        self.assertEqual(
            release_note_summary_classification("Changed routing ownership for 👩‍💻 users."),
            "MATERIAL",
        )
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(FIXTURE, package)
            request_path = package / "request.json"
            request = json.loads(request_path.read_text(encoding="utf-8"))
            request["challenger"] = "rélease-challenger"
            request_path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
            preflight(package)

    def test_record_binds_native_root_owner_and_request_git_identity(self) -> None:
        """The record distinguishes native content ownership from conditional Git work."""
        text = _record()
        context = preflight(FIXTURE)
        self.assertEqual(
            context["target"]["native_authority_owners"]["ROOT_INSTRUCTIONS"],
            "target-coordinator",
        )
        self.assertEqual(
            context["request_role_keys"]["coordinator"],
            context["request_role_keys"]["git_holder"],
        )
        exact = (
            "The surviving `ROOT_INSTRUCTIONS` native owner is `target-coordinator`; "
            "the sole request coordinator/Git holder is `target-upgrade-coordinator` "
            "if later authorized."
        )
        self.assertEqual(text.count(exact), 1)
        verify(FIXTURE, text)
        receipt = resumer_receipt(FIXTURE, text)
        self.assertEqual(receipt["freshness"], "CURRENT_AFTER_STALE_HANDOFF_REJECTED")

        mutations = (
            (
                "native role",
                "`ROOT_INSTRUCTIONS` native owner",
                "`STANDARDS` native owner",
            ),
            (
                "native owner identity",
                "native owner is `target-coordinator`",
                "native owner is `application-owner`",
            ),
            (
                "request coordinator identity",
                "holder is `target-upgrade-coordinator`",
                "holder is `target-coordinator`",
            ),
            (
                "Git-holder role",
                "request coordinator/Git holder",
                "request coordinator",
            ),
            (
                "conditional authority",
                "if later authorized.",
                "is already authorized.",
            ),
        )
        for name, old, new in mutations:
            with self.subTest(name=name):
                self.assertIn(old, text)
                malformed = text.replace(old, new, 1)
                with self.assertRaisesRegex(
                    UpgradeVerificationError,
                    "target-native/coordinator ownership is missing",
                ):
                    verify(FIXTURE, malformed)

    def test_native_ownership_requires_unique_section_and_first_raw_paragraph(self) -> None:
        """Hidden, quoted, fenced, late, or multiply headed claims cannot rescue authority."""
        text = _record()
        heading = "## Native truth and excluded work"
        exact = (
            "The surviving `ROOT_INSTRUCTIONS` native owner is `target-coordinator`; "
            "the sole request coordinator/Git holder is `target-upgrade-coordinator` "
            "if later authorized."
        )
        self.assertEqual(text.count(heading), 1)
        self.assertEqual(text.count(exact), 1)
        verify(FIXTURE, text)
        self.assertEqual(
            resumer_receipt(FIXTURE, text)["freshness"],
            "CURRENT_AFTER_STALE_HANDOFF_REJECTED",
        )
        verify(FIXTURE, text.replace(exact, f"   {exact}", 1))

        section_start = text.index(heading)
        section_end = text.index("\n## Applicable material changes", section_start)
        section = text[section_start:section_end]
        blockquote_section = "\n".join(
            f"> {line}" if line else ">" for line in section.splitlines()
        )

        cases = (
            ("HTML comment", text.replace(exact, f"<!-- {exact} -->", 1)),
            (
                "fenced decoy",
                text.replace(exact, f"```text\n{exact}\n```", 1),
            ),
            ("blockquote decoy", text.replace(exact, f"> {exact}", 1)),
            ("four-space indented code block", text.replace(exact, f"    {exact}", 1)),
            ("tab-indented code block", text.replace(exact, f"\t{exact}", 1)),
            (
                "contradictory first paragraph",
                text.replace(
                    exact,
                    "The native owner and Git holder are the same person now.\n\n" + exact,
                    1,
                ),
            ),
            ("missing heading", text.replace(heading, "## Native ownership", 1)),
            (
                "whole section HTML comment",
                text[:section_start] + "<!--\n" + section + "\n-->" + text[section_end:],
            ),
            (
                "same-line commented heading",
                text.replace(heading, f"<!-- {heading} -->", 1),
            ),
            (
                "whole section backtick fence",
                text[:section_start] + "```markdown\n" + section + "\n```" + text[section_end:],
            ),
            (
                "whole section tilde fence",
                text[:section_start] + "~~~markdown\n" + section + "\n~~~" + text[section_end:],
            ),
            (
                "whole section blockquote",
                text[:section_start] + blockquote_section + text[section_end:],
            ),
            (
                "duplicate heading",
                text.replace(
                    heading,
                    f"{heading}\n\n{exact}\n\n{heading}",
                    1,
                ),
            ),
        )
        for name, malformed in cases:
            with (
                self.subTest(name=name),
                self.assertRaisesRegex(
                    UpgradeVerificationError, "target-native/coordinator ownership"
                ),
            ):
                verify(FIXTURE, malformed)

    def test_non_markdown_separators_cannot_create_upgrade_record_lines(self) -> None:
        """Python-only line boundaries remain content in every checked Markdown shape."""
        text = _record()
        native_sentence = (
            "The surviving `ROOT_INSTRUCTIONS` native owner is `target-coordinator`; "
            "the sole request coordinator/Git holder is `target-upgrade-coordinator` "
            "if later authorized."
        )
        targets = (
            ("safety fence", "```yaml", parse_upgrade_record),
            ("native heading", "## Native truth and excluded work", None),
            ("native prose", native_sentence, None),
            ("U01 disposition", "| U01 |", None),
            ("sequence guard", "| sequence |", None),
        )
        for separator_name, separator in NON_MARKDOWN_LINE_SEPARATORS:
            for target_name, target, parser in targets:
                with self.subTest(separator=separator_name, target=target_name):
                    self.assertIn(target, text)
                    malformed = text.replace(target, separator + target, 1)
                    with self.assertRaises(UpgradeVerificationError):
                        if parser is None:
                            verify(FIXTURE, malformed)
                        else:
                            parser(malformed)

    def test_safety_receipt_must_be_visible_markdown(self) -> None:
        """A hidden inner YAML fence cannot supply the safety receipt."""
        text = _record()
        block_end = text.index("\n```\n") + len("\n```")
        safety_block = text[:block_end]
        remainder = text[block_end:]
        hidden = (
            ("HTML comment", "<!--\n" + safety_block + "\n-->" + remainder),
            (
                "outer backtick fence",
                "````markdown\n" + safety_block + "\n````" + remainder,
            ),
            (
                "outer tilde fence",
                "~~~markdown\n" + safety_block + "\n~~~" + remainder,
            ),
        )
        for name, malformed in hidden:
            with (
                self.subTest(name=name),
                self.assertRaisesRegex(UpgradeVerificationError, "exactly one yaml safety block"),
            ):
                verify(FIXTURE, malformed)

    def test_disposition_and_guard_tables_must_be_visible_markdown(self) -> None:
        """Hidden disposition or migration-guard tables cannot supply required rows."""
        text = _record()
        disposition_table = text[text.index("| Change | Disposition") : text.index("\n\nU04")]
        guard_table = text[text.index("| Guard | Decision |") : text.index("\n\n## Workspace")]
        self.assertIn("| U01 |", disposition_table)
        self.assertIn("| sequence |", guard_table)
        cases = (
            (
                "disposition HTML comment",
                disposition_table,
                "<!--\n" + disposition_table + "\n-->",
                "only U01-U03 may create target disposition rows",
            ),
            (
                "disposition fenced code",
                disposition_table,
                "```text\n" + disposition_table + "\n```",
                "only U01-U03 may create target disposition rows",
            ),
            (
                "guard HTML comment",
                guard_table,
                "<!--\n" + guard_table + "\n-->",
                "migration guard rows differ",
            ),
            (
                "guard fenced code",
                guard_table,
                "```text\n" + guard_table + "\n```",
                "migration guard rows differ",
            ),
        )
        for name, target, replacement, message in cases:
            with self.subTest(name=name), self.assertRaisesRegex(UpgradeVerificationError, message):
                verify(FIXTURE, text.replace(target, replacement, 1))

    def test_safety_receipt_accepts_commonmark_closing_fence_shapes(self) -> None:
        """The selected triple-backtick block accepts bounded CommonMark closers."""
        text = _record()
        closing = "\n```\n"
        self.assertIn(closing, text)
        for name, replacement in (
            ("longer run", "\n`````\n"),
            ("two-space indent", "\n  ```\n"),
            ("three-space longer run", "\n   ````\n"),
        ):
            with self.subTest(name=name):
                verify(FIXTURE, text.replace(closing, replacement, 1))

    def test_safety_receipt_rejects_nonclosing_fence_shapes(self) -> None:
        """Wrong, short, or suffixed runs cannot close the selected safety block."""
        text = _record()
        closing = "\n```\n"
        self.assertIn(closing, text)
        for name, replacement in (
            ("wrong marker", "\n~~~\n"),
            ("too short", "\n``\n"),
            ("info suffix", "\n```yaml\n"),
        ):
            with (
                self.subTest(name=name),
                self.assertRaisesRegex(UpgradeVerificationError, "exactly one yaml safety block"),
            ):
                verify(FIXTURE, text.replace(closing, replacement, 1))

    def test_backtick_in_info_string_does_not_hide_upgrade_evidence(self) -> None:
        """Invalid backtick-fence info remains prose before either exact target."""
        text = _record()
        invalid_opener = "```lang`invalid"
        heading = "## Native truth and excluded work"
        cases = (
            ("safety receipt", invalid_opener + "\n" + text),
            (
                "native ownership",
                text.replace(heading, invalid_opener + "\n" + heading, 1),
            ),
        )
        for name, candidate in cases:
            with self.subTest(name=name):
                verify(FIXTURE, candidate)

    def test_comment_text_cannot_synthesize_or_leak_from_upgrade_fences(self) -> None:
        """Fence detection precedes comment parsing before both exact targets."""
        text = _record()
        heading = "## Native truth and excluded work"
        prefixes = (
            ("comment-stripped lookalike", "<!--x-->```markdown"),
            ("backtick info literal", "```markdown <!--\ndecoy\n```"),
            ("tilde info literal", "~~~markdown <!--\ndecoy\n~~~"),
        )
        for prefix_name, prefix in prefixes:
            candidates = (
                ("safety receipt", prefix + "\n" + text),
                (
                    "native ownership",
                    text.replace(heading, prefix + "\n" + heading, 1),
                ),
            )
            for target_name, candidate in candidates:
                with self.subTest(prefix=prefix_name, target=target_name):
                    verify(FIXTURE, candidate)

    def test_non_markdown_separators_cannot_be_trimmed_from_table_cells(self) -> None:
        """Unicode separators remain material at disposition and guard cell edges."""
        text = _record()
        targets = (("U01 disposition", "U01"), ("sequence guard", "sequence"))
        for separator_name, separator in NON_MARKDOWN_LINE_SEPARATORS:
            for target_name, target in targets:
                with self.subTest(separator=separator_name, target=target_name):
                    marker = f"| {target} |"
                    self.assertIn(marker, text)
                    malformed = text.replace(marker, f"| {separator}{target} |", 1)
                    with self.assertRaises(UpgradeVerificationError):
                        verify(FIXTURE, malformed)

    def test_repeated_outer_pipes_cannot_shift_checked_table_cells(self) -> None:
        """Repeated edge or internal delimiters remain material empty cells."""
        text = _record()
        for name, target in (("U01 disposition", "U01"), ("sequence guard", "sequence")):
            marker = f"| {target} |"
            line = next(line for line in text.split("\n") if line.startswith(marker))
            mutations = (
                ("doubled leading", "|" + line),
                ("doubled trailing", line + "|"),
                ("both edges", "|" + line + "|"),
                ("internal empty cell", line.replace(marker, marker + "|", 1)),
            )
            for mutation, replacement in mutations:
                with self.subTest(name=name, mutation=mutation):
                    malformed = text.replace(line, replacement, 1)
                    with self.assertRaises(UpgradeVerificationError):
                        verify(FIXTURE, malformed)

    def test_upgrade_record_accepts_commonmark_line_endings(self) -> None:
        """LF, CRLF, and CR remain the only accepted Markdown line boundaries."""
        text = _record()
        for name, line_ending in (("LF", "\n"), ("CRLF", "\r\n"), ("CR", "\r")):
            with self.subTest(line_ending=name):
                verify(FIXTURE, text.replace("\n", line_ending))

    def test_native_owner_identities_reject_unsafe_text_and_accept_alias_forms(self) -> None:
        """Digest-bound native owners share canonical identity ingress without forced spelling."""
        original = json.loads((FIXTURE / "native-authorities.json").read_text(encoding="utf-8"))
        rejecting = (
            ("padded", lambda value: f" {value} ", "canonical non-empty"),
            ("CGJ", lambda value: f"{value}\u034f", "synthetic Unicode ignorables"),
            ("runtime Cf", lambda value: f"{value}\u0600", "synthetic Unicode ignorables"),
        )
        for index, authority in enumerate(original["authorities"]):
            for name, mutate, error in rejecting:
                with (
                    self.subTest(role=authority["role"], mutation=name),
                    tempfile.TemporaryDirectory() as directory,
                ):
                    package = Path(directory) / "package"
                    shutil.copytree(FIXTURE, package)
                    path = package / "native-authorities.json"
                    inventory = json.loads(path.read_text(encoding="utf-8"))
                    inventory["authorities"][index]["owner"] = mutate(authority["owner"])
                    path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
                    _rebind_target(package)
                    with self.assertRaisesRegex(UpgradeVerificationError, error):
                        preflight(package)

            for name, transform in (("case", str.upper), ("fullwidth", _fullwidth_ascii)):
                with (
                    self.subTest(role=authority["role"], control=name),
                    tempfile.TemporaryDirectory() as directory,
                ):
                    package = Path(directory) / "package"
                    shutil.copytree(FIXTURE, package)
                    path = package / "native-authorities.json"
                    inventory = json.loads(path.read_text(encoding="utf-8"))
                    inventory["authorities"][index]["owner"] = transform(authority["owner"])
                    path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
                    _rebind_target(package)
                    preflight(package)

    def test_rejects_state_only_release_note_summary_after_digest_rebind(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(FIXTURE, package)
            notes_path = package / "new-release-notes.json"
            notes = json.loads(notes_path.read_text(encoding="utf-8"))
            notes["changes"][0]["summary"] = "Changed for the agent-warmboot-v2.0.0 candidate."
            notes_path.write_text(json.dumps(notes, indent=2) + "\n", encoding="utf-8")
            _rebind_release_notes(package, "new_release")
            with self.assertRaisesRegex(UpgradeVerificationError, "state-only"):
                verify(package, _record(package))

    def test_release_note_compatibility_is_canonical_and_release_specific(self) -> None:
        """Old baseline and new incompatible notes cannot exchange compatibility states."""
        cases = (
            ("old empty", "old_release", ""),
            ("old whitespace", "old_release", " "),
            ("old nontext", "old_release", True),
            ("old incompatible", "old_release", "INCOMPATIBLE_CORE_SAFETY"),
            ("old additive", "old_release", "COMPATIBLE_ADDITIVE"),
            ("new empty", "new_release", ""),
            ("new whitespace", "new_release", " "),
            ("new baseline", "new_release", "BASELINE"),
            ("new additive", "new_release", "COMPATIBLE_ADDITIVE"),
        )
        for name, release, compatibility in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                request = json.loads((package / "request.json").read_text(encoding="utf-8"))
                path = package / request[release]["release_notes_path"]
                notes = json.loads(path.read_text(encoding="utf-8"))
                notes["compatibility"] = compatibility
                path.write_text(json.dumps(notes, indent=2) + "\n", encoding="utf-8")
                _rebind_release_notes(package, release)
                with self.assertRaisesRegex(UpgradeVerificationError, "compatibility"):
                    preflight(package)

    def test_rejects_same_annotated_ref_after_fully_rebound_release_inputs(self) -> None:
        """Distinct commits and payloads cannot turn one immutable tag into two releases."""
        baseline = preflight(FIXTURE)
        self.assertNotEqual(
            baseline["request"]["old_release"]["identity"],
            baseline["request"]["new_release"]["identity"],
        )

        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(FIXTURE, package)
            request_path = package / "request.json"
            request = json.loads(request_path.read_text(encoding="utf-8"))
            old_ref = request["old_release"]["identity"]
            request["new_release"]["identity"] = old_ref

            manifest_path = package / request["new_release"]["manifest_path"]
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["release"]["declared_ref"] = old_ref
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            request["new_release"]["manifest_sha256"] = hashlib.sha256(
                manifest_path.read_bytes()
            ).hexdigest()

            notes_path = package / request["new_release"]["release_notes_path"]
            notes = json.loads(notes_path.read_text(encoding="utf-8"))
            notes["release_ref"] = old_ref
            notes_path.write_text(json.dumps(notes, indent=2) + "\n", encoding="utf-8")
            request["new_release"]["release_notes_sha256"] = hashlib.sha256(
                notes_path.read_bytes()
            ).hexdigest()
            request_path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")

            self.assertNotEqual(
                request["old_release"]["resolved_commit"],
                request["new_release"]["resolved_commit"],
            )
            self.assertNotEqual(
                json.loads(
                    (package / request["old_release"]["manifest_path"]).read_text(encoding="utf-8")
                )["release"]["payload_sha256"],
                manifest["release"]["payload_sha256"],
            )
            with self.assertRaisesRegex(
                UpgradeVerificationError,
                "old/new annotated release refs must be distinct",
            ):
                preflight(package)

    def test_release_note_summaries_are_canonical_and_material_after_rebind(self) -> None:
        """Empty, punctuation-only, padded, or state summaries cannot replace meaning."""
        cases = (
            ("bare", "Changed", "state-only"),
            ("exclamation", "Changed!", "state-only"),
            ("question", "Changed?", "state-only"),
            ("periods", "Changed...", "state-only"),
            ("ellipsis", "Changed…", "state-only"),
            ("upper", "UPDATED!", "state-only"),
            ("fullwidth alias", "Ｃｈａｎｇｅｄ!", "state-only"),
            ("circled alias", "Ⓒⓗⓐⓝⓖⓔⓓ!", "state-only"),
            ("mathematical alias", "𝖢𝗁𝖺𝗇𝗀𝖾𝖽!", "state-only"),
            ("leading punctuation", "!!!Changed", "state-only"),
            ("leading CJK fullwidth", "。Ｃｈａｎｇｅｄ", "state-only"),
            ("internal punctuation", "Cha!nged", "state-only"),
            ("punctuation token boundary", "Changed!for release", "state-only"),
            ("removed semicolons", "removed;;", "state-only"),
            ("release", "Changed for release.", "state-only"),
            (
                "candidate",
                "Changed for the agent-warmboot-v2.0.0 candidate!",
                "state-only",
            ),
            ("mixed punctuation", "Changed!?…;", "state-only"),
            ("ASCII punctuation", "!!!", "material text"),
            ("Unicode punctuation", "…；！？", "material text"),
            ("CJK stop", "。", "material text"),
            ("mixed punctuation only", "!…;；!?", "material text"),
            ("format after period", "Changed.\u200b", "state-only"),
            ("joiner alias", "Changed\u200d", "state-only"),
            ("format inside verb", "Cha\u200bnged", "state-only"),
            ("format token boundary", "Changed\u200bfor release.", "state-only"),
            (
                "word-joiner token boundary",
                "Changed\u2060for the agent-warmboot-v2.0.0 candidate.",
                "state-only",
            ),
            (
                "punctuation inside release ref",
                "Changed for the agent-warmboot-v2!.0.0 candidate.",
                "state-only",
            ),
            (
                "punctuation before exact candidate token",
                "Changed for the agent-warmboot-v2.0.0! candidate.",
                "state-only",
            ),
            ("format punctuation", "!!!\u200b", "material text"),
            ("CJK format punctuation", "。\u200b", "material text"),
            ("empty", "", "canonical non-empty"),
            ("whitespace", " ", "canonical non-empty"),
            ("nontext", None, "canonical non-empty"),
            ("padded punctuation", " !!! ", "canonical non-empty"),
            ("padded semantic", " Material routing changed. ", "canonical non-empty"),
        )
        for name, summary, error in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                path = package / "new-release-notes.json"
                notes = json.loads(path.read_text(encoding="utf-8"))
                notes["changes"][0]["summary"] = summary
                path.write_text(json.dumps(notes, indent=2) + "\n", encoding="utf-8")
                _rebind_release_notes(package, "new_release")
                with self.assertRaisesRegex(UpgradeVerificationError, error):
                    preflight(package)

    def test_unicode_policy_has_independent_table_count_and_predicate_parity(self) -> None:
        """The 4,174 DICP/runtime-Cf union and unsafe-category policy agree exhaustively."""
        self.assertEqual(
            sum(end - start + 1 for start, end in EXPECTED_DEFAULT_IGNORABLE_RANGES),
            4174,
        )
        mismatches: list[tuple[int, bool, bool, bool]] = []
        for codepoint in range(sys.maxunicode + 1):
            character = chr(codepoint)
            expected_default = _expected_default_ignorable(codepoint)
            actual_default = is_default_ignorable_code_point(character)
            expected_synthetic = expected_default or unicodedata.category(character) == "Cf"
            actual_synthetic = is_synthetic_ignorable(character)
            expected_unsafe = unicodedata.category(character) in {"Cc", "Cs", "Co", "Cn"}
            actual_unsafe = is_unsafe_evidence_character(character)
            if (
                actual_default != expected_default
                or actual_synthetic != expected_synthetic
                or actual_unsafe != expected_unsafe
            ):
                mismatches.append((codepoint, actual_default, actual_synthetic, actual_unsafe))
                break
        self.assertEqual(mismatches, [])
        for codepoint in (0x0600, 0x13430):
            with self.subTest(codepoint=f"U+{codepoint:04X}"):
                self.assertEqual(unicodedata.category(chr(codepoint)), "Cf")
                self.assertFalse(is_default_ignorable_code_point(chr(codepoint)))
                self.assertTrue(is_synthetic_ignorable(chr(codepoint)))
        self.assertEqual(unicodedata.category("\u0301"), "Mn")
        self.assertFalse(is_default_ignorable_code_point("\u0301"))
        self.assertFalse(is_synthetic_ignorable("\u0301"))
        self.assertFalse(is_unsafe_evidence_character("\u0301"))
        self.assertFalse(is_unsafe_evidence_character("\u200d"))
        self.assertFalse(is_unsafe_evidence_character("🔒"))
        for character, category in (
            ("\x00", "Cc"),
            ("\x7f", "Cc"),
            ("\ud800", "Cs"),
            ("\ue000", "Co"),
            ("\u0378", "Cn"),
        ):
            with self.subTest(unsafe=f"U+{ord(character):04X}"):
                self.assertEqual(unicodedata.category(character), category)
                self.assertTrue(is_unsafe_evidence_character(character))
        self.assertEqual(nfkc_casefold("Ⓒⓗⓐⓝⓖⓔⓓ"), "changed")

    def test_all_synthetic_ignorables_are_non_material(self) -> None:
        """Every designed/runtime ignorable stays inert in state and punctuation text."""
        ignorable_characters = (
            chr(codepoint)
            for codepoint in range(sys.maxunicode + 1)
            if is_synthetic_ignorable(chr(codepoint))
        )
        for character in ignorable_characters:
            with self.subTest(codepoint=f"U+{ord(character):04X}"):
                state_classification = (
                    "UNSAFE" if is_unsafe_evidence_character(character) else "STATE_ONLY"
                )
                empty_classification = (
                    "UNSAFE" if is_unsafe_evidence_character(character) else "EMPTY"
                )
                self.assertEqual(
                    release_note_summary_classification(f"Changed.{character}"),
                    state_classification,
                )
                self.assertEqual(
                    release_note_summary_classification(f"Cha{character}nged."),
                    state_classification,
                )
                self.assertEqual(
                    release_note_summary_classification(f"Changed{character}for release."),
                    state_classification,
                )
                self.assertEqual(
                    release_note_summary_classification(f"!!!{character}"),
                    empty_classification,
                )

    def test_ignorables_cannot_split_any_state_only_token_position(self) -> None:
        """Both interpretations reject representative DICP controls at every position."""
        phrases = (
            "Changed",
            "Changed for release.",
            "Changed for the agent-warmboot-v2.0.0 candidate.",
        )
        for control in ("\u034f", "\ufe0f", "\U000e0100", "\u0600"):
            for phrase in phrases:
                for position in range(len(phrase) + 1):
                    candidate = phrase[:position] + control + phrase[position:]
                    with self.subTest(
                        control=f"U+{ord(control):04X}",
                        phrase=phrase,
                        position=position,
                    ):
                        self.assertEqual(
                            release_note_summary_classification(candidate),
                            "STATE_ONLY",
                        )

    def test_unicode_punctuation_cannot_manufacture_materiality(self) -> None:
        """Every Unicode-P scalar stays inert at all positions in bounded state phrases."""
        phrases = (
            "Changed",
            "Removed for release",
            "Changed for the agent-warmboot-v2.0.0 candidate",
        )
        punctuation_characters = (
            chr(codepoint)
            for codepoint in range(sys.maxunicode + 1)
            if unicodedata.category(chr(codepoint)).startswith("P")
        )
        observed = 0
        for punctuation in punctuation_characters:
            observed += 1
            with self.subTest(codepoint=f"U+{ord(punctuation):04X}", position="punctuation-only"):
                self.assertEqual(
                    release_note_summary_classification(punctuation * 2),
                    "EMPTY",
                )
            for phrase in phrases:
                for position in range(len(phrase) + 1):
                    candidate = phrase[:position] + punctuation + phrase[position:]
                    with self.subTest(
                        codepoint=f"U+{ord(punctuation):04X}",
                        phrase=phrase,
                        position=position,
                    ):
                        self.assertEqual(
                            release_note_summary_classification(candidate),
                            "STATE_ONLY",
                        )
        # Guards against an empty scan across supported Python Unicode databases.
        self.assertGreater(observed, 700)

    def test_accepts_material_release_note_summaries_after_digest_rebind(self) -> None:
        """A concrete change sentence remains distinct from the bounded state-only grammar."""
        for summary in (
            "Material routing changed.",
            "Changed routing ownership to preserve the recovery boundary!",
            "Changed\u200d routing ownership to preserve the recovery boundary!",
            "Changed routing ownership 🔒.",
            "Cafe\u0301 routing remains explicit.",
            "Changed routing ownership for ✈️ users.",
            "C++ parser ownership changed.",
            "Routing/ownership changed.",
            "Agent-owned routing changed.",
            "Routing, ownership (and recovery) changed.",
        ):
            with self.subTest(summary=summary), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                path = package / "new-release-notes.json"
                notes = json.loads(path.read_text(encoding="utf-8"))
                notes["changes"][0]["summary"] = summary
                path.write_text(json.dumps(notes, indent=2) + "\n", encoding="utf-8")
                _rebind_release_notes(package, "new_release")
                preflight(package)

    def test_rejects_duplicate_json_authority_before_safe_value(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(FIXTURE, package)
            request_path = package / "request.json"
            text = request_path.read_text(encoding="utf-8")
            unsafe = (
                '  "authority": {"may_plan": true, "may_edit": true, '
                '"may_commit": true, "may_publish": true},\n'
            )
            request_path.write_text(
                text.replace('  "authority": {', unsafe + '  "authority": {', 1),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                UpgradeVerificationError, "duplicate JSON object key: authority"
            ):
                preflight(package)

    def test_rejects_boolean_like_schema_and_authority_values_after_rebind(self) -> None:
        """Python booleans cannot stand in for fixture schema or authority primitives."""
        cases = (
            ("request schema", "request.json", ("schema_version",), True),
            ("native schema", "native-authorities.json", ("schema_version",), True),
            ("adoption schema", "adoption-receipt.json", ("schema_version",), True),
            ("planning authority", "request.json", ("authority", "may_plan"), 1),
            ("edit authority", "request.json", ("authority", "may_edit"), 0),
            ("commit authority", "request.json", ("authority", "may_commit"), 0),
            ("publication authority", "request.json", ("authority", "may_publish"), 0),
        )
        for name, relative, keys, value in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                path = package / relative
                raw = json.loads(path.read_text(encoding="utf-8"))
                target = raw
                for key in keys[:-1]:
                    target = target[key]
                target[keys[-1]] = value
                path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
                _rebind_target(package)
                with self.assertRaises(UpgradeVerificationError):
                    preflight(package)

    def test_rejects_non_integer_handoff_schema_version(self) -> None:
        """Handoff schema_version is an exact integer, not an equality-compatible scalar."""
        for value in (True, 0, "1", None, {}, []):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                path = package / "HANDOFF.json"
                handoff = json.loads(path.read_text(encoding="utf-8"))
                handoff["schema_version"] = value
                path.write_text(json.dumps(handoff, indent=2) + "\n", encoding="utf-8")
                with self.assertRaisesRegex(UpgradeVerificationError, "handoff schema_version"):
                    preflight(package)

    def test_workspace_requires_two_unique_exact_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(FIXTURE, package)
            workspace_path = package / "consumer.code-workspace"
            workspace = json.loads(workspace_path.read_text(encoding="utf-8"))
            workspace["tasks"]["tasks"].insert(
                1,
                {
                    "label": "test: full",
                    "type": "shell",
                    "command": "python3 -c 'raise SystemExit(0)'",
                },
            )
            workspace_path.write_text(json.dumps(workspace, indent=2) + "\n", encoding="utf-8")
            _rebind_target(package)
            with self.assertRaisesRegex(UpgradeVerificationError, "labels must be unique"):
                preflight(package)

    def test_incompatible_guard_table_retains_exact_scope_and_stops(self) -> None:
        parsed = parse_upgrade_record(_record())
        scope = tuple(
            value for value in __import__("re").findall(r"`([^`]+)`", parsed["guards"]["scope"])
        )
        self.assertEqual(scope, ROLLBACK_SCOPE)
        self.assertIn("exact-path", parsed["guards"]["checkpoint"])
        self.assertIn("five prior file", parsed["guards"]["rollback"])
        self.assertIn("CLEAN", parsed["guards"]["review"])
        self.assertIn("RERUN NOW", parsed["guards"]["stale"])

    def test_rejects_indented_u04_disposition_and_escaped_pipe(self) -> None:
        u04 = (
            " | U04 | `ADOPT` | Teaching row disguised by indentation. | "
            "`docs/teaching.md` | None. |\n"
        )
        escaped_pipe = _record().replace(
            "Adapt recovery and provider-neutral routing",
            r"Adapt recovery \| provider-neutral routing",
            1,
        )
        for name, text in (
            ("one-space U04", _record() + u04),
            ("escaped pipe", escaped_pipe),
        ):
            with self.subTest(name=name), self.assertRaises(UpgradeVerificationError):
                verify(FIXTURE, text)

    def test_eight_fail_closed_canaries(self) -> None:
        def wrong_identity(package: Path, text: str) -> str:
            return text.replace(
                "@1111111111111111111111111111111111111111#",
                "@9999999999999999999999999999999999999999#",
                1,
            )

        def missing_adoption(package: Path, text: str) -> str:
            path = package / "adoption-receipt.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            del value["warmboot_release"]["manifest_sha256"]
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            return text

        def blind_overwrite(package: Path, text: str) -> str:
            return text.replace(
                "| U03 | `MERGE INTO EXISTING`", "| U03 | `REPLACE_FROM_TEMPLATE`", 1
            )

        def no_rollback(package: Path, text: str) -> str:
            return (
                "\n".join(line for line in text.splitlines() if not line.startswith("| rollback |"))
                + "\n"
            )

        def stale_input(package: Path, text: str) -> str:
            (package / "consumer.code-workspace").write_text("{}\n", encoding="utf-8")
            return text

        def publication(package: Path, text: str) -> str:
            return text.replace("  may_publish: false", "  may_publish: true", 1)

        def unrelated_dirt(package: Path, text: str) -> str:
            return text.replace(
                "`docs/testing.md` only.",
                "`docs/testing.md`; `notes/unrelated-owner.txt` only.",
                1,
            )

        def workspace(package: Path, text: str) -> str:
            return text.replace(
                "`docs/testing.md` only.",
                "`docs/testing.md`; `consumer.code-workspace` only.",
                1,
            )

        cases = {
            "identity": wrong_identity,
            "adoption": missing_adoption,
            "blind_overwrite": blind_overwrite,
            "no_rollback": no_rollback,
            "stale": stale_input,
            "publication": publication,
            "unrelated_dirt": unrelated_dirt,
            "workspace": workspace,
        }
        self.assertEqual(len(cases), 8)
        for name, mutate in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                text = mutate(package, _record(package))
                with self.assertRaises(UpgradeVerificationError):
                    verify(package, text)

    def test_fresh_resumer_recovers_exact_state_from_disposable_copy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "fresh-package"
            shutil.copytree(FIXTURE, package)
            receipt = resumer_receipt(package, _record(package))
        self.assertEqual(receipt["adoption"], "CURRENT")
        self.assertEqual(receipt["freshness"], "CURRENT_AFTER_STALE_HANDOFF_REJECTED")
        self.assertEqual(
            receipt["destinations"],
            {
                "U01": "AGENTS.md",
                "U02": ".agent-warmboot/routes/recovery.md",
                "U03": "docs/testing.md",
            },
        )
        self.assertEqual(
            receipt["rollback_prerequisite"],
            "EXPLICIT_AUTHORITY_AND_EXACT_PATH_CHECKPOINT",
        )
        self.assertTrue(receipt["workspace"]["preserve"])
        self.assertEqual(
            set(receipt["dirt"]),
            {"notes/unrelated-owner.txt", "scratch/local-analysis.txt"},
        )
        self.assertEqual(
            receipt["authority"],
            {"may_edit": False, "may_git": False, "may_publish": False},
        )

    def test_rejects_missing_old_or_target_identity_as_blocked(self) -> None:
        for boundary, key in (("old_release", "identity"), ("target", "identity")):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                request_path = package / "request.json"
                request = json.loads(request_path.read_text(encoding="utf-8"))
                request[boundary][key] = ""
                request_path.write_text(json.dumps(request), encoding="utf-8")
                with self.assertRaisesRegex(UpgradeVerificationError, "BLOCKED"):
                    preflight(package)

    def test_rejects_empty_or_unknown_field_release_manifest(self) -> None:
        for kind in ("empty", "unknown top-level field"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                manifest_path = package / "new-release-manifest.json"
                if kind == "empty":
                    manifest_path.write_text("{}\n", encoding="utf-8")
                else:
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    manifest["artifact_groups"] = {}
                    manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
                request_path = package / "request.json"
                request = json.loads(request_path.read_text(encoding="utf-8"))
                request["new_release"]["manifest_sha256"] = hashlib.sha256(
                    manifest_path.read_bytes()
                ).hexdigest()
                request_path.write_text(json.dumps(request) + "\n", encoding="utf-8")
                with self.assertRaisesRegex(UpgradeVerificationError, "schema is incompatible"):
                    preflight(package)

    def test_rejects_compact_manifest_policy_digest_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(FIXTURE, package)
            manifest_path = package / "new-release-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["payload_policy_sha256"] = "0" * 64
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            request_path = package / "request.json"
            request = json.loads(request_path.read_text(encoding="utf-8"))
            request["new_release"]["manifest_sha256"] = hashlib.sha256(
                manifest_path.read_bytes()
            ).hexdigest()
            request_path.write_text(json.dumps(request) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(UpgradeVerificationError, "policy digest"):
                preflight(package)

    def test_rejects_symlinked_workspace_or_dirt_evidence(self) -> None:
        for relative in ("consumer.code-workspace", "notes/unrelated-owner.txt"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                outside = Path(directory) / "outside"
                outside.write_text("outside\n", encoding="utf-8")
                path = package / relative
                path.unlink()
                path.symlink_to(outside)
                with self.assertRaises(UpgradeVerificationError):
                    preflight(package)

    def test_cli_reports_an_undecodable_record_as_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(FIXTURE, package)
            (package / "UPGRADE.md").write_bytes(b"\xff\xfe not text\n")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                status = main(["--package", str(package), "--result", "UPGRADE.md"])
            self.assertEqual(status, 1)
            self.assertTrue(stderr.getvalue().startswith("FAIL:"), stderr.getvalue())

    def test_names_a_missing_package_member(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(FIXTURE, package)
            (package / "handoff-source.txt").unlink()
            with self.assertRaisesRegex(UpgradeVerificationError, "handoff source must exist"):
                preflight(package)
            with self.assertRaisesRegex(
                UpgradeVerificationError, "upgrade record cannot be checked"
            ):
                _member(package, "a" * 300, "upgrade record")


class ReleaseManifestBoundaryTests(unittest.TestCase):
    """Reject malformed JSON domains and symlinked include ancestry before hashing."""

    @staticmethod
    def candidate(root: Path) -> dict:
        """Build an invented local candidate with independently encoded digest inputs."""
        for name, data in (
            ("payload.txt", b"synthetic payload\n"),
            ("receipt.txt", b"synthetic local lineage\n"),
        ):
            (root / name).write_bytes(data)
        manifest = json.loads((FIXTURE / "old-release-manifest.json").read_text())
        policy = {
            "include": ["."],
            "exclude": [
                {
                    "path": "candidate.json",
                    "scope": "FILE",
                    "reason": "Exclude this synthetic manifest's self-reference.",
                    "bound_receipt": "receipt.txt",
                }
            ],
        }
        manifest["payload_policy"] = policy
        encoded_policy = (
            json.dumps(policy, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
            + b"\n"
        )
        manifest["payload_policy_sha256"] = hashlib.sha256(encoded_policy).hexdigest()
        records = []
        for name in ("payload.txt", "receipt.txt"):
            data = (root / name).read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            records.append("\0".join((name, "regular", "100644", digest, str(len(data)))) + "\n")
        manifest["release"]["payload_sha256"] = hashlib.sha256(
            "".join(records).encode()
        ).hexdigest()
        manifest["lineage_receipts"] = [
            {
                "path": "receipt.txt",
                "sha256": hashlib.sha256((root / "receipt.txt").read_bytes()).hexdigest(),
            }
        ]
        return manifest

    @staticmethod
    def cli(root: Path, manifest: dict) -> subprocess.CompletedProcess:
        (root / "candidate.json").write_text(json.dumps(manifest) + "\n")
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(ROOT / "acceptance/release_manifest.py"),
                "--repository",
                str(root),
                "--manifest",
                "candidate.json",
                "--expected-policy-sha256",
                manifest["payload_policy_sha256"],
                "--expected-release-id",
                manifest["release"]["id"],
                "--expected-declared-ref",
                manifest["release"]["declared_ref"],
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_candidate_api_cli_and_illustrative_controls(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.candidate(root)
            verify_release_manifest(manifest)
            result = self.cli(root, manifest)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "PASS")
        example = json.loads((ROOT / "docs/releases/release-manifest.example.json").read_text())
        verify_illustrative_manifest(example)

    def test_invalid_set_membership_domains_fail_cleanly_in_api_and_cli(self) -> None:
        fields = (
            ("manifest_kind", "unknown release manifest_kind"),
            ("status", "commit-contained release status"),
            ("scope", "exclusion scope"),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline = self.candidate(root)
            for field, message in fields:
                for invalid in ([], {}, None, True):
                    with self.subTest(field=field, invalid=invalid):
                        manifest = copy.deepcopy(baseline)
                        owner = (
                            manifest
                            if field == "manifest_kind"
                            else (
                                manifest["release"]
                                if field == "status"
                                else manifest["payload_policy"]["exclude"][0]
                            )
                        )
                        owner[field] = invalid
                        with self.assertRaisesRegex(ReleaseManifestVerificationError, message):
                            verify_release_manifest(manifest)
                        illustrative = copy.deepcopy(manifest)
                        if field != "manifest_kind":
                            illustrative["manifest_kind"] = "ILLUSTRATIVE_NON_RELEASE"
                        with self.assertRaisesRegex(ReleaseManifestVerificationError, message):
                            verify_illustrative_manifest(illustrative)
                        result = self.cli(root, manifest)
                        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                        self.assertIn("FAIL:", result.stderr)
                        self.assertIn(message, result.stderr)
                        self.assertNotIn("Traceback", result.stderr)

    def test_nested_include_refuses_external_and_internal_symlink_ancestors(self) -> None:
        for destination in ("outside", "inside"):
            with self.subTest(destination=destination), tempfile.TemporaryDirectory() as directory:
                parent = Path(directory)
                root = parent / "repository"
                root.mkdir()
                backing = parent / "outside" if destination == "outside" else root / "backing"
                (backing / "subtree").mkdir(parents=True)
                (backing / "subtree/x.txt").write_bytes(b"must not be hashed\n")
                (root / "payload").symlink_to(backing, target_is_directory=True)
                with self.assertRaisesRegex(ReleaseManifestVerificationError, "symlink"):
                    selected_records(root, {"include": ["payload/subtree"], "exclude": []})

    def test_ordinary_nested_include_and_excluded_symlink_control(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = root / "payload/subtree"
            payload.mkdir(parents=True)
            data = b"included local data\n"
            (payload / "x.txt").write_bytes(data)
            (payload / "ignored").symlink_to(root, target_is_directory=True)
            policy = {
                "include": ["payload/subtree"],
                "exclude": [
                    {
                        "path": "payload/subtree/ignored",
                        "scope": "SUBTREE",
                        "reason": "Synthetic excluded symlink control.",
                        "bound_receipt": "receipt.txt",
                    }
                ],
            }
            records = selected_records(root, policy)
            self.assertEqual(
                records,
                [
                    {
                        "path": "payload/subtree/x.txt",
                        "type": "regular",
                        "mode": "100644",
                        "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                    }
                ],
            )


if __name__ == "__main__":
    unittest.main()
