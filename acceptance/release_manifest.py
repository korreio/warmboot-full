"""Canonical verifier for compact Warmboot Full consumer-release manifests.

The manifest binds one include/exclude policy, one aggregate over every selected
regular-file record, lineage/privacy receipt bytes, and conservative local claims. A
separate post-commit release receipt resolves the declared annotated tag to its full
commit. This module performs no Git, tag, remote, signature, network, generation, or
publication action.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Any

if __package__:
    from .strict_json import DuplicateJsonKeyError
    from .strict_json import loads as strict_json_loads
else:
    from strict_json import DuplicateJsonKeyError
    from strict_json import loads as strict_json_loads


SHA256_RE = re.compile(r"[0-9a-f]{64}")
RELEASE_STATES = {"CANDIDATE"}
MANIFEST_KINDS = {"RELEASE", "ILLUSTRATIVE_NON_RELEASE"}
REPRESENTATION = "COMPACT_POLICY_RECEIPT_V1"
IDENTITY_KIND = "ANNOTATED_TAG_DECLARATION_ONLY"
RECORD_ENCODING = "sorted(path + NUL + type + NUL + mode + NUL + sha256 + NUL + decimal_bytes + LF)"
CLAIMS = {
    "release_ready": False,
    "tag_verified": False,
    "remote_authenticity": "UNPROVED_LOCAL_ONLY",
}
REQUIRED_KNOWN_UNPROVED = (
    {
        "domain": "ANNOTATED_TAG",
        "state": "UNPROVED",
        "boundary": "No annotated tag was checked.",
    },
    {
        "domain": "RESOLVED_COMMIT",
        "state": "UNPROVED",
        "boundary": "No resolved commit was checked.",
    },
    {
        "domain": "SIGNATURE_AUTHENTICITY",
        "state": "UNPROVED",
        "boundary": "No signature authenticity was checked.",
    },
    {
        "domain": "REMOTE_AUTHENTICITY",
        "state": "UNPROVED",
        "boundary": "No remote authenticity was checked.",
    },
)
TOP_LEVEL_KEYS = {
    "schema_version",
    "manifest_kind",
    "representation",
    "release",
    "digest_algorithm",
    "record_encoding",
    "payload_policy",
    "payload_policy_sha256",
    "lineage_receipts",
    "claims",
    "known_unproved",
}
RELEASE_KEYS = {
    "id",
    "status",
    "identity_kind",
    "declared_ref",
    "payload_sha256",
}


class ReleaseManifestVerificationError(ValueError):
    """Raised when a release manifest violates the compact contract."""


def canonical_json(value: Any) -> bytes:
    """Return the canonical JSON bytes used for policy hashing."""
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode() + b"\n"
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _exact_object(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReleaseManifestVerificationError(f"{label} must be an object")
    actual = set(value)
    if actual != keys:
        raise ReleaseManifestVerificationError(
            f"{label} keys differ: missing={sorted(keys - actual)}, extra={sorted(actual - keys)}"
        )
    return value


def _require_sha256(value: Any, label: str) -> str:
    if type(value) is not str or not SHA256_RE.fullmatch(value):
        raise ReleaseManifestVerificationError(f"{label} must be canonical lowercase SHA-256")
    return value


def canonical_relative(value: Any, label: str, *, allow_root: bool = False) -> str:
    """Return a canonical repository-relative POSIX path, rejecting any other form."""
    if not isinstance(value, str) or not value:
        raise ReleaseManifestVerificationError(f"{label} must be a non-empty string")
    if allow_root and value == ".":
        return value
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or path.as_posix() != value
        or "\\" in value
        or any(ord(character) < 32 for character in value)
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ReleaseManifestVerificationError(f"{label} must be canonical repository-relative")
    return value


def _declared_tag(value: Any) -> str:
    if type(value) is not str or not value:
        raise ReleaseManifestVerificationError("declared annotated tag must be non-empty")
    components = value.split("/")
    if (
        value == "@"
        or value.startswith(("-", "/", "refs/"))
        or value.endswith((".", "/"))
        or any(fragment in value for fragment in ("..", "@{", "//"))
        or any(
            character.isspace()
            or ord(character) < 32
            or ord(character) == 127
            or character in "~^:?*[\\"
            for character in value
        )
        or not re.fullmatch(r"[A-Za-z0-9._/-]+", value)
        or any(
            not component
            or component in {".", ".."}
            or component.startswith(".")
            or component.endswith((".", ".lock"))
            for component in components
        )
    ):
        raise ReleaseManifestVerificationError("declared annotated tag has an invalid domain")
    return value


def _repository_path(root: Path, relative: str, label: str, *, allow_root: bool = False) -> Path:
    """Check all repository-relative components before following or reading a path."""
    if root.is_symlink() or not root.is_dir():
        raise ReleaseManifestVerificationError("repository root must be a real directory")
    current = root
    canonical = canonical_relative(relative, label, allow_root=allow_root)
    # Before Python 3.14, is_symlink() raises for an over-long or unsearchable component.
    try:
        for part in PurePosixPath(canonical).parts:
            current = current / part
            if current.is_symlink():
                raise ReleaseManifestVerificationError(f"{label} must not traverse a symlink")
        resolved = current.resolve(strict=True)
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise ReleaseManifestVerificationError(f"{label} must exist") from exc
    except OSError as exc:
        raise ReleaseManifestVerificationError(
            f"{label} cannot be checked: {exc.strerror}"
        ) from exc
    try:
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise ReleaseManifestVerificationError(
            f"{label} must resolve inside its repository"
        ) from exc
    return current


def repository_member(root: Path, relative: str, label: str) -> Path:
    """Return the regular file at a repository-relative path, rejecting anything else."""
    current = _repository_path(root, relative, label)
    if not current.is_file():
        raise ReleaseManifestVerificationError(f"{label} must be a regular file")
    return current


def validate_policy(policy: Any) -> dict[str, Any]:
    """Return the payload policy after checking its includes and exclusions."""
    policy = _exact_object(policy, {"include", "exclude"}, "payload_policy")
    includes = policy["include"]
    excludes = policy["exclude"]
    if not isinstance(includes, list) or not includes:
        raise ReleaseManifestVerificationError("payload_policy.include must be non-empty")
    if not isinstance(excludes, list):
        raise ReleaseManifestVerificationError("payload_policy.exclude must be an array")
    normalized_includes = [
        canonical_relative(item, f"include[{index}]", allow_root=True)
        for index, item in enumerate(includes)
    ]
    if normalized_includes != sorted(set(normalized_includes)):
        raise ReleaseManifestVerificationError("include paths must be unique and sorted")
    include_paths = [PurePosixPath(item) for item in normalized_includes if item != "."]
    if "." in normalized_includes and len(normalized_includes) != 1:
        raise ReleaseManifestVerificationError("root include makes every other include redundant")
    for index, candidate in enumerate(include_paths):
        if any(prior in candidate.parents for prior in include_paths[:index]):
            raise ReleaseManifestVerificationError("include paths must not overlap")
    seen_excludes: list[tuple[PurePosixPath, str]] = []
    ordered_excludes: list[str] = []
    for index, raw in enumerate(excludes):
        item = _exact_object(raw, {"path", "scope", "reason", "bound_receipt"}, f"exclude[{index}]")
        path = canonical_relative(item["path"], f"exclude[{index}].path")
        if type(item["scope"]) is not str or item["scope"] not in {"FILE", "SUBTREE"}:
            raise ReleaseManifestVerificationError("exclusion scope must be FILE or SUBTREE")
        if (
            not isinstance(item["reason"], str)
            or not item["reason"].strip()
            or item["reason"] != item["reason"].strip()
        ):
            raise ReleaseManifestVerificationError(
                "exclusion reason must be canonical non-empty text"
            )
        canonical_relative(item["bound_receipt"], f"exclude[{index}].bound_receipt")
        candidate = PurePosixPath(path)
        if "." not in normalized_includes and not any(
            candidate == include or include in candidate.parents for include in include_paths
        ):
            raise ReleaseManifestVerificationError(
                f"exclusion lies outside every include path: {path}"
            )
        for prior, prior_scope in seen_excludes:
            if candidate == prior or prior in candidate.parents or candidate in prior.parents:
                raise ReleaseManifestVerificationError(
                    f"overlapping or duplicate exclusions are ambiguous: {path}"
                )
        seen_excludes.append((candidate, item["scope"]))
        ordered_excludes.append(path)
    if ordered_excludes != sorted(ordered_excludes):
        raise ReleaseManifestVerificationError("exclusions must be sorted by path")
    return policy


def policy_digest(policy: Any) -> str:
    """Return the SHA-256 of the validated policy's canonical JSON."""
    return _sha256_bytes(canonical_json(validate_policy(policy)))


