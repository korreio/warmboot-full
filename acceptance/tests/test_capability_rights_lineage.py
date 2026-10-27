"""Check local design bindings and inherited synthetic rights restrictions."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from acceptance import capability_oracle
from acceptance.capability_oracle import (
    CapabilityVerificationError,
    effective_source_claim,
    validate_library,
)

ROOT = Path(__file__).resolve().parents[2]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class NormalizedLineageTests(unittest.TestCase):
    def make_repository(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        repository = Path(temporary.name) / "repository"
        (repository / "docs").mkdir(parents=True)
        shutil.copytree(ROOT / "templates/capabilities", repository / "templates/capabilities")
        (repository / "acceptance").mkdir()
        shutil.copy2(
            ROOT / "acceptance/capability-outsider.md",
            repository / "acceptance/capability-outsider.md",
        )
        for name in (
            "capability-sources.json",
            "capability-design.md",
            "documentation-architecture.md",
        ):
            shutil.copy2(ROOT / "docs" / name, repository / "docs" / name)
        return repository

    @staticmethod
    def write_json(path: Path, document: dict) -> None:
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    def mutate_catalog(self, mutation) -> None:
        repository = self.make_repository()
        path = repository / "docs/capability-sources.json"
        document = read_json(path)
        mutation(document)
        self.write_json(path, document)
        with self.assertRaises(CapabilityVerificationError):
            validate_library(repository)

    def sync_card(self, repository: Path, module: str) -> None:
        path = repository / "templates/capabilities" / (module + ".md")
        manifest_path = repository / "templates/capabilities/MANIFEST.json"
        manifest = read_json(manifest_path)
        entry = next(row for row in manifest["files"] if row.get("module_id") == module)
        entry.update(
            bytes=len(path.read_bytes()), sha256=hashlib.sha256(path.read_bytes()).hexdigest()
        )
        self.write_json(manifest_path, manifest)

    def test_rejects_identity_digest_coverage_and_unknown_fields(self) -> None:
        for mutation in (
            lambda d: d["sources"][0].update(sha256="f" * 64),
            lambda d: d["sources"][0].update(path="../escaping-design.md"),
            lambda d: d["sources"][0].update(object_id="invented identity"),
            lambda d: d["entries"].pop(),
            lambda d: d["entries"].append(copy.deepcopy(d["entries"][0])),
            lambda d: d["entries"][0].update(source_id="unknown"),
            lambda d: d["entries"][0].update(rationale=""),
            lambda d: d["sources"].append(copy.deepcopy(d["sources"][0])),
        ):
            with self.subTest(mutation=mutation):
                self.mutate_catalog(mutation)

    def test_rejects_rights_overrides_payload_and_privacy_fields(self) -> None:
        for mutation in (
            lambda d: d["sources"][0]["rights"].update(spdx="LicenseRef-Synthetic-Restricted"),
            lambda d: d["sources"][0]["rights"].update(spdx="unknown"),
            lambda d: d["entries"][0].update(spdx="MIT"),
            lambda d: d["entries"][0].update(rights={"spdx": "MIT"}),
            lambda d: d["sources"][0].update(private_capture="fictional capture"),
            lambda d: d["entries"][0].update(payload="invented bytes"),
        ):
            with self.subTest(mutation=mutation):
                self.mutate_catalog(mutation)

    def test_rejects_missing_dangling_duplicate_and_noncanonical_card_sources(self) -> None:
        for field in (
            "- Sources: `testing-feedback-design`.",
            "- Source IDs: `unknown-design`.",
            "- Source IDs: `testing-feedback-design`, `testing-feedback-design`.",
            "- Source IDs: `Not Canonical`.",
            "- Source IDs: .",
            "- Source IDs: `testing-feedback-design`.\n- Source IDs: `testing-feedback-design`.",
        ):
            with self.subTest(field=field):
                repository = self.make_repository()
                card = repository / "templates/capabilities/testing-feedback.md"
                card.write_text(
                    card.read_text().replace("- Source IDs: `testing-feedback-design`.", field)
                )
                self.sync_card(repository, "testing-feedback")
                with self.assertRaises(CapabilityVerificationError):
                    validate_library(repository)

    def test_rejects_semantic_cross_card_swap_with_complete_inventory(self) -> None:
        repository = self.make_repository()
        for module, replacement in (
            ("quality-evaluation", "device-rig-app-control"),
            ("device-rig-app-control", "quality-evaluation"),
        ):
            card = repository / "templates/capabilities" / (module + ".md")
            card.write_text(
                card.read_text().replace("`" + module + "-design`", "`" + replacement + "-design`")
            )
            self.sync_card(repository, module)
        with self.assertRaisesRegex(CapabilityVerificationError, "module/source mapping"):
            validate_library(repository)

    def test_rejects_symlinked_catalog_parent_and_design_member(self) -> None:
        repository = self.make_repository()
        design = repository / "docs/capability-design.md"
        moved = design.with_name("design-real.md")
        design.rename(moved)
        design.symlink_to(moved.name)
        with self.assertRaisesRegex(CapabilityVerificationError, "traverse a symlink"):
            validate_library(repository)
        repository = self.make_repository()
        docs = repository / "docs"
        docs.rename(repository / "docs-real")
        docs.symlink_to("docs-real", target_is_directory=True)
        with self.assertRaisesRegex(CapabilityVerificationError, "traverse a symlink"):
            validate_library(repository)

    def test_source_path_that_cannot_be_checked_fails_closed(self) -> None:
        repository = self.make_repository()
        catalog = read_json(repository / "docs/capability-sources.json")
        catalog["sources"][0]["path"] = f"docs/{'a' * 300}"
        self.write_json(repository / "docs/capability-sources.json", catalog)
        with self.assertRaisesRegex(CapabilityVerificationError, "source cannot be checked"):
            validate_library(repository)

    def test_resolves_current_design_and_rejects_stale_bytes_then_accepts_refresh(self) -> None:
        catalog = read_json(ROOT / "docs/capability-sources.json")
        claims = [effective_source_claim(catalog, row["id"]) for row in catalog["entries"]]
        self.assertEqual(len(claims), 12)
        self.assertTrue(all(row["kind"] == "TOOLKIT-LOCAL" for row in claims))
        self.assertTrue(all(row["rights"] == {"spdx": "MIT"} for row in claims))
        repository = self.make_repository()
        design = repository / "docs/capability-design.md"
        design.write_text(design.read_text() + "\nLocal design clarification.\n")
        with self.assertRaisesRegex(CapabilityVerificationError, "byte/digest mismatch"):
            validate_library(repository)
        catalog["sources"][0]["sha256"] = hashlib.sha256(design.read_bytes()).hexdigest()
        self.write_json(repository / "docs/capability-sources.json", catalog)
        validate_library(repository)

    def test_synthetic_restrictions_inherit_and_cannot_upgrade(self) -> None:
        catalog = read_json(
            ROOT / "acceptance/fixtures/capability-library/synthetic-restricted-sources.json"
        )
        claim = effective_source_claim(catalog, "testing-feedback-design")
        self.assertEqual(claim["kind"], "SYNTHETIC")
        self.assertEqual(claim["rights"], {"spdx": "LicenseRef-Synthetic-Restricted"})
        for mutate in (
            lambda d: d["sources"][0]["rights"].update(spdx="Apache-2.0"),
            lambda d: d["entries"][0].update(rights={"spdx": "MIT"}),
            lambda d: d["sources"][0]["rights"].update(spdx="MIT"),
        ):
            altered = copy.deepcopy(catalog)
            mutate(altered)
            with self.assertRaises(CapabilityVerificationError):
                capability_oracle.validate_source_catalog(altered)


if __name__ == "__main__":
    unittest.main()
