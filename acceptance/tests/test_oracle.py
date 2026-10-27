"""Exercise the baseline oracle's bounded fixture and strict JSON ingress contract."""

import copy
import io
import json
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

from acceptance.oracle import (
    TEST_COMMAND,
    VerificationError,
    expected_response,
    main,
    verify,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "acceptance" / "fixtures" / "baseline"


class OracleTests(unittest.TestCase):
    @staticmethod
    def snapshot(project: Path) -> dict[str, tuple[str, bytes | None]]:
        observed: dict[str, tuple[str, bytes | None]] = {}
        for path in sorted(project.rglob("*")):
            relative = path.relative_to(project).as_posix()
            if path.is_dir():
                observed[relative] = ("directory", None)
            elif path.is_file():
                observed[relative] = ("file", path.read_bytes())
            else:
                observed[relative] = ("other", None)
        return observed

    def test_accepts_exact_evidence_derived_response(self) -> None:
        verify(FIXTURE, expected_response(FIXTURE))

    def test_rejects_extra_key(self) -> None:
        response = expected_response(FIXTURE)
        response["commentary"] = "looks good"
        with self.assertRaises(VerificationError):
            verify(FIXTURE, response)

    def test_rejects_stale_claim_reported_current(self) -> None:
        response = copy.deepcopy(expected_response(FIXTURE))
        response["handoff"]["freshness"] = "CURRENT"
        with self.assertRaises(VerificationError):
            verify(FIXTURE, response)

    def test_rejects_boolean_schema_version(self) -> None:
        response = expected_response(FIXTURE)
        response["schema_version"] = True
        with self.assertRaises(VerificationError):
            verify(FIXTURE, response)

    def test_rejects_numeric_authority_flags(self) -> None:
        """Exact authority booleans do not admit Python's numeric equivalents."""
        for key, value in (("may_edit", 0), ("may_commit", 0), ("may_publish", 0)):
            with self.subTest(key=key):
                response = expected_response(FIXTURE)
                response["authority"][key] = value
                with self.assertRaisesRegex(VerificationError, "exact booleans"):
                    verify(FIXTURE, response)

    def test_cli_rejects_duplicate_unsafe_authority_from_file_and_stdin(self) -> None:
        """Both CLI ingress paths reject an unsafe duplicate before safe authority."""
        response = json.dumps(expected_response(FIXTURE), indent=2) + "\n"
        duplicate = response.replace(
            '  "authority": {',
            '  "authority": {"may_edit": true, "may_commit": true, '
            '"may_publish": true},\n  "authority": {',
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "response.json"
            result_path.write_text(duplicate, encoding="utf-8")
            self.assertEqual(main(["--project", str(FIXTURE), "--result", str(result_path)]), 1)
        with patch("acceptance.oracle.sys.stdin", io.StringIO(duplicate)):
            self.assertEqual(main(["--project", str(FIXTURE), "--result", "-"]), 1)

    def test_rejects_missing_or_incorrect_testing_decision_owner(self) -> None:
        for replacement in ("", "- Testing decision owner: `somebody-else`\n"):
            with self.subTest(replacement=replacement):
                with tempfile.TemporaryDirectory() as directory:
                    project = Path(directory) / "project"
                    shutil.copytree(FIXTURE, project)
                    task_path = project / "TASK.md"
                    task = task_path.read_text(encoding="utf-8")
                    task_path.write_text(
                        task.replace(
                            "- Testing decision owner: `fixture-target-owner`\n",
                            replacement,
                        ),
                        encoding="utf-8",
                    )
                    with self.assertRaises(VerificationError):
                        expected_response(project)

    def test_rejects_parent_traversal_source_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            shutil.copytree(FIXTURE, project)
            handoff = (project / "HANDOFF.md").read_text(encoding="utf-8")
            (project / "HANDOFF.md").write_text(
                handoff.replace("`src/labels.py`", "`../labels.py`"), encoding="utf-8"
            )
            with self.assertRaises(VerificationError):
                expected_response(project)

    def test_rejects_symlinked_source_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            shutil.copytree(FIXTURE, project)
            outside = Path(directory) / "outside.py"
            outside.write_text("VALUE = 'outside'\n", encoding="utf-8")
            source = project / "src" / "labels.py"
            source.unlink()
            source.symlink_to(outside)
            with self.assertRaises(VerificationError):
                expected_response(project)

    def test_names_a_missing_or_non_file_source(self) -> None:
        cases = (("missing", "does not exist"), ("directory", "must be a regular file"))
        for kind, message in cases:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                project = Path(directory) / "project"
                shutil.copytree(FIXTURE, project)
                source = project / "src" / "labels.py"
                source.unlink()
                if kind == "directory":
                    source.mkdir()
                with self.assertRaisesRegex(VerificationError, f"handoff source {message}"):
                    expected_response(project)

    def test_names_a_source_path_that_cannot_be_checked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            shutil.copytree(FIXTURE, project)
            handoff = (project / "HANDOFF.md").read_text(encoding="utf-8")
            (project / "HANDOFF.md").write_text(
                handoff.replace("`src/labels.py`", f"`src/{'a' * 300}`"), encoding="utf-8"
            )
            with self.assertRaisesRegex(VerificationError, "handoff source cannot be checked"):
                expected_response(project)

    def test_cli_reports_unreadable_or_undecodable_task_as_fail(self) -> None:
        kinds = ["not UTF-8"] if os.geteuid() == 0 else ["unreadable", "not UTF-8"]
        for kind in kinds:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                project = Path(directory) / "project"
                shutil.copytree(FIXTURE, project)
                result_path = Path(directory) / "result.json"
                response = json.dumps(expected_response(project)) + "\n"
                result_path.write_text(response, encoding="utf-8")
                task = project / "TASK.md"
                if kind == "unreadable":
                    task.chmod(0)
                else:
                    task.write_bytes(b"\xff\xfe not text\n")
                stderr = io.StringIO()
                try:
                    with redirect_stderr(stderr):
                        status = main(["--project", str(project), "--result", str(result_path)])
                finally:
                    task.chmod(0o644)
                self.assertEqual(status, 1)
                self.assertTrue(stderr.getvalue().startswith("FAIL:"), stderr.getvalue())

    def test_cli_rejects_non_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "result.txt"
            result_path.write_text("```json\n{}\n```\n", encoding="utf-8")
            self.assertEqual(main(["--project", str(FIXTURE), "--result", str(result_path)]), 1)

    def test_cli_rejects_utf16_encoded_response(self) -> None:
        """UTF-16/BOM ingress is refused like the six sibling UTF-8 readers."""
        response = json.dumps(expected_response(FIXTURE), indent=2) + "\n"
        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "response.json"
            result_path.write_text(response, encoding="utf-16")
            self.assertEqual(main(["--project", str(FIXTURE), "--result", str(result_path)]), 1)

    def test_read_only_native_command_passes_without_mutating_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            shutil.copytree(
                FIXTURE,
                project,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            before = self.snapshot(project)
            self.assertFalse(
                any(
                    "__pycache__" in Path(relative).parts or relative.endswith(".pyc")
                    for relative in before
                )
            )

            result = subprocess.run(
                shlex.split(TEST_COMMAND),
                cwd=project,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            after = self.snapshot(project)
            self.assertEqual(after, before)
            self.assertFalse(
                any(
                    "__pycache__" in Path(relative).parts or relative.endswith(".pyc")
                    for relative in after
                )
            )


if __name__ == "__main__":
    unittest.main()