def _is_excluded(relative: str, policy: dict[str, Any]) -> bool:
    path = PurePosixPath(relative)
    for item in policy["exclude"]:
        excluded = PurePosixPath(item["path"])
        if path == excluded or (item["scope"] == "SUBTREE" and excluded in path.parents):
            return True
    return False


def _entries(directory: Path) -> list[Path]:
    """Return every entry below a directory, failing on any entry it cannot inspect."""
    entries: list[Path] = []
    pending = [directory]
    while pending:
        for entry in pending.pop().iterdir():
            entries.append(entry)
            if stat.S_ISDIR(entry.lstat().st_mode):
                pending.append(entry)
    return sorted(entries)


def _included_nodes(root: Path, policy: dict[str, Any]) -> dict[str, Path]:
    nodes: dict[str, Path] = {}
    for raw in policy["include"]:
        # A nested include can hide a symlink above its leaf; validate ancestry
        # before enumeration, while explicit exclusions still skip selected nodes.
        include = _repository_path(root, raw, f"include path {raw}", allow_root=True)
        try:
            candidates = _entries(include) if include.is_dir() else [include]
        except OSError as exc:
            raise ReleaseManifestVerificationError(
                f"include path {raw} cannot be listed: {exc.strerror}"
            ) from exc
        for candidate in candidates:
            relative = candidate.relative_to(root).as_posix()
            if not relative or _is_excluded(relative, policy):
                continue
            nodes.setdefault(relative, candidate)
    return nodes


