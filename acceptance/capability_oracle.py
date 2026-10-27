"""Offline structural oracle for the opt-in capability library.

The oracle proves inventory, selection isolation and fake decision behavior only. It
does not install a capability or contact Git, networks, services, databases or rigs.
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
    from .unicode_policy import visible_markdown_lines
else:
    from strict_json import DuplicateJsonKeyError
    from strict_json import loads as strict_json_loads
    from unicode_policy import visible_markdown_lines  # type: ignore[no-redef]


MODULE_IDS = (
    "testing-feedback",
    "delivery-git-hooks",
    "ci-build-release-deploy",
    "quality-evaluation",
    "code-native-graphics",
    "data-database-operations",
    "security-privacy-secrets",
    "dependencies-licences",
    "observability-diagnostics",
    "api-service-contracts",
    "public-api-catalogue",
    "device-rig-app-control",
)
MODULE_ID_SET = set(MODULE_IDS)
# Ignored working folders that repository-wide scans skip.
UNTRACKED_PARTS = {".git", ".acceptance-work", "__pycache__", ".mypy_cache"}
DISPOSITIONS = {"ADOPT", "MERGE INTO EXISTING", "CITE ONLY", "OMIT"}
MANIFEST_LIBRARY_ID = "agent-warmboot-optional-capabilities"
MANIFEST_AUTHORITY = "DISCOVERY_ONLY_NOT_TARGET_POLICY_OR_AUTHORIZATION"
MANIFEST_SELF_INVENTORY = (
    "EXCLUDED_TO_AVOID_RECURSIVE_HASH; validator requires this one MANIFEST.json "
    "in addition to every listed file"
)
CANONICAL_ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
AUTHORITY_KEYS = {
    "credentials",
    "database_mutation",
    "deployment",
    "device",
    "external_security_scan",
    "git_mutation",
    "hosted_ci",
    "llm_action",
    "local_process",
    "local_read",
    "network",
}
REFUSED_ACTIONS = {
    "GIT_MUTATION",
    "NETWORK_OR_PUBLIC_API",
    "CREDENTIAL_OR_ACCOUNT_ACCESS",
    "HOSTED_CI",
    "EXTERNAL_SECURITY_SCAN",
    "DATABASE_MUTATION",
    "DEPLOYMENT_OR_PUBLICATION",
    "DEVICE_OR_SIMULATOR_CONTROL",
    "APP_OR_LLM_ACTION",
}
SHA256_RE = re.compile(r"[0-9a-f]{64}")
# An inline link or image. Empty text counts only before a destination with no space and
# an optional quoted title, as Markdown requires, so a lambda such as `[](int value)` in
# code is not a link. Text and that check stop at `[`, so a run of brackets is scanned once.
# A quoted title may hold `)`; any other destination runs to the first `)`.
MARKDOWN_LINK_RE = re.compile(
    r"\[(?:[^\[\]]+|(?=\]\([^)\s\[]+(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)))\]\("
    r"([^)\s]+\s+(?:\"[^\"]*\"|'[^']*')(?=\s*\))|[^)]+)\s*\)"
)
# A quoted link title after the destination; it is not part of the path. It starts only at
# the beginning of a run of spaces, so a long run is scanned once.
LINK_TITLE_RE = re.compile(r"""(?<!\s)\s+(?:"[^"]*"|'[^']*')\s*$""")
# Catches a link a maintainer could paste in any Markdown form (inline, reference, autolink
# or bare text), not deliberate obfuscation, so the whole text is searched instead of
# parsing each link form. A scheme-relative link to a single-label host with no path or
# port (`//intranet`, `//intranet?view=1`) may pass. Each branch starts only at a lookbehind
# or word boundary, so the search stays linear. A scheme name followed by prose (a space, a
# closing span or quote, or sentence punctuation before a space) is not a link. An
# underscore is emphasis only when no letter or digit precedes it; a version after `@` is
# not an email domain. Any `<scheme:...>` autolink, and a one-line reference definition
# outside a blockquote whose destination starts with a scheme of 2 to 32 characters, is a
# link whatever the scheme; inline links are checked below.
EXTERNAL_URI_RE = re.compile(
    r"(?<![A-Za-z0-9+.-])[A-Za-z0-9+.-]*://\S*"
    r"|(?<![\w:/])//(?:\[|[A-Za-z0-9-]+(?:[./\"'>)]|:\d))\S*"
    r"|(?<![A-Za-z0-9/#.-])(?<![A-Za-z0-9]_)(?<![A-Za-z0-9]__)www\.[A-Za-z0-9-]+\S*"
    r"|(?<![A-Za-z0-9])(?<![A-Za-z0-9]_)(?<![A-Za-z0-9]__)(?:mailto|tel|javascript|data):"
    r"(?=\S)(?![`*_)\]>\"']|[.,;:!?](?:\s|$))\S*"
    r"|(?<![\w.+-])[\w.+-]+@(?!\d+\.\d)[A-Za-z0-9][A-Za-z0-9-]*\.(?:[A-Za-z0-9-]+\.)*[A-Za-z]{2,}"
    r"(?![A-Za-z0-9-]|\.[A-Za-z0-9])"
    r"|<[A-Za-z][A-Za-z0-9+.-]{1,31}:[^\s<>]*>"
    r"|(?m:^ {0,3}\[[^\]\n]+\]:[ \t]*<?[A-Za-z][A-Za-z0-9+.-]{1,31}:)",
    re.IGNORECASE,
)

