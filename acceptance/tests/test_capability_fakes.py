"""Exercise bounded fake decisions and the repository's absence of shell source and shell execution."""

from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

from acceptance.capability_oracle import (
    UNTRACKED_PARTS,
    CapabilityVerificationError,
    verify_fake_cases,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "acceptance" / "fixtures" / "capability-library" / "fake-decisions.json"


class CapabilityFakeTests(unittest.TestCase):
    def cases(self) -> dict:
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fake_decisions_cover_hazard_stops_and_api_failures(self) -> None:
        observed = verify_fake_cases(self.cases())
        self.assertEqual(len(observed), 10)
        self.assertTrue(all(item["scope"] == "LOCAL_FAKE_ONLY" for item in observed))
        self.assertTrue(all(item["live_proof"] == "UNPROVED" for item in observed))
        by_id = {item["case_id"]: item for item in observed}
        self.assertEqual(by_id["api-429-bounded-retry-recovers"]["attempts"], 2)
        self.assertEqual(by_id["api-5xx-bounded-retry-exhausted"]["decision"], "FAIL_CLOSED")
        self.assertEqual(by_id["deploy-without-authority"]["decision"], "REFUSE_AUTHORITY")

    def test_rejects_expected_decision_that_does_not_match_observation(self) -> None:
        document = self.cases()
        document["cases"][0]["expected"]["decision"] = "PASS_FAKE"
        with self.assertRaises(CapabilityVerificationError):
            verify_fake_cases(document)

    def test_rejects_boolean_or_float_expected_attempts(self) -> None:
        """Numeric equality cannot turn fake retry counts into non-integer evidence."""
        cases = (
            ("false", "deploy-without-authority", False),
            ("zero float", "deploy-without-authority", 0.0),
            ("true", "api-401-stops", True),
            ("one float", "api-401-stops", 1.0),
        )
        for name, case_id, value in cases:
            with self.subTest(name=name):
                document = self.cases()
                case = next(item for item in document["cases"] if item["case_id"] == case_id)
                case["expected"]["attempts"] = value
                with self.assertRaisesRegex(CapabilityVerificationError, "expected attempts"):
                    verify_fake_cases(document)

    def test_rejects_float_or_boolean_status_sequence_element(self) -> None:
        """Only exact int or str statuses may drive the fake decision table."""
        cases = (
            (
                "float 200.0",
                "api-429-bounded-retry-recovers",
                [429, 200.0],
                {
                    "attempts": 2,
                    "decision": "PASS_FAKE",
                    "live_proof": "UNPROVED",
                    "reason": "RECOVERED_AFTER_BOUNDED_RETRY",
                },
            ),
            (
                "boolean True",
                "api-401-stops",
                [True],
                {
                    "attempts": 1,
                    "decision": "FAIL_CLOSED",
                    "live_proof": "UNPROVED",
                    "reason": "UNEXPECTED_FAKE_STATUS",
                },
            ),
        )
        for name, case_id, sequence, expected in cases:
            with self.subTest(name=name):
                document = self.cases()
                case = next(item for item in document["cases"] if item["case_id"] == case_id)
                case["status_sequence"] = sequence
                case["expected"] = expected
                with self.assertRaisesRegex(CapabilityVerificationError, "status_sequence"):
                    verify_fake_cases(document)

    def test_rejects_live_case_or_retry_budget_above_bound(self) -> None:
        document = self.cases()
        document["cases"][0]["simulation"] = False
        with self.assertRaises(CapabilityVerificationError):
            verify_fake_cases(document)

        document = self.cases()
        api = next(case for case in document["cases"] if case["operation"] == "API_FAKE")
        api["retry_limit"] = 99
        with self.assertRaises(CapabilityVerificationError):
            verify_fake_cases(document)

    def test_repository_has_no_shell_source_and_no_shell_execution(self) -> None:
        """No shell source ships, the oracle starts no process and no code enables a shell."""
        shell_paths = set()
        for path in ROOT.rglob("*"):
            relative = path.relative_to(ROOT)
            if UNTRACKED_PARTS.intersection(relative.parts):
                continue
            if not path.is_file():
                continue
            if path.suffix in {".sh", ".tmpl"}:
                shell_paths.add(relative.as_posix())
            if path.suffix != ".py" and relative.as_posix() != "bin/warmboot":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
                for keyword in call.keywords:
                    if keyword.arg == "shell":
                        self.assertIsInstance(keyword.value, ast.Constant, str(relative))
                        self.assertIs(keyword.value.value, False, str(relative))
                if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
                    self.assertNotIn(
                        (call.func.value.id, call.func.attr),
                        {("os", "system"), ("os", "popen")},
                        str(relative),
                    )
            if relative.as_posix() == "acceptance/capability_oracle.py":
                # The oracle validates structure only; it imports no process module.
                imported = {
                    alias.name.split(".")[0]
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Import)
                    for alias in node.names
                } | {
                    (node.module or "").split(".")[0]
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom)
                }
                self.assertFalse(
                    imported & {"subprocess", "os", "pty", "asyncio", "multiprocessing"}
                )
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute):
                            self.assertNotIn(
                                node.func.attr, {"write", "write_text", "write_bytes", "open"}
                            )
                        elif isinstance(node.func, ast.Name):
                            self.assertNotIn(node.func.id, {"open", "eval", "exec"})
        self.assertEqual(shell_paths, set())


if __name__ == "__main__":
    unittest.main()