def selected_records(root: Path, policy: Any) -> list[dict[str, Any]]:
    """Expand the complete policy and return canonical selected regular-file records."""
    policy = validate_policy(policy)
    if root.is_symlink() or not root.is_dir():
        raise ReleaseManifestVerificationError("repository root must be a real directory")
    records: list[dict[str, Any]] = []
    for relative, path in sorted(_included_nodes(root, policy).items()):
        # Recheck each eligible member before reading bytes; this is a local
        # containment observation, not protection against concurrent path swaps.
        path = _repository_path(root, relative, f"eligible node {relative}")
        node = path.lstat()
        if stat.S_ISDIR(node.st_mode) and not path.is_symlink():
            continue
        if not stat.S_ISREG(node.st_mode) or path.is_symlink():
            raise ReleaseManifestVerificationError(
                f"eligible node is not a regular file: {relative}"
            )
        records.append(
            {
                "path": relative,
                "type": "regular",
                "mode": "100755" if node.st_mode & 0o111 else "100644",
                "bytes": node.st_size,
                "sha256": _sha256(path),
            }
        )
    if not records:
        raise ReleaseManifestVerificationError("consumer payload must be non-empty")
    return records


def payload_digest(records: list[dict[str, Any]]) -> str:
    """Return the aggregate SHA-256 over the file records, ordered by path."""
    payload = b"".join(
        (
            f"{record['path']}\0{record['type']}\0{record['mode']}\0"
            f"{record['sha256']}\0{record['bytes']}\n"
        ).encode()
        for record in sorted(records, key=lambda item: item["path"])
    )
    return _sha256_bytes(payload)


