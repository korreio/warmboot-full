"""Deterministic structural oracle for Warmboot self-improvement planning.

This oracle proves only that a receipt matches fixed repository/fixture evidence. It
does not prove live agent discovery, provider behavior, mutation, Git or release work.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

if __package__:
    from .release_manifest import (
        ReleaseManifestVerificationError,
    )
    from .release_manifest import (
        verify_illustrative_manifest as _verify_illustrative_manifest,
    )
    from .release_manifest import (
        verify_release_manifest as _verify_release_manifest,
    )
    from .strict_json import DuplicateJsonKeyError
    from .strict_json import loads as strict_json_loads
    from .unicode_policy import (
        is_synthetic_ignorable,
        is_unsafe_evidence_character,
        nfkc_casefold,
    )
else:
    from release_manifest import (  # type: ignore[no-redef]
        ReleaseManifestVerificationError,
    )
    from release_manifest import (
        verify_illustrative_manifest as _verify_illustrative_manifest,
    )
    from release_manifest import (
        verify_release_manifest as _verify_release_manifest,
    )
    from strict_json import DuplicateJsonKeyError
    from strict_json import loads as strict_json_loads
    from unicode_policy import (  # type: ignore[no-redef]
        is_synthetic_ignorable,
        is_unsafe_evidence_character,
        nfkc_casefold,
    )


SHA256_RE = re.compile(r"[0-9a-f]{64}")
GIT_OID_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
REQUIRED_CONTEXT = [
    "MAINTAINING.md",
    "ROLE-INDEX.md",
    "docs/maintainer-system-map.md",
    "docs/engineering-standards.md",
    "docs/testing.md",
    "docs/invariants.md",
    "docs/adoption-disposition.md",
    "docs/adr/",
    "docs/plans/warmboot-build-plan.md",
    "CHANGELOG.md",
    "BUGFIXES.md",
    "docs/release.md",
]
EXPLORATION_CONCERN_OWNERS = {
    "objective_context": "context-language-tooling-owner",
    "language_runtime": "context-language-tooling-owner",
    "stack_portfolio": "stack-architecture-owner",
    "tooling": "context-language-tooling-owner",
    "architecture_risk_privacy": "stack-architecture-owner",
    "testing_bootstrap_release": "testing-bootstrap-release-owner",
}
EXPLORATION_OWNERS = list(dict.fromkeys(EXPLORATION_CONCERN_OWNERS.values()))
TOPOLOGY_KEYS = {
    "classification",
    "coordinator",
    "coordinator_role",
    "git_release_holder",
    "exploration_concern_owners",
    "exploration_owners",
    "challenger",
}
NEW_PROJECT_PROMPT = (
    "Read AGENTS.md or CLAUDE.md. Take full ownership of bootstrapping a new project "
    "at <ABSOLUTE_TARGET_FOLDER> whose objective is <PLAIN_LANGUAGE_OBJECTIVE>. Do "
    "not publish anything remotely without my authorization."
)
IMPROVEMENT_PROMPT = (
    "Read AGENTS.md or CLAUDE.md. Take full ownership of improving Warmboot Full at "
    "<ABSOLUTE_REPOSITORY> for <IMPROVEMENT_OBJECTIVE>. Treat "
    "<FROZEN_COMMIT_OR_TAG> as the immutable consumer baseline. Follow "
    "MAINTAINING.md, orchestrate only, do not edit other repositories, "
    "and do not publish remotely without my authorization."
)


class SelfImprovementVerificationError(ValueError):
    """Raised when self-improvement evidence violates the fixed contract."""


def _exact_object(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SelfImprovementVerificationError(f"{label} must be an object")
    actual = set(value)
    if actual != keys:
        raise SelfImprovementVerificationError(
            f"{label} keys differ: missing={sorted(keys - actual)}, extra={sorted(actual - keys)}"
        )
    return value


def _canonical_relative(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise SelfImprovementVerificationError(f"{label} must be a string")
    path = Path(value)
    if (
        not value
        or path.is_absolute()
        or path.as_posix() != value
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise SelfImprovementVerificationError(f"{label} must be canonical repository-relative")
    return value


def _canonical_text(value: Any, label: str) -> str:
    if type(value) is not str or not value or value != value.strip():
        raise SelfImprovementVerificationError(f"{label} must be canonical non-empty text")
    return value


def _identity_key(value: Any, label: str) -> str:
    """Return a compatibility-normalized key for one canonical role identity."""
    text = _canonical_text(value, label)
    if any(is_unsafe_evidence_character(character) for character in text):
        raise SelfImprovementVerificationError(
            f"{label} must not contain unsafe Unicode evidence characters"
        )
    if any(is_synthetic_ignorable(character) for character in text):
        raise SelfImprovementVerificationError(
            f"{label} must not contain synthetic Unicode ignorables"
        )
    return nfkc_casefold(text)


def _member(root: Path, relative: str, label: str) -> Path:
    current = root
    # Before Python 3.14, is_symlink() raises for an over-long or unsearchable component.
    try:
        for part in Path(_canonical_relative(relative, label)).parts:
            current = current / part
            if current.is_symlink():
                raise SelfImprovementVerificationError(f"{label} must not traverse a symlink")
        resolved = current.resolve(strict=True)
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise SelfImprovementVerificationError(f"{label} must exist") from exc
    except OSError as exc:
        raise SelfImprovementVerificationError(
            f"{label} cannot be checked: {exc.strerror}"
        ) from exc
    try:
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise SelfImprovementVerificationError(f"{label} must resolve inside its root") from exc
    if not current.is_file():
        raise SelfImprovementVerificationError(f"{label} must be a regular file")
    return current


def _read_json(path: Path, label: str) -> Any:
    if path.is_symlink() or not path.is_file():
        raise SelfImprovementVerificationError(f"{label} must be a regular JSON file")
    try:
        return strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateJsonKeyError) as exc:
        raise SelfImprovementVerificationError(f"invalid {label}: {exc}") from exc


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_release_manifest(
    manifest: Any,
    repository: Path | None = None,
    manifest_path: str | None = None,
) -> None:
    """Preserve this oracle's public exception while using the canonical validator."""
    try:
        _verify_release_manifest(manifest, repository, manifest_path)
    except ReleaseManifestVerificationError as exc:
        raise SelfImprovementVerificationError(str(exc)) from exc