PRIVACY_PATTERNS = {
    "LOCAL_ABSOLUTE_PATH": re.compile(
        r"(?<![A-Za-z0-9])" + re.escape(chr(47)) + r"(?:Users|home)" + re.escape(chr(47))
    ),
    "PRIVATE_IPV4": re.compile(
        r"(?<!\d)(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|"
        r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})(?!\d)"
    ),
    "SECRET_TOKEN": re.compile(
        r"(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|"
        r"AIza[A-Za-z0-9_-]{20,})"
    ),
    "CREDENTIAL_ASSIGNMENT": re.compile(
        r"(?i)(?:password|api[_-]?key|access[_-]?token|secret)\s*[:=]\s*"
        r"[\"']?[A-Za-z0-9+/=_-]{12,}"
    ),
}
PRIVACY_CANARIES = {
    "LOCAL_ABSOLUTE_PATH": chr(47).join(("", "home", "fictional-user", "private-input")),
    "PRIVATE_IPV4": "192.168.40.7",
    "SECRET_TOKEN": "ghp_abcdefghijklmnopqrstuvwxyz123456",
    # Assembled at run time so secret scanners do not flag this file.
    "CREDENTIAL_ASSIGNMENT": "".join(("api", "_key", "=", "abcdefghijkl", "mnopqrstuvwx")),  # noqa: FLY002
}