def _validate_lineage(
    value: Any,
    policy: dict[str, Any],
    repository: Path | None,
    selected_paths: set[str] | None,
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ReleaseManifestVerificationError("lineage_receipts must be non-empty")
    result: list[dict[str, Any]] = []
    paths: list[str] = []
    for index, raw in enumerate(value):
        item = _exact_object(raw, {"path", "sha256"}, f"lineage_receipts[{index}]")
        path = canonical_relative(item["path"], f"lineage_receipts[{index}].path")
        digest = _require_sha256(item["sha256"], f"lineage_receipts[{index}].sha256")
        paths.append(path)
        if repository is not None:
            member = repository_member(repository, path, f"lineage receipt {path}")
            if _sha256(member) != digest:
                raise ReleaseManifestVerificationError(f"lineage/privacy receipt mismatch: {path}")
            if selected_paths is None or path not in selected_paths:
                raise ReleaseManifestVerificationError(
                    f"lineage/privacy receipt must remain in selected payload: {path}"
                )
        result.append(item)
    if paths != sorted(set(paths)):
        raise ReleaseManifestVerificationError("lineage receipt paths must be unique and sorted")
    bound = {item["bound_receipt"] for item in policy["exclude"]}
    if not bound.issubset(paths):
        raise ReleaseManifestVerificationError(
            "every exclusion must bind a listed lineage/privacy receipt"
        )
    return result


def _verify_manifest(
    manifest: Any,
    repository: Path | None = None,
    manifest_path: str | None = None,
    *,
    expected_policy_sha256: str | None = None,
    expected_release_id: str | None = None,
    expected_declared_ref: str | None = None,
    illustrative_schema_only: bool = False,
) -> None:
    manifest = _exact_object(manifest, TOP_LEVEL_KEYS, "release manifest")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise ReleaseManifestVerificationError("release schema_version must be integer 1")
    if (
        type(manifest["manifest_kind"]) is not str
        or manifest["manifest_kind"] not in MANIFEST_KINDS
    ):
        raise ReleaseManifestVerificationError("unknown release manifest_kind")
    if manifest["manifest_kind"] == "ILLUSTRATIVE_NON_RELEASE":
        if not illustrative_schema_only:
            raise ReleaseManifestVerificationError(
                "ILLUSTRATIVE_NON_RELEASE is not admissible as release-candidate proof"
            )
        if (
            repository is not None
            or manifest_path is not None
            or any(
                value is not None
                for value in (
                    expected_policy_sha256,
                    expected_release_id,
                    expected_declared_ref,
                )
            )
        ):
            raise ReleaseManifestVerificationError(
                "illustrative manifests support explicit structure-only validation"
            )
    elif illustrative_schema_only:
        raise ReleaseManifestVerificationError(
            "the illustrative validation path accepts ILLUSTRATIVE_NON_RELEASE only"
        )
    if manifest["representation"] != REPRESENTATION:
        raise ReleaseManifestVerificationError("unknown release representation")
    if manifest["digest_algorithm"] != "sha256":
        raise ReleaseManifestVerificationError("release digest algorithm must be sha256")
    if manifest["record_encoding"] != RECORD_ENCODING:
        raise ReleaseManifestVerificationError("unknown payload record encoding")

    release = _exact_object(manifest["release"], RELEASE_KEYS, "release")
    if (
        not isinstance(release["id"], str)
        or not release["id"]
        or release["id"] != release["id"].strip()
        or any(ord(character) < 32 for character in release["id"])
    ):
        raise ReleaseManifestVerificationError("release id must be canonical non-empty text")
    if type(release["status"]) is not str or release["status"] not in RELEASE_STATES:
        raise ReleaseManifestVerificationError(
            "commit-contained release status must remain CANDIDATE"
        )
    if release["identity_kind"] != IDENTITY_KIND:
        raise ReleaseManifestVerificationError(
            "commit-contained identity must be an annotated-tag declaration only"
        )
    _declared_tag(release["declared_ref"])
    _require_sha256(release["payload_sha256"], "release.payload_sha256")
    if expected_release_id is not None and release["id"] != expected_release_id:
        raise ReleaseManifestVerificationError("release id differs from frozen receipt")
    if expected_declared_ref is not None and release["declared_ref"] != expected_declared_ref:
        raise ReleaseManifestVerificationError("declared tag differs from frozen receipt")

    claims = _exact_object(manifest["claims"], set(CLAIMS), "claims")
    if (
        claims != CLAIMS
        or type(claims["release_ready"]) is not bool
        or type(claims["tag_verified"]) is not bool
        or type(claims["remote_authenticity"]) is not str
    ):
        raise ReleaseManifestVerificationError(
            "manifest must not claim release, tag, signature, or remote authenticity"
        )
    limitations = manifest["known_unproved"]
    if not isinstance(limitations, list):
        raise ReleaseManifestVerificationError("known_unproved must be an array")
    validated_limits: list[dict[str, Any]] = []
    for index, raw in enumerate(limitations):
        validated_limits.append(
            _exact_object(
                raw,
                {"domain", "state", "boundary"},
                f"known_unproved[{index}]",
            )
        )
    if validated_limits != list(REQUIRED_KNOWN_UNPROVED):
        raise ReleaseManifestVerificationError(
            "known_unproved must exactly retain the four conservative authenticity boundaries"
        )

    policy = validate_policy(manifest["payload_policy"])
    computed_policy = policy_digest(policy)
    if manifest["payload_policy_sha256"] != computed_policy:
        raise ReleaseManifestVerificationError("payload policy digest mismatch")
    _require_sha256(manifest["payload_policy_sha256"], "payload_policy_sha256")
    if expected_policy_sha256 is not None:
        _require_sha256(expected_policy_sha256, "expected policy SHA-256")
        if computed_policy != expected_policy_sha256:
            raise ReleaseManifestVerificationError(
                "payload policy differs from independently frozen policy"
            )

    selected: list[dict[str, Any]] | None = None
    selected_paths: set[str] | None = None
    if repository is not None:
        if not all(
            value is not None
            for value in (expected_policy_sha256, expected_release_id, expected_declared_ref)
        ):
            raise ReleaseManifestVerificationError(
                "repository verification requires frozen policy, release id, and declared tag"
            )
        if manifest_path is None:
            raise ReleaseManifestVerificationError(
                "repository verification requires the separate manifest path"
            )
        known_manifest_path = canonical_relative(manifest_path, "manifest path")
        repository_member(repository, known_manifest_path, "manifest path")
        if not any(
            item["path"] == known_manifest_path and item["scope"] == "FILE"
            for item in policy["exclude"]
        ):
            raise ReleaseManifestVerificationError(
                "release manifest path must be an exact FILE policy exclusion"
            )
        selected = selected_records(repository, policy)
        selected_paths = {item["path"] for item in selected}
        if release["payload_sha256"] != payload_digest(selected):
            raise ReleaseManifestVerificationError(
                "complete eligible consumer payload aggregate mismatch"
            )
    _validate_lineage(manifest["lineage_receipts"], policy, repository, selected_paths)


def verify_release_manifest(
    manifest: Any,
    repository: Path | None = None,
    manifest_path: str | None = None,
    *,
    expected_policy_sha256: str | None = None,
    expected_release_id: str | None = None,
    expected_declared_ref: str | None = None,
) -> None:
    """Validate a RELEASE candidate, optionally against a frozen local tree.

    Repository-backed verification requires independently frozen policy, release-ID,
    and declared-tag expectations. Illustrative manifests are deliberately rejected;
    use :func:`verify_illustrative_manifest` for structure-only example validation.
    """
    _verify_manifest(
        manifest,
        repository,
        manifest_path,
        expected_policy_sha256=expected_policy_sha256,
        expected_release_id=expected_release_id,
        expected_declared_ref=expected_declared_ref,
    )


def verify_illustrative_manifest(manifest: Any) -> None:
    """Validate an illustrative manifest's structure without proving a release."""
    _verify_manifest(manifest, illustrative_schema_only=True)


def load_manifest(path: Path) -> Any:
    """Read one raw manifest without allowing duplicate JSON object keys."""
    if path.is_symlink() or not path.is_file():
        raise ReleaseManifestVerificationError("release manifest must be a regular JSON file")
    try:
        return strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateJsonKeyError) as exc:
        raise ReleaseManifestVerificationError(f"invalid release manifest: {exc}") from exc