def verify_illustrative_release_manifest(manifest: Any) -> None:
    """Validate only the non-release example through its explicit schema path."""
    try:
        _verify_illustrative_manifest(manifest)
    except ReleaseManifestVerificationError as exc:
        raise SelfImprovementVerificationError(str(exc)) from exc


def verify_maintainer_repository(repository: Path) -> None:
    """Check the maintainer files, README prompts and routes that planning relies on."""
    if repository.is_symlink() or not repository.is_dir():
        raise SelfImprovementVerificationError("repository root must be a real directory")
    required = [
        "AGENTS.md",
        "WARMBOOT.md",
        "MAINTAINING.md",
        "ROLE-INDEX.md",
        "CHANGELOG.md",
        "BUGFIXES.md",
        *REQUIRED_CONTEXT[2:7],
        "docs/adr/0001-single-repository-self-hosting-and-release-boundary.md",
        "docs/source-refresh.md",
        "docs/release.md",
        "docs/releases/release-manifest.schema.json",
        "docs/releases/release-manifest.example.json",
    ]
    for relative in required:
        _member(repository, relative, f"maintainer path {relative}")

    readme = _member(repository, "README.md", "README").read_text(encoding="utf-8")
    session_heading = "\n## How a session uses it\n"
    if readme.count(session_heading) != 1:
        raise SelfImprovementVerificationError("README needs one How a session uses it section")
    session = readme.split(session_heading, 1)[1].split("\n## ", 1)[0].replace("\n", " ")
    if NEW_PROJECT_PROMPT not in session:
        raise SelfImprovementVerificationError(
            "new-project copy/paste prompt must appear in README's How a session uses it section"
        )
    validate_heading = "\n## Validate this checkout\n"
    if readme.count(validate_heading) != 1:
        raise SelfImprovementVerificationError("README needs one Validate this checkout section")
    validate = readme.split(validate_heading, 1)[1].split("\n## ", 1)[0].replace("\n", " ")
    if IMPROVEMENT_PROMPT not in validate:
        raise SelfImprovementVerificationError(
            "improvement copy/paste prompt must appear in README's Validate this checkout section"
        )
    flat = readme.replace("\n", " ")
    if flat.index(NEW_PROJECT_PROMPT) > flat.index(IMPROVEMENT_PROMPT):
        raise SelfImprovementVerificationError("new-project prompt must precede improvement prompt")

    maintaining = _member(repository, "MAINTAINING.md", "MAINTAINING").read_text(encoding="utf-8")
    for relative in REQUIRED_CONTEXT[:7]:
        if relative not in maintaining:
            raise SelfImprovementVerificationError(f"MAINTAINING does not route {relative}")
    warmboot = _member(repository, "WARMBOOT.md", "WARMBOOT").read_text(encoding="utf-8")
    if "MAINTAINING.md" not in warmboot:
        raise SelfImprovementVerificationError("WARMBOOT does not route maintainer work")

    schema = _read_json(repository / "docs/releases/release-manifest.schema.json", "release schema")
    if schema.get("x-schema-vocabulary") != "JSON Schema Draft 2020-12":
        raise SelfImprovementVerificationError("release schema draft is not declared")
    example = _read_json(
        repository / "docs/releases/release-manifest.example.json", "release example"
    )
    verify_illustrative_release_manifest(example)
    if example["manifest_kind"] != "ILLUSTRATIVE_NON_RELEASE":
        raise SelfImprovementVerificationError("release example must not claim a release")