class CapabilityVerificationError(ValueError):
    """Raised when the library, a selection or a fake case violates its contract."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json(path: Path, label: str) -> Any:
    if path.is_symlink() or not path.is_file():
        raise CapabilityVerificationError(f"{label} must be a regular non-symlink file")
    try:
        return strict_json_loads(path.read_text(encoding="utf-8"))
    except DuplicateJsonKeyError as exc:
        key = str(exc).removeprefix("duplicate JSON object key: ")
        raise CapabilityVerificationError(f"duplicate JSON key in {label}: {key}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CapabilityVerificationError(f"invalid {label}: {exc}") from exc


def load_repository_json(repository: Path, path: Path, label: str) -> Any:
    """Load one repository-owned JSON file without following an in-repo symlink."""
    if repository.is_symlink() or not repository.is_dir():
        raise CapabilityVerificationError("attested repository must be a real directory")
    try:
        attested = repository.resolve(strict=True)
    # A link created after the check above can loop; 3.11 and 3.12 raise RuntimeError.
    except (OSError, RuntimeError) as exc:
        raise CapabilityVerificationError("attested repository cannot be resolved") from exc
    if path.is_absolute():
        try:
            relative_path = path.relative_to(repository)
        except ValueError as exc:
            raise CapabilityVerificationError(
                f"{label} must remain beneath the attested repository"
            ) from exc
    else:
        relative_path = path
    relative = _canonical_relative(relative_path.as_posix(), label)
    member = attested
    # Before Python 3.14, is_symlink() raises for an over-long or unsearchable component.
    try:
        for part in relative.parts:
            member = member / part
            if member.is_symlink():
                raise CapabilityVerificationError(
                    f"{label} must not traverse a symlink: {relative}"
                )
        resolved = member.resolve(strict=True)
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise CapabilityVerificationError(f"{label} must exist") from exc
    except OSError as exc:
        raise CapabilityVerificationError(f"{label} cannot be checked: {exc.strerror}") from exc
    # A link created after the walk above can still loop; 3.11 and 3.12 raise RuntimeError.
    except RuntimeError as exc:
        raise CapabilityVerificationError(f"{label} cannot be checked: symlink loop") from exc
    try:
        resolved.relative_to(attested)
    except ValueError as exc:
        raise CapabilityVerificationError(f"{label} escaped the attested repository") from exc
    return _load_json(resolved, label)


def _entries(directory: Path, skip: frozenset[str] = frozenset()) -> list[Path]:
    """Return every entry below a directory, failing on any entry it cannot inspect."""
    entries: list[Path] = []
    pending = [directory]
    while pending:
        for entry in pending.pop().iterdir():
            entries.append(entry)
            if entry.name not in skip and stat.S_ISDIR(entry.lstat().st_mode):
                pending.append(entry)
    return entries


def _strings(value: Any) -> bool:
    """Whether a JSON value is an array of strings, so set-based checks cannot raise."""
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _object(value: Any, required: set[str], label: str, *, exact: bool = True) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CapabilityVerificationError(f"{label} must be an object")
    keys = set(value)
    if (exact and keys != required) or (not exact and not required.issubset(keys)):
        raise CapabilityVerificationError(
            f"{label} keys differ: missing={sorted(required - keys)}, "
            f"extra={sorted(keys - required) if exact else []}"
        )
    return value


def _canonical_relative(raw: Any, label: str) -> PurePosixPath:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        raise CapabilityVerificationError(f"{label} must be a non-empty POSIX path")
    path = PurePosixPath(raw)
    if (
        path.is_absolute()
        or path.as_posix() != raw
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise CapabilityVerificationError(f"{label} must be canonical and relative: {raw!r}")
    return path


def privacy_findings(text: str) -> set[str]:
    """Return privacy/secret detector names matched by text."""
    return {name for name, pattern in PRIVACY_PATTERNS.items() if pattern.search(text)}


def _validate_privacy_detector() -> None:
    for expected, canary in PRIVACY_CANARIES.items():
        findings = privacy_findings(canary)
        if expected not in findings:
            raise CapabilityVerificationError(
                f"privacy detector is ineffective for built-in {expected} canary"
            )


def _read_text_member(root: Path, relative: str) -> str:
    member = root / relative
    if member.is_symlink() or not member.is_file():
        raise CapabilityVerificationError(f"inventory member is not a regular file: {relative}")
    try:
        return member.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise CapabilityVerificationError(
            f"inventory member is not UTF-8 text: {relative}"
        ) from exc


def _source_ids_from_card(text: str, module_id: str) -> set[str]:
    marker = "- Source IDs:"
    lines = visible_markdown_lines(text)
    field_indexes = [index for index, line in enumerate(lines) if line.startswith(marker)]
    if len(field_indexes) != 1:
        raise CapabilityVerificationError(
            f"module {module_id} must have exactly one Source IDs field"
        )

    index = field_indexes[0]
    payload_parts = [lines[index][len(marker) :].strip(" \t")]
    for line in lines[index + 1 :]:
        if line.startswith("- ") or not line.strip(" \t"):
            break
        if not line.startswith("  "):
            raise CapabilityVerificationError(
                f"module {module_id} has malformed Source IDs continuation"
            )
        payload_parts.append(line.strip(" \t"))

    payload = " ".join(payload_parts).strip(" \t")
    if not payload.endswith("."):
        raise CapabilityVerificationError(
            f"module {module_id} Source IDs field must end with a period"
        )
    payload = payload[:-1].strip(" \t")
    if not payload:
        raise CapabilityVerificationError(f"module {module_id} declares no Source IDs")

    ordered_source_ids: list[str] = []
    for raw_item in payload.split(","):
        item = raw_item.strip(" \t")
        match = re.fullmatch(r"`([^`]*)`", item)
        if match is None or CANONICAL_ID_RE.fullmatch(match.group(1)) is None:
            raise CapabilityVerificationError(
                f"module {module_id} has a noncanonical Source ID: {item}"
            )
        ordered_source_ids.append(match.group(1))
    if len(ordered_source_ids) != len(set(ordered_source_ids)):
        raise CapabilityVerificationError(f"module {module_id} has a duplicate Source ID")
    return set(ordered_source_ids)


def _validate_local_links(repository: Path, relative: str, text: str) -> None:
    external = EXTERNAL_URI_RE.search(text)
    if external is not None:
        raise CapabilityVerificationError(f"external link in {relative}: {external.group(0)}")
    source = repository / relative
    for raw in MARKDOWN_LINK_RE.findall(text):
        target = LINK_TITLE_RE.sub("", raw).split("#", 1)[0]
        if not target:
            continue
        if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target):
            raise CapabilityVerificationError(f"external link in {relative}: {raw}")
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        target_path = PurePosixPath(target)
        if (
            target_path.is_absolute()
            or "\\" in target
            or any(part == "" for part in target_path.parts)
        ):
            raise CapabilityVerificationError(f"unsafe local link in {relative}: {raw}")
        member = source.parent / target_path.as_posix()
        try:
            resolved = member.resolve(strict=True)
            resolved_relative = resolved.relative_to(repository)
        # Python 3.11 and 3.12 raise RuntimeError for a symlink loop.
        except (OSError, RuntimeError, ValueError) as exc:
            raise CapabilityVerificationError(
                f"broken or escaping local link in {relative}: {raw}"
            ) from exc
        current = repository
        for part in resolved_relative.parts:
            current = current / part
            if current.is_symlink():
                raise CapabilityVerificationError(f"symlinked local link in {relative}: {raw}")
        if not resolved.is_file():
            raise CapabilityVerificationError(f"broken local link in {relative}: {raw}")


def _validated_sources(document: Any) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Resolve local design evidence or explicitly synthetic rights inputs.

    Entry fields cannot override inherited source rights. Synthetic restrictions
    exercise refusal without pretending to describe a real third-party source.
    """
    catalog = _object(
        document, {"schema_version", "status", "authority", "sources", "entries"}, "source catalog"
    )
    if type(catalog["schema_version"]) is not int or catalog["schema_version"] != 1:
        raise CapabilityVerificationError("source catalog schema_version must be integer 1")
    if not isinstance(catalog["status"], str):
        raise CapabilityVerificationError("source catalog status must be text")
    synthetic = catalog["status"] == "SYNTHETIC_VALIDATION_INPUTS"
    if (
        catalog["status"] not in {"TOOLKIT_LOCAL_DESIGN_REFERENCES", "SYNTHETIC_VALIDATION_INPUTS"}
        or catalog["authority"] != "DESIGN_AND_RIGHTS_EVIDENCE_ONLY"
    ):
        raise CapabilityVerificationError("source catalog authority/status differs")
    sources = catalog["sources"]
    if not isinstance(sources, list) or not sources:
        raise CapabilityVerificationError("source catalog needs sources")
    by_source = {}
    for raw in sources:
        source = _object(raw, {"id", "kind", "path", "sha256", "rights"}, "source")
        identifier = source["id"]
        if (
            not isinstance(identifier, str)
            or not CANONICAL_ID_RE.fullmatch(identifier)
            or identifier in by_source
        ):
            raise CapabilityVerificationError("source IDs must be canonical and unique")
        if source["kind"] != ("SYNTHETIC" if synthetic else "TOOLKIT-LOCAL"):
            raise CapabilityVerificationError("source kind differs")
        _canonical_relative(source["path"], "source path")
        if not isinstance(source["sha256"], str) or not SHA256_RE.fullmatch(source["sha256"]):
            raise CapabilityVerificationError("source digest must be SHA-256")
        rights = _object(source["rights"], {"spdx"}, "source rights")
        expected = {"spdx": "LicenseRef-Synthetic-Restricted"} if synthetic else {"spdx": "MIT"}
        if rights != expected:
            raise CapabilityVerificationError("source rights differ")
        by_source[identifier] = source
    entries = catalog["entries"]
    if not isinstance(entries, list) or not entries:
        raise CapabilityVerificationError("source catalog needs entries")
    seen = set()
    modules = set()
    used = set()
    for raw in entries:
        entry = _object(raw, {"id", "module_id", "source_id", "rationale"}, "source entry")
        identifier = entry["id"]
        module = entry["module_id"]
        if (
            not isinstance(identifier, str)
            or not CANONICAL_ID_RE.fullmatch(identifier)
            or identifier in seen
        ):
            raise CapabilityVerificationError("entry IDs must be canonical and unique")
        if (
            not isinstance(module, str)
            or module not in MODULE_ID_SET
            or module in modules
            or identifier != module + "-design"
        ):
            raise CapabilityVerificationError("source module mapping differs")
        if not isinstance(entry["source_id"], str) or entry["source_id"] not in by_source:
            raise CapabilityVerificationError("unknown source ID")
        if not isinstance(entry["rationale"], str) or not entry["rationale"].strip():
            raise CapabilityVerificationError("source rationale is required")
        seen.add(identifier)
        modules.add(module)
        used.add(entry["source_id"])
    if used != set(by_source):
        raise CapabilityVerificationError("unused source declaration")
    if privacy_findings(json.dumps(catalog)):
        raise CapabilityVerificationError("source catalog contains a private/secret literal")
    return catalog, by_source