def _read_manifest(repository: Path, manifest_path: str) -> Any:
    return load_manifest(repository_member(repository, manifest_path, "manifest path"))


def _resolve_argument(path: Path, label: str) -> Path:
    """Resolve a command-line path, reporting a symlink loop as a verification failure."""
    try:
        return path.resolve()
    except RuntimeError as exc:  # Python 3.11 and 3.12 report a symlink loop this way.
        raise ReleaseManifestVerificationError(f"{label} is a symlink loop: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    """Run the command line and return the exit code."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--manifest", required=True, help="repository-relative manifest path")
    parser.add_argument("--expected-policy-sha256", required=True)
    parser.add_argument("--expected-release-id", required=True)
    parser.add_argument("--expected-declared-ref", required=True)
    args = parser.parse_args(argv)
    try:
        repository = _resolve_argument(args.repository, "repository")
        manifest = _read_manifest(repository, args.manifest)
        verify_release_manifest(
            manifest,
            repository,
            args.manifest,
            expected_policy_sha256=args.expected_policy_sha256,
            expected_release_id=args.expected_release_id,
            expected_declared_ref=args.expected_declared_ref,
        )
    except (OSError, UnicodeDecodeError, ReleaseManifestVerificationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "claim": "COMPACT_POLICY_AND_COMPLETE_LOCAL_PAYLOAD_ONLY",
                "completeness": "VERIFIED_AGAINST_EXPANDED_FROZEN_POLICY",
                "manifest_kind": manifest["manifest_kind"],
                "payload_sha256": manifest["release"]["payload_sha256"],
                "policy_sha256": manifest["payload_policy_sha256"],
                "release_ready": False,
                "remote_authenticity": "UNPROVED_LOCAL_ONLY",
                "signature_authenticity": "UNPROVED_NOT_EVALUATED",
                "status": "PASS",
                "tag_verified": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
