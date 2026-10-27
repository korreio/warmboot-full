"""Every oracle reports a path through a symlink loop as one FAIL, on every supported Python."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from acceptance import (
    capability_oracle,
    kickoff_oracle,
    oracle,
    release_manifest,
    self_improvement_oracle,
    source_comprehension_oracle,
    upgrade_oracle,
)

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "acceptance" / "fixtures" / "baseline"
SELF_IMPROVEMENT = ROOT / "acceptance" / "fixtures" / "self-improvement-package"


class SymlinkLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.loop = self.root / "loop"
        self.loop.symlink_to("loop")

    def test_command_lines_report_a_loop_path_as_fail(self) -> None:
        response = self.root / "result.json"
        # A valid response, so the fresh-agent oracle reaches the looped project.
        response.write_text(json.dumps(oracle.expected_response(BASELINE)), encoding="utf-8")
        loop = str(self.loop)
        package = str(SELF_IMPROVEMENT)
        planner = str(SELF_IMPROVEMENT / "planner-result.json")
        release = ["--manifest", "release-manifest.json", "--expected-policy-sha256", "0" * 64]
        release += ["--expected-release-id", "candidate", "--expected-declared-ref", "candidate"]
        cases = {
            "fresh-agent project": (oracle.main, ["--project", loop, "--result", str(response)]),
            "source-comprehension case": (source_comprehension_oracle.main, [loop]),
            "upgrade package": (upgrade_oracle.main, ["--package", loop, "--result", "UPGRADE.md"]),
            "self-improvement package": (
                self_improvement_oracle.main,
                ["--package", loop, "--result", planner],
            ),
            "self-improvement repository": (
                self_improvement_oracle.main,
                ["--package", package, "--result", planner, "--repository", loop],
            ),
            "release repository": (release_manifest.main, ["--repository", loop, *release]),
            "kickoff package": (kickoff_oracle.main, ["--package", str(self.loop / "x")]),
        }
        for name, (main, arguments) in cases.items():
            with self.subTest(case=name):
                stderr = io.StringIO()
                with (
                    contextlib.redirect_stderr(stderr),
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    try:
                        status = main(arguments)
                    except SystemExit as exit_:  # The source-comprehension CLI exits via argparse.
                        status = exit_.code
                self.assertEqual(status, 1)
                self.assertTrue(stderr.getvalue().startswith("FAIL:"), stderr.getvalue())
                self.assertEqual(len(stderr.getvalue().splitlines()), 1, stderr.getvalue())
                if name == "fresh-agent project":  # Reached the project, not the response keys.
                    self.assertIn("project", stderr.getvalue())

    def test_member_paths_through_a_loop_fail_as_verification_errors(self) -> None:
        with self.assertRaisesRegex(capability_oracle.CapabilityVerificationError, "local link"):
            capability_oracle._validate_local_links(self.root, "card.md", "[x](loop)")
        with self.assertRaisesRegex(
            source_comprehension_oracle.SourceComprehensionError, "probe cannot be checked"
        ):
            source_comprehension_oracle._relative_file(self.root, "loop/x", "probe")


if __name__ == "__main__":
    unittest.main()