def validate_source_catalog(document: Any) -> set[str]:
    """Validate strict source fields without granting publication authority."""
    catalog, _ = _validated_sources(document)
    return {entry["id"] for entry in catalog["entries"]}


def effective_source_claim(document: Any, entry_id: str) -> dict[str, Any]:
    """Resolve rights from the source; entries have no overriding rights fields."""
    catalog, sources = _validated_sources(document)
    entry = next((entry for entry in catalog["entries"] if entry["id"] == entry_id), None)
    if entry is None:
        raise CapabilityVerificationError(f"unknown source entry: {entry_id}")
    source = sources[entry["source_id"]]
    return {
        **entry,
        "kind": source["kind"],
        "path": source["path"],
        "sha256": source["sha256"],
        "rights": dict(source["rights"]),
    }


def _validate_source_bytes(repository: Path, catalog: Any) -> set[str]:
    """Bind evidence to regular contained files, rejecting synthetic admission."""
    source_ids = validate_source_catalog(catalog)
    if catalog["status"] != "TOOLKIT_LOCAL_DESIGN_REFERENCES":
        raise CapabilityVerificationError("synthetic sources cannot enter the real library")
    if {entry["module_id"] for entry in catalog["entries"]} != MODULE_ID_SET:
        raise CapabilityVerificationError("source catalog must cover every module")
    for source in catalog["sources"]:
        relative = _canonical_relative(source["path"], "source path")
        member = repository
        # Before Python 3.14, is_symlink() raises for an over-long or unsearchable component.
        try:
            for part in relative.parts:
                member = member / part
                if member.is_symlink():
                    raise CapabilityVerificationError("source must not traverse a symlink")
            data = member.read_bytes() if stat.S_ISREG(member.stat().st_mode) else None
        except (FileNotFoundError, NotADirectoryError):
            data = None
        except OSError as exc:
            raise CapabilityVerificationError(f"source cannot be checked: {exc.strerror}") from exc
        if data is None or _sha256(data) != source["sha256"]:
            raise CapabilityVerificationError("source byte/digest mismatch")
    return source_ids