def expected_response(package: Path) -> dict[str, Any]:
    """Return the planner result the package's request requires."""
    if package.is_symlink() or not package.is_dir():
        raise SelfImprovementVerificationError("package root must be a real directory")
    request = _read_json(package / "request.json", "request")
    request = _exact_object(
        request,
        {
            "schema_version",
            "repository",
            "objective",
            "change_class",
            "coordinator",
            "baseline",
            "authority",
            "handoff_path",
        },
        "request",
    )
    if type(request["schema_version"]) is not int or request["schema_version"] != 1:
        raise SelfImprovementVerificationError("request schema_version must be integer 1")
    if request["change_class"] != "ARCHITECTURE_BOOTSTRAP_RELEASE":
        raise SelfImprovementVerificationError(
            "fixture must exercise the intensive exploration boundary"
        )
    baseline = _exact_object(
        request["baseline"],
        {"identity_kind", "identity", "resolved_commit", "manifest_path", "manifest_sha256"},
        "baseline",
    )
    if baseline["identity_kind"] != "ANNOTATED_TAG" or not GIT_OID_RE.fullmatch(
        baseline["resolved_commit"]
    ):
        raise SelfImprovementVerificationError(
            "fixture baseline must be an immutable full Git identity"
        )
    if not SHA256_RE.fullmatch(baseline["manifest_sha256"]):
        raise SelfImprovementVerificationError("fixture manifest digest must be SHA-256")
    _canonical_relative(baseline["manifest_path"], "baseline manifest path")
    authority = _exact_object(
        request["authority"],
        {"may_plan", "may_edit", "may_commit", "may_publish", "source_repositories"},
        "authority",
    )
    if any(
        type(authority[key]) is not bool
        for key in ("may_plan", "may_edit", "may_commit", "may_publish")
    ) or authority != {
        "may_plan": True,
        "may_edit": False,
        "may_commit": False,
        "may_publish": False,
        "source_repositories": "READ_ONLY",
    }:
        raise SelfImprovementVerificationError("fixture authority must remain planning-only")

    handoff_path = _canonical_relative(request["handoff_path"], "handoff path")
    handoff = _read_json(_member(package, handoff_path, "handoff"), "handoff")
    handoff = _exact_object(
        handoff, {"schema_version", "receipt_id", "source_path", "claimed_sha256"}, "handoff"
    )
    if type(handoff["schema_version"]) is not int or handoff["schema_version"] != 1:
        raise SelfImprovementVerificationError("handoff schema_version must be integer 1")
    source_path = _canonical_relative(handoff["source_path"], "handoff source path")
    source = _member(package, source_path, "handoff source")
    claimed = handoff["claimed_sha256"]
    if not isinstance(claimed, str) or not SHA256_RE.fullmatch(claimed):
        raise SelfImprovementVerificationError("claimed handoff digest must be SHA-256")
    actual = _sha256(source)
    if claimed == actual:
        raise SelfImprovementVerificationError("fixture handoff must be stale")

    return {
        "schema_version": 1,
        "mode": "PLANNING_ONLY_NON_MUTATING",
        "objective": request["objective"],
        "repository": request["repository"],
        "baseline": {**baseline, "state": "IMMUTABLE_BASELINE"},
        "authority": authority,
        "topology": {
            "classification": "PROPORTIONAL_EXPLORATION_REQUIRED",
            "coordinator": request["coordinator"],
            "coordinator_role": "ORCHESTRATOR_ONLY_SYNTHESIS_ONLY",
            "git_release_holder": request["coordinator"],
            "exploration_concern_owners": dict(EXPLORATION_CONCERN_OWNERS),
            "exploration_owners": list(EXPLORATION_OWNERS),
            "challenger": "independent-non-author-challenger",
        },
        "required_context": REQUIRED_CONTEXT,
        "evidence": {
            "baseline_checkout": "SEPARATE_TEMP_CLEAN",
            "candidate_checkout": "SEPARATE_TEMP_CLEAN",
            "deterministic_suite": "REQUIRED",
            "cold_before_agent": "BRAND_NEW_CONTEXT_CLEAN",
            "cold_after_agent": "DIFFERENT_BRAND_NEW_CONTEXT_CLEAN",
            "recovery_resumer": "DISTINCT_FRESH_AGENT",
            "independent_review": "REQUIRED_ON_UNCHANGED_CANDIDATE",
            "runtime_claim": "UNPROVED_NOT_RUN",
        },
        "checkpoint_publication": {
            "local_checkpoint_holder": request["coordinator"],
            "checkpoint_state": "NOT_AUTHORIZED_IN_PLANNING_DRY_RUN",
            "remote_authority": "EXPLICIT_USER_AUTHORIZATION_REQUIRED",
            "may_publish": False,
        },
        "recovery": {
            "handoff_path": handoff_path,
            "source_path": source_path,
            "claimed_sha256": claimed,
            "actual_sha256": actual,
            "freshness": "STALE",
            "next_action": "RERUN_NOW",
            "authority_renewed": False,
        },
        "next_action": "DELEGATE_PROPORTIONAL_READ_ONLY_EXPLORATION_CONCERNS",
    }


