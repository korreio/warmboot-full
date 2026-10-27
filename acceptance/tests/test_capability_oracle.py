"""Exercise bounded capability-library selection and strict fake-evidence regressions."""

from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from acceptance import capability_oracle
from acceptance.capability_oracle import (
    CapabilityVerificationError,
    load_repository_json,
    validate_library,
    validate_selection,
)
from acceptance.unicode_policy import NON_MARKDOWN_LINE_SEPARATORS

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "acceptance" / "fixtures" / "capability-library"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CapabilityOracleTests(unittest.TestCase):
    @unittest.skipIf(os.geteuid() == 0, "root can read mode-000 paths")
    def test_directory_it_cannot_inspect_fails_closed(self) -> None:
        _, repository = self.make_repository()
        cases = [
            ("templates/capabilities/hidden", "stray.md", "capability library cannot be listed"),
            ("docs/locked", "inner/stray.tmpl", "repository cannot be listed"),
        ]
        for directory, relative, message in cases:
            locked = repository / directory
            stray = locked / relative
            stray.parent.mkdir(parents=True)
            stray.write_text("stray\n", encoding="utf-8")
            for mode in (0, 0o444):
                with self.subTest(directory=directory, mode=oct(mode)):
                    locked.chmod(mode)
                    try:
                        with self.assertRaisesRegex(CapabilityVerificationError, message):
                            validate_library(repository)
                    finally:
                        locked.chmod(0o755)
            shutil.rmtree(locked)

    def test_cli_reports_an_unusable_path_or_unreadable_card_as_fail(self) -> None:
        long_path = str(ROOT / ("a" * 300))
        outsider = ["--selection", str(FIXTURES / "outsider-all-12.json"), "--outsider"]
        _, repository = self.make_repository()
        card = repository / "templates" / "capabilities" / "testing-feedback.md"
        cases = [
            (["--repository", long_path], 0o644),
            (["--repository", str(ROOT), "--selection", long_path], 0o644),
            (["--repository", str(ROOT), *outsider, "--fake-cases", long_path], 0o644),
        ]
        if os.geteuid() != 0:
            cases.append((["--repository", str(repository)], 0))
        for arguments, mode in cases:
            with self.subTest(arguments=arguments, mode=oct(mode)):
                card.chmod(mode)
                stderr = io.StringIO()
                try:
                    with contextlib.redirect_stderr(stderr):
                        status = capability_oracle.main(arguments)
                finally:
                    card.chmod(0o644)
                self.assertEqual(status, 1)
                self.assertTrue(stderr.getvalue().startswith("FAIL:"), stderr.getvalue())

    def test_a_loop_found_only_at_resolve_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "member.json").write_text("{}\n", encoding="utf-8")
            resolve = Path.resolve

            def load_json() -> object:
                return load_repository_json(root, Path("member.json"), "probe")

            unresolved = "attested repository cannot be resolved"
            cases = [
                ("member.json", load_json, "probe cannot be checked: symlink loop"),
                (root.name, load_json, unresolved),
                (root.name, lambda: validate_library(root), unresolved),
            ]
            for name, call, message in cases:

                def looping(path: Path, strict: bool = False, name: str = name) -> Path:
                    if path.name == name:
                        raise RuntimeError(f"Symlink loop from {str(path)!r}")
                    return resolve(path, strict=strict)

                with (
                    self.subTest(loops_at=name, message=message),
                    mock.patch.object(Path, "resolve", looping),
                    self.assertRaisesRegex(CapabilityVerificationError, message),
                ):
                    call()

    def test_repository_json_path_that_cannot_be_checked_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(CapabilityVerificationError, "probe cannot be checked"):
                load_repository_json(Path(directory), Path("a" * 300), "probe")

    def make_repository(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        repository = Path(temporary.name) / "repository"
        (repository / "templates").mkdir(parents=True)
        (repository / "docs").mkdir(parents=True)
        (repository / "acceptance").mkdir(parents=True)
        shutil.copytree(ROOT / "templates/capabilities", repository / "templates/capabilities")
        shutil.copytree(FIXTURES, repository / "acceptance/fixtures/capability-library")
        for name in (
            "capability-sources.json",
            "capability-design.md",
            "acceptance.md",
            "documentation-architecture.md",
        ):
            shutil.copy2(ROOT / "docs" / name, repository / "docs" / name)
        shutil.copy2(
            ROOT / "acceptance/capability-outsider.md",
            repository / "acceptance/capability-outsider.md",
        )
        return temporary, repository

    def read_manifest(self, repository: Path) -> dict:
        return read_json(repository / "templates" / "capabilities" / "MANIFEST.json")

    def write_manifest(self, repository: Path, manifest: dict) -> None:
        (repository / "templates" / "capabilities" / "MANIFEST.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )

    def write_json(self, path: Path, document: dict) -> None:
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def sync_entry(self, repository: Path, relative: str) -> None:
        manifest = self.read_manifest(repository)
        entry = next(item for item in manifest["files"] if item["path"] == relative)
        data = (repository / "templates" / "capabilities" / relative).read_bytes()
        entry["bytes"] = len(data)
        entry["sha256"] = hashlib.sha256(data).hexdigest()
        self.write_manifest(repository, manifest)

    def test_accepts_exact_real_library(self) -> None:
        manifest = validate_library(ROOT)
        self.assertEqual(len([item for item in manifest["files"] if item["kind"] == "module"]), 12)

    def test_cold_outsider_route_rejects_observed_history_markers(self) -> None:
        cold_visible_paths = (
            ROOT / "docs" / "acceptance.md",
            ROOT / "acceptance" / "capability-outsider.md",
        )
        for path in cold_visible_paths:
            text = path.read_text(encoding="utf-8")
            for historical_marker in (
                "Current cold-run status",
                "before/friction evidence only",
                "Neither after receipt exists",
            ):
                self.assertNotIn(historical_marker, text)

    def test_cold_prompt_routes_before_bootstrap_misclassification(self) -> None:
        acceptance = (ROOT / "docs" / "acceptance.md").read_text(encoding="utf-8")
        section = acceptance.split("## Optional-capability cold outsider gate", 1)[1].split(
            "## Evidence boundary", 1
        )[0]
        self.assertEqual(section.count("```text\n"), 1)
        prompt = section.split("```text\n", 1)[1].split("\n```", 1)[0]
        route = (
            "After `WARMBOOT.md`, read\n"
            "`acceptance/capability-outsider.md`; this is an acceptance audit, not bootstrap,\n"
            "integration or upgrade."
        )
        self.assertIn(route, prompt)
        self.assertLess(prompt.index(route), prompt.index("Inspect the target's native owners"))

    def test_accepts_empty_single_and_outsider_selections_without_auto_selecting_related(
        self,
    ) -> None:
        validate_selection(ROOT, read_json(FIXTURES / "selection-empty.json"))
        api = read_json(FIXTURES / "selection-single-api.json")
        validate_selection(ROOT, api)
        self.assertEqual(api["considered_modules"], ["api-service-contracts"])
        self.assertNotIn("public-api-catalogue", api["considered_modules"])
        rig = read_json(FIXTURES / "selection-single-rig.json")
        validate_selection(ROOT, rig)
        self.assertEqual(rig["considered_modules"], ["device-rig-app-control"])
        outsider = read_json(FIXTURES / "outsider-all-12.json")
        validate_selection(ROOT, outsider, outsider=True)

    def test_rejects_coherent_extra_card(self) -> None:
        _, repository = self.make_repository()
        library = repository / "templates" / "capabilities"
        card = library / "universal-magic.md"
        card.write_text(
            "# Universal magic\n\n- ID: `universal-magic`\n\n"
            "- Source IDs: `testing-feedback-design`.\n",
            encoding="utf-8",
        )
        manifest = self.read_manifest(repository)
        data = card.read_bytes()
        entry = copy.deepcopy(
            next(item for item in manifest["files"] if item.get("module_id") == "testing-feedback")
        )
        entry.update(
            {
                "path": "universal-magic.md",
                "module_id": "universal-magic",
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "related_modules": [],
                "source_refs": ["testing-feedback-design"],
            }
        )
        manifest["files"].append(entry)
        self.write_manifest(repository, manifest)
        with self.assertRaises(CapabilityVerificationError):
            validate_library(repository)

    def test_rejects_unlisted_file_even_with_a_coherent_manifest_entry(self) -> None:
        """Inventory and manifest kinds are closed; a rehashed entry cannot add a file."""
        for relative in ("extra.md", "scripts/check.sh"):
            with self.subTest(relative=relative):
                _, repository = self.make_repository()
                candidate = repository / "templates" / "capabilities" / relative
                candidate.parent.mkdir(parents=True, exist_ok=True)
                candidate.write_text("unlisted\n", encoding="utf-8")
                with self.assertRaisesRegex(
                    CapabilityVerificationError, "manifest inventory differs"
                ):
                    validate_library(repository)
                data = candidate.read_bytes()
                manifest = self.read_manifest(repository)
                manifest["files"].append(
                    {
                        "path": relative,
                        "kind": "extra",
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "bytes": len(data),
                        "mode": "0644",
                        "requires": [],
                        "related_modules": [],
                        "hazards": ["false-proof"],
                    }
                )
                self.write_manifest(repository, manifest)
                with self.assertRaisesRegex(CapabilityVerificationError, "unknown manifest kind"):
                    validate_library(repository)

    def test_rejects_executable_index_or_card(self) -> None:
        for relative in ("README.md", "testing-feedback.md"):
            with self.subTest(relative=relative):
                _, repository = self.make_repository()
                (repository / "templates" / "capabilities" / relative).chmod(0o755)
                with self.assertRaisesRegex(CapabilityVerificationError, "regular non-executable"):
                    validate_library(repository)

    def test_accepts_group_writable_checkout_modes_but_rejects_execute_bits(self) -> None:
        _, repository = self.make_repository()
        library = repository / "templates" / "capabilities"
        for member in library.rglob("*"):
            if member.is_file():
                member.chmod(0o664)
        validate_library(repository)
        (library / "testing-feedback.md").chmod(0o764)
        with self.assertRaisesRegex(CapabilityVerificationError, "regular non-executable"):
            validate_library(repository)

    def test_rejects_undeclared_related_dependency_and_nonempty_default(self) -> None:
        _, repository = self.make_repository()
        manifest = self.read_manifest(repository)
        entry = next(
            item for item in manifest["files"] if item.get("module_id") == "api-service-contracts"
        )
        entry["requires"] = ["public-api-catalogue"]
        self.write_manifest(repository, manifest)
        with self.assertRaises(CapabilityVerificationError):
            validate_library(repository)

        _, repository = self.make_repository()
        manifest = self.read_manifest(repository)
        manifest["default_selection"] = ["testing-feedback"]
        self.write_manifest(repository, manifest)
        with self.assertRaises(CapabilityVerificationError):
            validate_library(repository)

    def test_rejects_card_manifest_source_mismatch_and_broken_local_link(self) -> None:
        _, repository = self.make_repository()
        card = repository / "templates" / "capabilities" / "testing-feedback.md"
        card.write_text(
            card.read_text(encoding="utf-8").replace("`testing-feedback-design`", ""),
            encoding="utf-8",
        )
        self.sync_entry(repository, "testing-feedback.md")
        with self.assertRaises(CapabilityVerificationError):
            validate_library(repository)

        _, repository = self.make_repository()
        readme = repository / "templates" / "capabilities" / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8") + "\n[missing](does-not-exist.md)\n",
            encoding="utf-8",
        )
        self.sync_entry(repository, "README.md")
        with self.assertRaises(CapabilityVerificationError):
            validate_library(repository)

    def test_rejects_an_external_link_in_any_markdown_form(self) -> None:
        card = "testing-feedback.md"
        forms = [
            ("inline", card, "[guide](https://example.org/guide)"),
            ("reference", "README.md", "[guide][up]\n\n[up]: https://example.org/guide"),
            ("autolink", card, "<https://example.org/guide>"),
            ("bare", card, "See ftp://example.org/archive for details."),
            ("scheme-relative", card, "[guide][cdn]\n\n[cdn]: //example.org/guide"),
            ("scheme-relative host", card, '<a href="//localhost:8000/docs">docs</a>'),
            ("www", card, "See _www.example.org_ for details."),
            ("mailto", card, "[contact][owner]\n\n[owner]: mailto:?subject=Feedback"),
            ("tel", card, '<a href="tel:(+1)0000">call</a>'),
            ("javascript", card, "[run][script]\n\n[script]: javascript:(alert(1))"),
            ("data", card, "[note][inline]\n\n[inline]: data:;base64,SGVsbG8="),
            ("email", card, "Write to <owner@163.example> for access."),
            ("irc autolink", card, "Join <irc:example.org/warmboot>."),
            ("file autolink", card, "Open <file:/srv/share/guide.md>."),
            ("reference other scheme", card, "[chat][room]\n\n[room]: irc:example.org/warmboot"),
            ("inline other scheme", card, "[chat](irc:example.org/warmboot)"),
            ("empty inline link", card, "[](irc:example.org/warmboot)"),
            ("empty image", card, "![](file:/srv/share/x.png)"),
            ("empty image with a title", card, '![](file:/srv/share/x.png "Diagram")'),
            ("empty link with a title", card, "[](irc:example.org/warmboot 'Chat')"),
        ]
        for form, relative, markdown in forms:
            with self.subTest(form=form, path=relative):
                _, repository = self.make_repository()
                member = repository / "templates" / "capabilities" / relative
                text = member.read_text(encoding="utf-8")
                member.write_text(f"{text}\n{markdown}\n", encoding="utf-8")
                self.sync_entry(repository, relative)
                with self.assertRaisesRegex(CapabilityVerificationError, "external link"):
                    validate_library(repository)

    def test_accepts_scheme_names_and_package_versions_in_prose(self) -> None:
        _, repository = self.make_repository()
        member = repository / "templates" / "capabilities" / "testing-feedback.md"
        prose = (
            "**Data:** name the `data:`, tel: and javascript: schemes; pin `node@20`, `pkg@1.2` and"
            " `pkg@1.2.3-alpha.beta`; set `raw_data:{}`; edit `pool.d/www.conf`;"
            ' see [section](#www.config), ![](README.md), [index](README.md "Index") and'
            " ![](README.md 'Index (1)'), and [index](README.md \"Index (#1)\")."
        )
        code = "Map with `[](int value) { return value; }`.\n\n```cpp\nauto f = [](int x) { return x; };\n```"
        text = member.read_text(encoding="utf-8")
        member.write_text(f"{text}\n{prose}\n\n{code}\n", encoding="utf-8")
        self.sync_entry(repository, "testing-feedback.md")
        validate_library(repository)

    def test_source_ids_field_must_be_visible_markdown(self) -> None:
        """A Source IDs field hidden in a comment or fence is treated as absent."""
        field = "- Source IDs: `testing-feedback-design`."
        for name, replacement in (
            ("HTML comment", "<!--\n" + field + "\n\n-->"),
            ("fenced code", "```text\n" + field + "\n\n```"),
        ):
            with self.subTest(name=name):
                _, repository = self.make_repository()
                relative = "testing-feedback.md"
                path = repository / "templates" / "capabilities" / relative
                text = path.read_text(encoding="utf-8")
                self.assertIn(field, text)
                path.write_text(text.replace(field, replacement, 1), encoding="utf-8")
                self.sync_entry(repository, relative)
                with self.assertRaisesRegex(
                    CapabilityVerificationError, "exactly one Source IDs field"
                ):
                    validate_library(repository)

    def test_non_markdown_separators_cannot_create_capability_lines(self) -> None:
        """Python-only boundaries stay content in card fields."""
        mutations = (("card Source IDs", "testing-feedback.md", "- Source IDs:"),)
        for separator_name, separator in NON_MARKDOWN_LINE_SEPARATORS:
            for target_name, relative, target in mutations:
                with self.subTest(separator=separator_name, target=target_name):
                    _, repository = self.make_repository()
                    path = repository / "templates/capabilities" / relative
                    text = path.read_text(encoding="utf-8")
                    self.assertIn(target, text)
                    path.write_text(
                        text.replace(target, separator + target, 1),
                        encoding="utf-8",
                    )
                    self.sync_entry(repository, relative)
                    with self.assertRaises(CapabilityVerificationError):
                        validate_library(repository)

    def test_non_markdown_separators_cannot_be_trimmed_from_source_ids(self) -> None:
        """Unicode separators remain material immediately after the field marker."""
        marker = "- Source IDs:"
        for separator_name, separator in NON_MARKDOWN_LINE_SEPARATORS:
            with self.subTest(separator=separator_name):
                _, repository = self.make_repository()
                relative = "testing-feedback.md"
                path = repository / "templates" / "capabilities" / relative
                text = path.read_text(encoding="utf-8")
                self.assertIn(marker, text)
                path.write_text(
                    text.replace(marker, marker + separator, 1),
                    encoding="utf-8",
                )
                self.sync_entry(repository, relative)
                with self.assertRaises(CapabilityVerificationError):
                    validate_library(repository)

    def test_capability_markdown_accepts_commonmark_line_endings(self) -> None:
        """LF, CRLF, and CR remain valid for Markdown capability cards."""
        relative = "testing-feedback.md"
        for name, line_ending in (("LF", b"\n"), ("CRLF", b"\r\n"), ("CR", b"\r")):
            with self.subTest(line_ending=name):
                _, repository = self.make_repository()
                path = repository / "templates/capabilities" / relative
                path.write_bytes(path.read_bytes().replace(b"\n", line_ending))
                self.sync_entry(repository, relative)
                validate_library(repository)

    def test_rejects_noop_privacy_detector_and_unsafe_value(self) -> None:
        with mock.patch.object(capability_oracle, "privacy_findings", return_value=set()):
            with self.assertRaisesRegex(
                CapabilityVerificationError, "privacy detector is ineffective"
            ):
                validate_library(ROOT)

        _, repository = self.make_repository()
        card = repository / "templates" / "capabilities" / "testing-feedback.md"
        card.write_text(
            card.read_text(encoding="utf-8")
            + "\nUnsafe injected value: "
            + capability_oracle.PRIVACY_CANARIES["LOCAL_ABSOLUTE_PATH"]
            + "\n",
            encoding="utf-8",
        )
        self.sync_entry(repository, "testing-feedback.md")
        with self.assertRaisesRegex(CapabilityVerificationError, "unsafe literal"):
            validate_library(repository)

    def test_rejects_selection_that_skips_a_considered_module_or_uses_wrong_disposition(
        self,
    ) -> None:
        selection = read_json(FIXTURES / "selection-single-api.json")
        selection["dispositions"] = []
        with self.assertRaises(CapabilityVerificationError):
            validate_selection(ROOT, selection)

        selection = read_json(FIXTURES / "selection-single-api.json")
        selection["dispositions"][0]["disposition"] = "AUTO-INSTALL"
        with self.assertRaises(CapabilityVerificationError):
            validate_selection(ROOT, selection)

    def test_selection_dispositions_reject_unknown_fields(self) -> None:
        selection = read_json(FIXTURES / "outsider-all-12.json")
        for extra in ({"notes": "unreviewed"}, {"records": {}}):
            with self.subTest(extra=extra):
                candidate = copy.deepcopy(selection)
                candidate["dispositions"][0].update(extra)
                with self.assertRaisesRegex(CapabilityVerificationError, "disposition keys differ"):
                    validate_selection(ROOT, candidate, outsider=True)

        api = read_json(FIXTURES / "selection-single-api.json")
        api["dispositions"][0].update(disposition="ADOPT", notes="unreviewed")
        with self.assertRaisesRegex(CapabilityVerificationError, "disposition keys differ"):
            validate_selection(ROOT, api)

    def test_cli_validates_selections_without_starting_a_process(self) -> None:
        """The validation CLI reads files only; it never starts a target or shell process."""
        with mock.patch("subprocess.run") as run, mock.patch("subprocess.Popen") as popen:
            with mock.patch("builtins.print") as output:
                status = capability_oracle.main(
                    [
                        "--repository",
                        str(ROOT),
                        "--selection",
                        str(FIXTURES / "outsider-all-12.json"),
                        "--outsider",
                        "--fake-cases",
                        str(FIXTURES / "fake-decisions.json"),
                    ]
                )
        self.assertEqual(status, 0, output.call_args_list)
        run.assert_not_called()
        popen.assert_not_called()

    def test_unhashable_json_values_fail_as_verification_errors(self) -> None:
        for mutation in (
            lambda selection: selection.update(considered_modules=[["testing-feedback"]]),
            lambda selection: selection["dispositions"][0].update(module_id=["testing-feedback"]),
            lambda selection: selection["dispositions"][0].update(disposition=["ADOPT"]),
            lambda selection: selection["live_boundary"].update(
                refused_actions=[{"action": "DEPLOY"}]
            ),
        ):
            with self.subTest(mutation=mutation):
                selection = read_json(FIXTURES / "outsider-all-12.json")
                mutation(selection)
                with self.assertRaises(CapabilityVerificationError):
                    validate_selection(ROOT, selection, outsider=True)

        def module(manifest: dict) -> dict:
            return next(
                item for item in manifest["files"] if item.get("module_id") == "testing-feedback"
            )

        def index(manifest: dict) -> dict:
            return next(item for item in manifest["files"] if item["kind"] == "index")

        for mutation in (
            lambda manifest: manifest.update(allowed_dispositions=[["ADOPT"]]),
            lambda manifest: module(manifest).update(related_modules=[["testing-feedback"]]),
            lambda manifest: module(manifest).update(hazards=[["false-proof"]]),
            lambda manifest: module(manifest).update(module_id=["testing-feedback"]),
            lambda manifest: index(manifest).update(source_refs=[["source"]]),
        ):
            with self.subTest(mutation=mutation):
                _, repository = self.make_repository()
                manifest = self.read_manifest(repository)
                mutation(manifest)
                self.write_manifest(repository, manifest)
                with self.assertRaises(CapabilityVerificationError):
                    validate_library(repository)

        cases = read_json(FIXTURES / "fake-decisions.json")
        cases["cases"][0]["operation"] = ["DEPLOY"]
        with self.assertRaises(CapabilityVerificationError):
            capability_oracle.verify_fake_cases(cases)

    def test_manifest_schema_rejects_unknown_key_version_and_shell_templates(self) -> None:
        for mutation in (
            lambda manifest: manifest.update(schema_version=2),
            lambda manifest: manifest.update(schema_version=True),
            lambda manifest: manifest.update(extra={"note": "unreviewed"}),
        ):
            with self.subTest(mutation=mutation):
                _, repository = self.make_repository()
                manifest = self.read_manifest(repository)
                mutation(manifest)
                self.write_manifest(repository, manifest)
                with self.assertRaises(CapabilityVerificationError):
                    validate_library(repository)

        _, repository = self.make_repository()
        (repository / "stray.sh.tmpl").write_text("# inert\n", encoding="utf-8")
        with self.assertRaisesRegex(
            CapabilityVerificationError, "must not contain shell templates"
        ):
            validate_library(repository)

        _, repository = self.make_repository()
        (repository / ".acceptance-work").mkdir()
        (repository / ".acceptance-work" / "scratch.sh.tmpl").write_text(
            "# inert\n", encoding="utf-8"
        )
        validate_library(repository)

    def test_rejects_outsider_live_authority_or_missing_refusal(self) -> None:
        selection = read_json(FIXTURES / "outsider-all-12.json")
        selection["authority"]["device"] = True
        with self.assertRaises(CapabilityVerificationError):
            validate_selection(ROOT, selection, outsider=True)

        selection = read_json(FIXTURES / "outsider-all-12.json")
        selection["live_boundary"]["refused_actions"].pop()
        with self.assertRaises(CapabilityVerificationError):
            validate_selection(ROOT, selection, outsider=True)

    def test_rejects_manifest_identity_extra_keys_and_typed_list_drift(self) -> None:
        mutations = (
            lambda manifest: manifest.update({"library_id": "lookalike-library"}),
            lambda manifest: manifest.update({"authority": "MAY_INSTALL"}),
            lambda manifest: manifest.update({"manifest_self_inventory": "self excluded"}),
            lambda manifest: next(
                item for item in manifest["files"] if item["kind"] == "index"
            ).update({"extra": "unreviewed"}),
            lambda manifest: next(
                item for item in manifest["files"] if item.get("module_id") == "testing-feedback"
            ).update({"note": "unreviewed"}),
            lambda manifest: next(
                item for item in manifest["files"] if item.get("module_id") == "testing-feedback"
            ).update({"hazards": ["false-proof", "false-proof"]}),
            lambda manifest: next(
                item for item in manifest["files"] if item.get("module_id") == "testing-feedback"
            ).update({"source_refs": ["Not Canonical"]}),
        )
        for mutation in mutations:
            _, repository = self.make_repository()
            manifest = self.read_manifest(repository)
            mutation(manifest)
            self.write_manifest(repository, manifest)
            with self.assertRaises(CapabilityVerificationError):
                validate_library(repository)

    def test_rejects_source_catalog_rights_payload_and_invalid_identity(self) -> None:
        mutations = (
            lambda d: d["sources"][0]["rights"].update(spdx="LicenseRef-Synthetic-Restricted"),
            lambda d: d["entries"][0].update(rights={"spdx": "MIT"}),
            lambda d: d["sources"][0].update(private_endpoint="invented endpoint"),
            lambda d: d["sources"][0].update(sha256="not-a-digest"),
            lambda d: d["sources"][0]["rights"].update(spdx="Apache-2.0"),
            lambda d: d["entries"][0].update(source_id="unknown"),
        )
        for mutation in mutations:
            _, repository = self.make_repository()
            path = repository / "docs/capability-sources.json"
            document = read_json(path)
            mutation(document)
            self.write_json(path, document)
            with self.assertRaises(CapabilityVerificationError):
                validate_library(repository)

    def test_rejects_synthetic_source_admission_and_rights_upgrade(self) -> None:
        _, repository = self.make_repository()
        synthetic = read_json(FIXTURES / "synthetic-restricted-sources.json")
        self.write_json(repository / "docs/capability-sources.json", synthetic)
        with self.assertRaises(CapabilityVerificationError):
            validate_library(repository)
        synthetic["sources"][0]["rights"]["spdx"] = "MIT"
        with self.assertRaises(CapabilityVerificationError):
            capability_oracle.validate_source_catalog(synthetic)

    def test_repository_json_inputs_reject_symlinked_parent_directories(self) -> None:
        cases = (
            "templates/capabilities/MANIFEST.json",
            "docs/capability-sources.json",
            "acceptance/fixtures/capability-library/synthetic-restricted-sources.json",
        )
        for relative in cases:
            with self.subTest(relative=relative):
                _, repository = self.make_repository()
                member = repository / relative
                parent = member.parent
                real_parent = parent.with_name(parent.name + "-real")
                parent.rename(real_parent)
                parent.symlink_to(real_parent.name, target_is_directory=True)
                with self.assertRaisesRegex(CapabilityVerificationError, "traverse a symlink"):
                    load_repository_json(repository, Path(relative), relative)

    def test_repository_json_inputs_reject_escaped_resolution_and_outside_paths(self) -> None:
        _, repository = self.make_repository()
        outside = Path(repository.parent) / "outside-json"
        outside.mkdir()
        (outside / "MANIFEST.json").write_text("{}\n", encoding="utf-8")
        owned_parent = repository / "acceptance" / "fixtures" / "capability-library"
        shutil.rmtree(owned_parent)
        owned_parent.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(CapabilityVerificationError):
            load_repository_json(
                repository,
                Path("acceptance/fixtures/capability-library/MANIFEST.json"),
                "synthetic source manifest",
            )
        with self.assertRaisesRegex(CapabilityVerificationError, "beneath the attested repository"):
            load_repository_json(repository, outside / "MANIFEST.json", "outside JSON")

    def test_repository_json_inputs_reject_same_and_different_duplicate_keys_recursively(
        self,
    ) -> None:
        _, repository = self.make_repository()
        catalog_path = repository / "docs" / "capability-sources.json"
        catalog_text = catalog_path.read_text(encoding="utf-8")
        catalog_needle = '        "spdx": "MIT"\n'
        self.assertIn(catalog_needle, catalog_text)
        catalog_path.write_text(
            catalog_text.replace(
                catalog_needle,
                '        "spdx": "MIT",\n        "spdx": "Apache-2.0"\n',
                1,
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(CapabilityVerificationError, "duplicate JSON key.*spdx"):
            validate_library(repository)

        _, repository = self.make_repository()
        manifest_path = repository / "templates" / "capabilities" / "MANIFEST.json"
        manifest_text = manifest_path.read_text(encoding="utf-8")
        manifest_needle = '      "source_refs": []\n'
        self.assertIn(manifest_needle, manifest_text)
        manifest_path.write_text(
            manifest_text.replace(
                manifest_needle,
                '      "source_refs": [],\n      "source_refs": []\n',
                1,
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(CapabilityVerificationError, "duplicate JSON key.*source_refs"):
            validate_library(repository)

        relative = "acceptance/fixtures/capability-library/synthetic-restricted-sources.json"
        _, repository = self.make_repository()
        path = repository / relative
        text = path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("{\n"))
        path.write_text(
            text.replace(
                "{\n",
                '{\n  "duplicate_canary": false,\n  "duplicate_canary": false,\n',
                1,
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            CapabilityVerificationError, "duplicate JSON key.*duplicate_canary"
        ):
            load_repository_json(repository, Path(relative), relative)


if __name__ == "__main__":
    unittest.main()