def validate_library(repository: Path) -> dict[str, Any]:
    """Validate the optional library rooted in a repository checkout."""
    if repository.is_symlink() or not repository.is_dir():
        raise CapabilityVerificationError("attested repository must be a real directory")
    try:
        repository = repository.resolve(strict=True)
    # A link created after the check above can loop; 3.11 and 3.12 raise RuntimeError.
    except (OSError, RuntimeError) as exc:
        raise CapabilityVerificationError("attested repository cannot be resolved") from exc
    library = repository / "templates" / "capabilities"
    if library.is_symlink() or not library.is_dir():
        raise CapabilityVerificationError("capability library must be a real directory")
    _validate_privacy_detector()

    manifest = load_repository_json(
        repository, Path("templates/capabilities/MANIFEST.json"), "capability manifest"
    )
    manifest = _object(
        manifest,
        {
            "schema_version",
            "library_id",
            "authority",
            "always_loaded",
            "auto_installed",
            "default_selection",
            "requires",
            "related_modules_are_navigation_only",
            "manifest_self_inventory",
            "allowed_dispositions",
            "files",
        },
        "capability manifest",
    )
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise CapabilityVerificationError("capability manifest schema_version must be integer 1")
    if manifest["library_id"] != MANIFEST_LIBRARY_ID:
        raise CapabilityVerificationError("capability manifest library_id differs")
    if manifest["authority"] != MANIFEST_AUTHORITY:
        raise CapabilityVerificationError("capability manifest authority differs")
    if manifest["manifest_self_inventory"] != MANIFEST_SELF_INVENTORY:
        raise CapabilityVerificationError("capability manifest self-inventory rule differs")
    if manifest["always_loaded"] is not False or manifest["auto_installed"] is not False:
        raise CapabilityVerificationError(
            "capability library must never be always-loaded or auto-installed"
        )
    if manifest["default_selection"] != [] or manifest["requires"] != []:
        raise CapabilityVerificationError(
            "capability library must have empty defaults and requires"
        )
    if manifest["related_modules_are_navigation_only"] is not True:
        raise CapabilityVerificationError("related modules must be navigation only")
    if (
        not _strings(manifest["allowed_dispositions"])
        or set(manifest["allowed_dispositions"]) != DISPOSITIONS
        or len(manifest["allowed_dispositions"]) != 4
    ):
        raise CapabilityVerificationError("allowed dispositions differ from the exact accepted set")

    files = manifest["files"]
    if not isinstance(files, list):
        raise CapabilityVerificationError("manifest files must be an array")
    by_path: dict[str, dict[str, Any]] = {}
    for index, raw_entry in enumerate(files):
        entry = _object(
            raw_entry,
            {"path", "kind", "sha256", "bytes", "mode", "requires", "related_modules", "hazards"},
            f"manifest files[{index}]",
            exact=False,
        )
        relative = _canonical_relative(entry["path"], f"manifest files[{index}].path").as_posix()
        if relative in by_path:
            raise CapabilityVerificationError(f"duplicate manifest path: {relative}")
        by_path[relative] = entry
        if entry["requires"] != []:
            raise CapabilityVerificationError(f"module requirements are forbidden: {relative}")
        if entry["mode"] != "0644":
            raise CapabilityVerificationError(f"manifest mode must be 0644: {relative}")
        if (
            not isinstance(entry["bytes"], int)
            or isinstance(entry["bytes"], bool)
            or entry["bytes"] < 1
        ):
            raise CapabilityVerificationError(f"invalid byte count: {relative}")
        if not isinstance(entry["sha256"], str) or not SHA256_RE.fullmatch(entry["sha256"]):
            raise CapabilityVerificationError(f"invalid SHA-256: {relative}")
        if (
            not _strings(entry["related_modules"])
            or len(entry["related_modules"]) != len(set(entry["related_modules"]))
            or not all(
                isinstance(item, str) and CANONICAL_ID_RE.fullmatch(item)
                for item in entry["related_modules"]
            )
            or not set(entry["related_modules"]).issubset(MODULE_ID_SET)
        ):
            raise CapabilityVerificationError(f"unknown related module: {relative}")
        if "source_refs" in entry and (
            not _strings(entry["source_refs"])
            or len(entry["source_refs"]) != len(set(entry["source_refs"]))
            or not all(
                isinstance(item, str) and CANONICAL_ID_RE.fullmatch(item)
                for item in entry["source_refs"]
            )
        ):
            raise CapabilityVerificationError(f"invalid source refs: {relative}")
        if (
            not _strings(entry["hazards"])
            or not entry["hazards"]
            or len(entry["hazards"]) != len(set(entry["hazards"]))
            or not all(
                isinstance(item, str) and CANONICAL_ID_RE.fullmatch(item)
                for item in entry["hazards"]
            )
        ):
            raise CapabilityVerificationError(f"invalid hazards: {relative}")

    actual_files: set[str] = set()
    try:
        library_entries = _entries(library)
    except OSError as exc:
        raise CapabilityVerificationError(
            f"capability library cannot be listed: {exc.strerror}"
        ) from exc
    for member in library_entries:
        relative = member.relative_to(library).as_posix()
        if member.is_symlink():
            raise CapabilityVerificationError(
                f"symlink forbidden in capability library: {relative}"
            )
        if member.is_file():
            actual_files.add(relative)
    if actual_files != set(by_path) | {"MANIFEST.json"}:
        raise CapabilityVerificationError(
            f"manifest inventory differs: missing={sorted(actual_files - set(by_path) - {'MANIFEST.json'})}, "
            f"extra={sorted(set(by_path) - actual_files)}"
        )

    catalog = load_repository_json(
        repository, Path("docs/capability-sources.json"), "source catalog"
    )
    source_ids = _validate_source_bytes(repository, catalog)

    module_ids: list[str] = []
    manifest_source_refs: set[str] = set()
    for relative, entry in by_path.items():
        member = library / relative
        data = member.read_bytes()
        if len(data) != entry["bytes"] or _sha256(data) != entry["sha256"]:
            raise CapabilityVerificationError(f"manifest byte/hash mismatch: {relative}")
        # Checkout umask may add group/other bits; only the type and execute bits matter.
        member_mode = member.lstat().st_mode
        if not stat.S_ISREG(member_mode) or member_mode & 0o111:
            raise CapabilityVerificationError(f"must be a regular non-executable file: {relative}")
        text = _read_text_member(library, relative)
        findings = privacy_findings(text)
        if findings:
            raise CapabilityVerificationError(
                f"unsafe literal(s) in {relative}: {sorted(findings)}"
            )
        if relative.endswith(".md"):
            _validate_local_links(repository, f"templates/capabilities/{relative}", text)
        if entry["kind"] == "module":
            if set(entry) != {
                "path",
                "kind",
                "module_id",
                "sha256",
                "bytes",
                "mode",
                "requires",
                "related_modules",
                "hazards",
            }:
                raise CapabilityVerificationError(f"module manifest keys differ: {relative}")
            module_id = entry["module_id"]
            if (
                not isinstance(module_id, str)
                or module_id not in MODULE_ID_SET
                or relative != f"{module_id}.md"
            ):
                raise CapabilityVerificationError(f"invalid module identity: {relative}")
            if module_id in entry["related_modules"]:
                raise CapabilityVerificationError(f"module isolation metadata differs: {relative}")
            if f"- ID: `{module_id}`" not in text:
                raise CapabilityVerificationError(f"card ID does not match manifest: {relative}")
            card_refs = _source_ids_from_card(text, module_id)
            if not card_refs.issubset(source_ids):
                raise CapabilityVerificationError(
                    f"unresolved source ref in {relative}: {sorted(card_refs - source_ids)}"
                )
            if card_refs != {module_id + "-design"}:
                raise CapabilityVerificationError("module/source mapping differs")
            manifest_source_refs.update(card_refs)
            module_ids.append(module_id)
        elif entry["kind"] == "index":
            if relative != "README.md" or set(entry) != {
                "path",
                "kind",
                "sha256",
                "bytes",
                "mode",
                "requires",
                "related_modules",
                "hazards",
                "source_refs",
            }:
                raise CapabilityVerificationError("only README.md may be the index")
            refs = entry["source_refs"]
            if not set(refs).issubset(source_ids):
                raise CapabilityVerificationError(
                    f"unresolved source ref in {relative}: {sorted(set(refs) - source_ids)}"
                )
            manifest_source_refs.update(refs)
        else:
            raise CapabilityVerificationError(f"unknown manifest kind: {entry['kind']!r}")

    if tuple(module_ids) != MODULE_IDS or len(module_ids) != 12:
        raise CapabilityVerificationError(f"module inventory/order differs: {module_ids}")
    if manifest_source_refs != source_ids:
        raise CapabilityVerificationError(
            f"manifest/catalog source inventory differs: unused={sorted(source_ids - manifest_source_refs)}, "
            f"missing={sorted(manifest_source_refs - source_ids)}"
        )
    try:
        repository_entries = _entries(repository, frozenset(UNTRACKED_PARTS))
    except OSError as exc:
        raise CapabilityVerificationError(f"repository cannot be listed: {exc.strerror}") from exc
    all_templates = {
        path.relative_to(repository).as_posix()
        for path in repository_entries
        if path.name.endswith(".tmpl")
    }
    if all_templates:
        raise CapabilityVerificationError(
            f"repository must not contain shell templates: {sorted(all_templates)}"
        )

    return manifest