def _validate_topology(value: Any) -> None:
    topology = _exact_object(value, TOPOLOGY_KEYS, "topology")
    if topology["classification"] != "PROPORTIONAL_EXPLORATION_REQUIRED":
        raise SelfImprovementVerificationError("topology classification is invalid")
    coordinator = topology["coordinator"]
    coordinator_key = _identity_key(coordinator, "topology coordinator")
    if topology["coordinator_role"] != "ORCHESTRATOR_ONLY_SYNTHESIS_ONLY":
        raise SelfImprovementVerificationError(
            "topology coordinator must remain orchestration-only"
        )
    if (
        _identity_key(topology["git_release_holder"], "topology Git/release holder")
        != coordinator_key
    ):
        raise SelfImprovementVerificationError(
            "topology Git/release holder must be the coordinator"
        )

    concern_owners = topology["exploration_concern_owners"]
    if not isinstance(concern_owners, dict) or set(concern_owners) != set(
        EXPLORATION_CONCERN_OWNERS
    ):
        raise SelfImprovementVerificationError("all six exploration concerns are required")
    concern_owner_keys = {
        concern: _identity_key(owner, f"exploration concern {concern} owner")
        for concern, owner in concern_owners.items()
    }
    owners = topology["exploration_owners"]
    if not isinstance(owners, list):
        raise SelfImprovementVerificationError("exploration owners must be a text list")
    owner_keys = [
        _identity_key(owner, f"exploration owner {index}") for index, owner in enumerate(owners)
    ]
    if len(owners) < 2:
        raise SelfImprovementVerificationError(
            "topology requires at least two attributed research owners"
        )
    if coordinator_key in owner_keys or coordinator_key in concern_owner_keys.values():
        raise SelfImprovementVerificationError("coordinator must not own exploration concerns")
    if (
        concern_owner_keys["architecture_risk_privacy"]
        == concern_owner_keys["testing_bootstrap_release"]
    ):
        raise SelfImprovementVerificationError(
            "high-risk architecture and delivery concerns must be separated"
        )
    if len(owner_keys) != len(set(owner_keys)) or set(owner_keys) != set(
        concern_owner_keys.values()
    ):
        raise SelfImprovementVerificationError(
            "exploration owner list must exactly match attributed concern owners"
        )
    challenger_key = _identity_key(topology["challenger"], "challenger")
    if challenger_key in {*owner_keys, coordinator_key}:
        raise SelfImprovementVerificationError("challenger must be a distinct non-author")


