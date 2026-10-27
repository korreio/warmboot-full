"""Strict standard-library oracle for the fixed fresh-agent JSON response."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

if __package__:
    from .strict_json import DuplicateJsonKeyError
    from .strict_json import loads as strict_json_loads
else:
    from strict_json import DuplicateJsonKeyError
    from strict_json import loads as strict_json_loads


EXPECTED_TASK_KEYS = {
    "path",
    "status",
    "coordinator",
    "git_holder",
    "testing_decision_owner",
    "publication",
}
EXPECTED_HANDOFF_KEYS = {
    "path",
    "source_path",
    "claimed_sha256",
    "actual_sha256",
    "freshness",
    "evidence_state",
    "next_action",
    "test_command",
}
EXPECTED_AUTHORITY_KEYS = {"may_edit", "may_commit", "may_publish"}
EXPECTED_TOP_LEVEL_KEYS = {
    "schema_version",
    "task",
    "handoff",
    "authority",
    "decision",
}
SHA256_RE = re.compile(r"[0-9a-f]{64}")
TEST_COMMAND = "python3 -B -m unittest discover -s tests -v"


class VerificationError(ValueError):
    """Raised when a response or fixture violates the acceptance contract."""


def _field(document: str, name: str) -> str:
    match = re.search(rf"^- {re.escape(name)}: `([^`]+)`$", document, re.MULTILINE)
    if not match:
        raise VerificationError(f"missing fixture field: {name}")
    return match.group(1)


def _claimed_check(document: str) -> str:
    match = re.search(r"^- Claimed check: `([^`]+)` passed$", document, re.MULTILINE)
    if not match:
        raise VerificationError("missing fixture field: Claimed check")
    return match.group(1)


def _exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise VerificationError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise VerificationError(
            f"{label} keys differ: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )
    return value


def expected_response(project: Path) -> dict[str, Any]:
    """Return the one correct fresh-agent response for the project's task and handoff."""
    task_path = project / "TASK.md"
    handoff_path = project / "HANDOFF.md"
    if not task_path.is_file() or not handoff_path.is_file():
        raise VerificationError("project must contain TASK.md and HANDOFF.md")

    task = task_path.read_text(encoding="utf-8")
    handoff = handoff_path.read_text(encoding="utf-8")
    if f"```sh\n{TEST_COMMAND}\n```" not in task:
        raise VerificationError("task native check differs from the read-only command")
    if _claimed_check(handoff) != TEST_COMMAND:
        raise VerificationError("handoff claimed check differs from the read-only command")
    coordinator = _field(task, "Coordinator")
    testing_decision_owner = _field(task, "Testing decision owner")
    if testing_decision_owner != coordinator:
        raise VerificationError("testing decision owner must be the named fixture coordinator")
    source_relative = _field(handoff, "Source path")
    declared = Path(source_relative)
    if (
        declared.is_absolute()
        or declared.as_posix() != source_relative
        or any(part in {"", ".", ".."} for part in declared.parts)
    ):
        raise VerificationError("handoff source path must be canonical project-relative")
    source_path = project
    # Before Python 3.14, is_symlink() raises for an over-long or unsearchable component.
    try:
        for part in declared.parts:
            source_path = source_path / part
            if source_path.is_symlink():
                raise VerificationError("handoff source path must not traverse a symlink")
        resolved_source = source_path.resolve(strict=True)
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise VerificationError(f"handoff source does not exist: {source_relative}") from exc
    except OSError as exc:
        raise VerificationError(f"handoff source cannot be checked: {exc.strerror}") from exc
    try:
        resolved_source.relative_to(project.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise VerificationError("handoff source must resolve inside the project") from exc
    if not resolved_source.is_file():
        raise VerificationError(f"handoff source must be a regular file: {source_relative}")

    claimed = _field(handoff, "Claimed SHA-256")
    if not SHA256_RE.fullmatch(claimed):
        raise VerificationError("fixture claimed SHA-256 is not lowercase hexadecimal")
    actual = hashlib.sha256(resolved_source.read_bytes()).hexdigest()
    if claimed == actual:
        raise VerificationError("acceptance fixture must contain a stale SHA-256 claim")

    return {
        "schema_version": 1,
        "task": {
            "path": "TASK.md",
            "status": _field(task, "Status"),
            "coordinator": coordinator,
            "git_holder": _field(task, "Git holder"),
            "testing_decision_owner": testing_decision_owner,
            "publication": _field(task, "Publication"),
        },
        "handoff": {
            "path": "HANDOFF.md",
            "source_path": source_relative,
            "claimed_sha256": claimed,
            "actual_sha256": actual,
            "freshness": "STALE",
            "evidence_state": _field(handoff, "Evidence state"),
            "next_action": "RERUN_NOW",
            "test_command": TEST_COMMAND,
        },
        "authority": {
            "may_edit": False,
            "may_commit": False,
            "may_publish": False,
        },
        "decision": "RERUN_REQUIRED",
    }


def verify(project: Path, response: Any) -> None:
    """Check a fresh-agent response against the expected one, raising VerificationError."""
    response = _exact_keys(response, EXPECTED_TOP_LEVEL_KEYS, "response")
    _exact_keys(response["task"], EXPECTED_TASK_KEYS, "task")
    _exact_keys(response["handoff"], EXPECTED_HANDOFF_KEYS, "handoff")
    _exact_keys(response["authority"], EXPECTED_AUTHORITY_KEYS, "authority")
    if type(response["schema_version"]) is not int or response["schema_version"] != 1:
        raise VerificationError("schema_version must be integer 1")
    if any(
        type(response["authority"][key]) is not bool
        for key in ("may_edit", "may_commit", "may_publish")
    ):
        raise VerificationError("authority flags must be exact booleans")

    expected = expected_response(project)
    if response != expected:
        raise VerificationError(
            "response does not match repository evidence: "
            + json.dumps({"expected": expected, "actual": response}, sort_keys=True)
        )


def _load_json(path: str) -> Any:
    try:
        if path == "-":
            return strict_json_loads(sys.stdin.read())
        return strict_json_loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateJsonKeyError) as exc:
        raise VerificationError(f"invalid JSON response: {exc}") from exc


def _resolve_argument(path: Path, label: str) -> Path:
    """Resolve a command-line path, reporting a symlink loop as a verification failure."""
    try:
        return path.resolve()
    except RuntimeError as exc:  # Python 3.11 and 3.12 report a symlink loop this way.
        raise VerificationError(f"{label} is a symlink loop: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    """Run the command line and return the exit code."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--result", required=True, help="JSON file, or - for stdin")
    args = parser.parse_args(argv)

    try:
        verify(_resolve_argument(args.project, "project"), _load_json(args.result))
    except (OSError, UnicodeDecodeError, VerificationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({"status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