def validate_selection(repository: Path, selection: Any, *, outsider: bool = False) -> None:
    """Check a capability selection against the library, raising on any violation."""
    validate_library(repository)
    selection = _object(
        selection,
        {
            "schema_version",
            "selection_id",
            "target",
            "authority",
            "considered_modules",
            "dispositions",
        }
        | ({"live_boundary"} if outsider else set()),
        "selection",
    )
    if type(selection["schema_version"]) is not int or selection["schema_version"] != 1:
        raise CapabilityVerificationError("selection schema_version must be integer 1")
    authority = _object(selection["authority"], AUTHORITY_KEYS, "selection authority")
    if any(type(value) is not bool for value in authority.values()):
        raise CapabilityVerificationError("selection authority values must be booleans")
    considered = selection["considered_modules"]
    if (
        not _strings(considered)
        or len(considered) != len(set(considered))
        or not set(considered).issubset(MODULE_ID_SET)
    ):
        raise CapabilityVerificationError("considered_modules must be unique accepted module IDs")
    dispositions = selection["dispositions"]
    if not isinstance(dispositions, list):
        raise CapabilityVerificationError("selection dispositions must be an array")
    disposition_ids: list[str] = []
    for index, raw in enumerate(dispositions):
        item = _object(
            raw,
            {
                "module_id",
                "disposition",
                "destination",
                "surviving_owner",
                "evidence",
                "unproved_boundary",
                "revisit_trigger",
            },
            f"selection dispositions[{index}]",
            exact=False,
        )
        module_id = item["module_id"]
        if (
            not isinstance(module_id, str)
            or module_id not in MODULE_ID_SET
            or not isinstance(item["disposition"], str)
            or item["disposition"] not in DISPOSITIONS
        ):
            raise CapabilityVerificationError(f"invalid disposition at index {index}")
        if not all(
            isinstance(item[key], str) and item[key].strip()
            for key in ("destination", "surviving_owner", "unproved_boundary", "revisit_trigger")
        ):
            raise CapabilityVerificationError(
                f"disposition text fields must be non-empty: {module_id}"
            )
        evidence = item["evidence"]
        if set(item) != {
            "module_id",
            "disposition",
            "destination",
            "surviving_owner",
            "evidence",
            "unproved_boundary",
            "revisit_trigger",
        }:
            raise CapabilityVerificationError(f"disposition keys differ: {module_id}")
        if (
            not isinstance(evidence, list)
            or not evidence
            or not all(isinstance(value, str) and value.strip() for value in evidence)
        ):
            raise CapabilityVerificationError(
                f"disposition evidence must be non-empty: {module_id}"
            )
        disposition_ids.append(module_id)
    if disposition_ids != considered:
        raise CapabilityVerificationError(
            "dispositions must cover considered_modules exactly and in order"
        )

    if outsider:
        if tuple(considered) != MODULE_IDS:
            raise CapabilityVerificationError("outsider fixture must dispose all twelve modules")
        denied = {key for key, value in authority.items() if not value}
        required_denied = AUTHORITY_KEYS - {"local_read", "local_process"}
        if not required_denied.issubset(denied):
            raise CapabilityVerificationError("outsider fixture grants forbidden live authority")
        boundary = _object(
            selection["live_boundary"], {"simulation", "live", "refused_actions"}, "live boundary"
        )
        if boundary["simulation"] != "PROVED_BY_LOCAL_FAKES" or boundary["live"] != "UNPROVED":
            raise CapabilityVerificationError(
                "outsider fixture must separate fake proof from live UNPROVED"
            )
        refused = boundary["refused_actions"]
        if (
            not _strings(refused)
            or set(refused) != REFUSED_ACTIONS
            or len(refused) != len(REFUSED_ACTIONS)
        ):
            raise CapabilityVerificationError(
                "outsider fixture must refuse every unauthorized action"
            )