def verify_scope_change_record(package: Path, value: Any) -> None:
    """Verify the bounded revision fixture without claiming live orchestration proof."""
    record = _exact_object(
        value,
        {
            "schema_version",
            "coordinator",
            "lanes",
            "addendum",
            "disposition",
            "unaffected_receipts",
            "review",
        },
        "scope-change record",
    )
    if record["schema_version"] != 1 or type(record["schema_version"]) is not int:
        raise SelfImprovementVerificationError("scope-change schema_version must be integer 1")
    coordinator = record["coordinator"]
    coordinator_key = _identity_key(coordinator, "scope-change coordinator")

    lanes = record["lanes"]
    if not isinstance(lanes, list) or len(lanes) < 2:
        raise SelfImprovementVerificationError("scope-change fixture requires at least two lanes")
    lane_by_id: dict[str, dict[str, Any]] = {}
    lane_owner_keys: set[str] = set()
    for index, raw_lane in enumerate(lanes):
        lane = _exact_object(
            raw_lane,
            {"id", "owner", "receipt_path", "receipt_sha256"},
            f"scope-change lane {index}",
        )
        lane_id = lane["id"]
        owner = lane["owner"]
        if not isinstance(lane_id, str) or not lane_id or lane_id in lane_by_id:
            raise SelfImprovementVerificationError("scope-change lane ids must be unique text")
        owner_key = _identity_key(owner, f"scope-change lane {lane_id} owner")
        if owner_key == coordinator_key:
            raise SelfImprovementVerificationError(
                "scope-change lane owners must be distinct from the coordinator"
            )
        if owner_key in lane_owner_keys:
            raise SelfImprovementVerificationError(
                "scope-change lane owners must be unique identities"
            )
        lane_owner_keys.add(owner_key)
        _canonical_relative(lane["receipt_path"], f"scope-change lane {lane_id} receipt path")
        if not isinstance(lane["receipt_sha256"], str) or not SHA256_RE.fullmatch(
            lane["receipt_sha256"]
        ):
            raise SelfImprovementVerificationError("scope-change lane receipt must use SHA-256")
        receipt_file = _member(
            package, lane["receipt_path"], f"scope-change lane {lane_id} receipt"
        )
        if _sha256(receipt_file) != lane["receipt_sha256"]:
            raise SelfImprovementVerificationError(
                "scope-change lane receipt digest does not match current bytes"
            )
        lane_by_id[lane_id] = lane

    addendum = _exact_object(
        record["addendum"], {"id", "affected_lanes", "requirement"}, "scope-change addendum"
    )
    _canonical_text(addendum["id"], "scope-change addendum id")
    _canonical_text(addendum["requirement"], "scope-change addendum requirement")
    affected = addendum["affected_lanes"]
    if (
        not isinstance(affected, list)
        or not affected
        or len(affected) != len(set(affected))
        or not set(affected) <= set(lane_by_id)
    ):
        raise SelfImprovementVerificationError("affected_lanes must be unique known lane ids")

    disposition = _exact_object(
        record["disposition"],
        {"coordinator", "lane_actions", "stopped_lane_remaining_outcome", "next_holder"},
        "scope-change disposition",
    )
    if (
        _identity_key(disposition["coordinator"], "scope-change disposition coordinator")
        != coordinator_key
    ):
        raise SelfImprovementVerificationError("scope revision must not rotate the coordinator")
    actions = disposition["lane_actions"]
    if not isinstance(actions, dict) or set(actions) != set(lane_by_id):
        raise SelfImprovementVerificationError("lane actions must cover each existing lane exactly")
    for lane_id, action in actions.items():
        if lane_id in affected and action not in {"RENEW", "RERUN", "STOP"}:
            raise SelfImprovementVerificationError("affected lane must be RENEW, RERUN, or STOP")
        if lane_id not in affected and action != "UNAFFECTED":
            raise SelfImprovementVerificationError("unaffected lane action must be UNAFFECTED")
    has_stopped_lane = any(actions[lane_id] == "STOP" for lane_id in affected)
    remaining_outcome = disposition["stopped_lane_remaining_outcome"]
    next_holder = disposition["next_holder"]
    if has_stopped_lane:
        if not isinstance(remaining_outcome, str) or not remaining_outcome.strip():
            raise SelfImprovementVerificationError(
                "stopped lane remaining outcome must be non-empty text"
            )
        if (
            not isinstance(next_holder, str)
            or not next_holder.strip()
            or _identity_key(next_holder, "stopped lane next holder") == coordinator_key
        ):
            raise SelfImprovementVerificationError(
                "stopped lane next holder must be non-coordinator text"
            )
    elif remaining_outcome is not None or next_holder is not None:
        raise SelfImprovementVerificationError("stop fields must be null when no lane is stopped")

    receipts = record["unaffected_receipts"]
    unaffected = set(lane_by_id) - set(affected)
    if not isinstance(receipts, list) or len(receipts) != len(unaffected):
        raise SelfImprovementVerificationError(
            "each unaffected lane requires one digest-bound receipt"
        )
    seen_receipts: set[str] = set()
    for index, raw_receipt in enumerate(receipts):
        receipt = _exact_object(
            raw_receipt,
            {"lane", "receipt_path", "receipt_sha256"},
            f"unaffected receipt {index}",
        )
        lane_id = receipt["lane"]
        if lane_id not in unaffected or lane_id in seen_receipts:
            raise SelfImprovementVerificationError(
                "unaffected receipts must map one-to-one to unaffected lanes"
            )
        lane = lane_by_id[lane_id]
        if (
            receipt["receipt_path"] != lane["receipt_path"]
            or receipt["receipt_sha256"] != lane["receipt_sha256"]
        ):
            raise SelfImprovementVerificationError(
                "unaffected receipt must preserve the prior lane receipt"
            )
        receipt_file = _member(package, receipt["receipt_path"], "unaffected receipt path")
        if _sha256(receipt_file) != receipt["receipt_sha256"]:
            raise SelfImprovementVerificationError(
                "unaffected receipt digest does not match current bytes"
            )
        seen_receipts.add(lane_id)

    review = _exact_object(
        record["review"], {"reviewer", "author_ids", "required"}, "scope-change review"
    )
    authors = review["author_ids"]
    expected_author_keys = {coordinator_key, *lane_owner_keys}
    if not isinstance(authors, list):
        raise SelfImprovementVerificationError(
            "review authors must cover coordinator and lane owners"
        )
    author_keys = [
        _identity_key(author, f"review author_ids {index}") for index, author in enumerate(authors)
    ]
    if len(author_keys) != len(set(author_keys)) or set(author_keys) != expected_author_keys:
        raise SelfImprovementVerificationError(
            "review authors must cover coordinator and lane owners"
        )
    if review["required"] is not True:
        raise SelfImprovementVerificationError("non-author review must remain required")
    reviewer_key = _identity_key(review["reviewer"], "reviewer")
    if reviewer_key in expected_author_keys:
        raise SelfImprovementVerificationError("reviewer must not be an author")