AUTHORITY_REASONS = {
    "DEPLOY": "DEPLOYMENT_AUTHORITY_REQUIRED",
    "RIG_LIVE": "DEVICE_AUTHORITY_REQUIRED",
    "DATABASE_MUTATION": "DATABASE_MUTATION_AUTHORITY_REQUIRED",
    "HOSTED_CI": "HOSTED_CI_AUTHORITY_REQUIRED",
    "EXTERNAL_SECURITY_SCAN": "EXTERNAL_SECURITY_SCAN_AUTHORITY_REQUIRED",
}


def evaluate_fake_case(case: Any) -> dict[str, Any]:
    """Return the decision record one local fake case produces, raising if it is malformed."""
    case = _object(
        case,
        {
            "case_id",
            "operation",
            "authority",
            "simulation",
            "retry_limit",
            "status_sequence",
            "expected",
        },
        "fake case",
    )
    if case["simulation"] is not True:
        raise CapabilityVerificationError("fake case must be explicitly simulated")
    if type(case["authority"]) is not bool:
        raise CapabilityVerificationError("fake case authority must be boolean")
    retry_limit = case["retry_limit"]
    if type(retry_limit) is not int or retry_limit < 0 or retry_limit > 2:
        raise CapabilityVerificationError("fake retry_limit must be an integer from zero to two")
    sequence = case["status_sequence"]
    if not isinstance(sequence, list):
        raise CapabilityVerificationError("fake status_sequence must be an array")
    if any(type(status) is not int and type(status) is not str for status in sequence):
        raise CapabilityVerificationError("fake status_sequence elements must be exact int or str")
    operation = case["operation"]
    if not isinstance(operation, str):
        raise CapabilityVerificationError("fake operation must be a string")
    if operation in AUTHORITY_REASONS:
        if case["authority"] is not False or sequence:
            raise CapabilityVerificationError(
                "hazard fake must exercise missing authority without attempts"
            )
        return {
            "attempts": 0,
            "decision": "REFUSE_AUTHORITY",
            "live_proof": "UNPROVED",
            "reason": AUTHORITY_REASONS[operation],
        }
    if operation != "API_FAKE" or case["authority"] is not True or not sequence:
        raise CapabilityVerificationError("unsupported or malformed fake operation")

    attempts = 0
    transient = False
    for status_value in sequence[: retry_limit + 1]:
        attempts += 1
        if status_value == 200:
            return {
                "attempts": attempts,
                "decision": "PASS_FAKE",
                "live_proof": "UNPROVED",
                "reason": "RECOVERED_AFTER_BOUNDED_RETRY" if transient else "FAKE_SUCCESS",
            }
        if status_value in (401, 403):
            return {
                "attempts": attempts,
                "decision": "STOP_AUTH_FAILURE",
                "live_proof": "UNPROVED",
                "reason": "AUTH_OR_CREDENTIAL_FAILURE",
            }
        if status_value == "MALFORMED":
            return {
                "attempts": attempts,
                "decision": "FAIL_CLOSED",
                "live_proof": "UNPROVED",
                "reason": "MALFORMED_RESPONSE",
            }
        if (
            status_value == "TIMEOUT"
            or status_value == 429
            or (
                isinstance(status_value, int)
                and not isinstance(status_value, bool)
                and 500 <= status_value <= 599
            )
        ):
            transient = True
            continue
        return {
            "attempts": attempts,
            "decision": "FAIL_CLOSED",
            "live_proof": "UNPROVED",
            "reason": "UNEXPECTED_FAKE_STATUS",
        }
    return {
        "attempts": attempts,
        "decision": "FAIL_CLOSED",
        "live_proof": "UNPROVED",
        "reason": "TRANSIENT_RETRY_EXHAUSTED",
    }


def verify_fake_cases(document: Any) -> list[dict[str, Any]]:
    """Check each fake case's decision and the case coverage, and return the outcomes."""
    document = _object(document, {"schema_version", "cases"}, "fake cases")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise CapabilityVerificationError("fake cases schema_version must be integer 1")
    cases = document["cases"]
    if not isinstance(cases, list) or not cases:
        raise CapabilityVerificationError("fake cases must be a non-empty array")
    observed: list[dict[str, Any]] = []
    case_ids: set[str] = set()
    for case in cases:
        if (
            not isinstance(case, dict)
            or not isinstance(case.get("case_id"), str)
            or case["case_id"] in case_ids
        ):
            raise CapabilityVerificationError("fake case IDs must be unique strings")
        case_ids.add(case["case_id"])
        decision = evaluate_fake_case(case)
        expected = _object(
            case["expected"],
            {"attempts", "decision", "live_proof", "reason"},
            "fake expected decision",
        )
        if type(expected["attempts"]) is not int or expected["attempts"] < 0:
            raise CapabilityVerificationError(
                "fake expected attempts must be a nonnegative integer"
            )
        if decision != expected:
            raise CapabilityVerificationError(
                f"fake decision differs for {case['case_id']}: expected={expected!r}, observed={decision!r}"
            )
        observed.append({"case_id": case["case_id"], **decision, "scope": "LOCAL_FAKE_ONLY"})
    required_cases = {
        "deploy-without-authority",
        "rig-without-holder-or-authority",
        "api-401-stops",
        "api-429-bounded-retry-recovers",
        "api-5xx-bounded-retry-exhausted",
        "api-timeout-bounded-retry-exhausted",
        "api-malformed-fails-closed",
        "database-mutation-without-authority",
        "hosted-ci-without-authority",
        "external-security-scan-without-authority",
    }
    if case_ids != required_cases:
        raise CapabilityVerificationError(f"fake case coverage differs: {sorted(case_ids)}")
    return observed


def main(argv: list[str] | None = None) -> int:
    """Run the command line and return the exit code."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--selection", type=Path)
    parser.add_argument("--outsider", action="store_true")
    parser.add_argument("--fake-cases", type=Path)
    args = parser.parse_args(argv)
    try:
        validate_library(args.repository)
        if args.selection:
            validate_selection(
                args.repository, _load_json(args.selection, "selection"), outsider=args.outsider
            )
        if args.fake_cases:
            verify_fake_cases(_load_json(args.fake_cases, "fake cases"))
    except (OSError, UnicodeDecodeError, CapabilityVerificationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"scope": "STRUCTURE_AND_LOCAL_FAKES_ONLY", "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