def verify(package: Path, result: Any, repository: Path | None = None) -> None:
    """Check a planner result and any given maintainer repository, raising on any mismatch."""
    expected = expected_response(package)
    if not isinstance(result, dict) or "topology" not in result:
        raise SelfImprovementVerificationError("planner result must contain topology")
    if type(result.get("schema_version")) is not int or result["schema_version"] != 1:
        raise SelfImprovementVerificationError("planner result schema_version must be integer 1")
    authority = result.get("authority")
    if not isinstance(authority, dict) or any(
        type(authority.get(key)) is not bool
        for key in ("may_plan", "may_edit", "may_commit", "may_publish")
    ):
        raise SelfImprovementVerificationError("planner result authority must use exact booleans")
    for section, field in (
        ("checkpoint_publication", "may_publish"),
        ("recovery", "authority_renewed"),
    ):
        value = result.get(section)
        if not isinstance(value, dict) or type(value.get(field)) is not bool:
            raise SelfImprovementVerificationError(
                f"planner result {section}.{field} must use an exact boolean"
            )
    _validate_topology(result["topology"])
    if result != expected:
        raise SelfImprovementVerificationError(
            "planner result does not match fixture evidence: "
            + json.dumps({"expected": expected, "actual": result}, sort_keys=True)
        )
    if repository is not None:
        verify_maintainer_repository(repository)


def _resolve_argument(path: Path, label: str) -> Path:
    """Resolve a command-line path, reporting a symlink loop as a verification failure."""
    try:
        return path.resolve()
    except RuntimeError as exc:  # Python 3.11 and 3.12 report a symlink loop this way.
        raise SelfImprovementVerificationError(f"{label} is a symlink loop: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    """Run the command line and return the exit code."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        result = _read_json(args.result, "planner result")
        verify(
            _resolve_argument(args.package, "package"),
            result,
            _resolve_argument(args.repository, "repository"),
        )
    except (OSError, UnicodeDecodeError, SelfImprovementVerificationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps({"claim": "STRUCTURE_ONLY_NO_RUNTIME_PROOF", "status": "PASS"}, sort_keys=True)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
