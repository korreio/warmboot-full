"""Exercise the self-improvement oracle's fixture and fail-closed boundaries."""

import copy
import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from acceptance.release_manifest import (
    CLAIMS,
    IDENTITY_KIND,
    RECORD_ENCODING,
    RELEASE_KEYS,
    REPRESENTATION,
    REQUIRED_KNOWN_UNPROVED,
    TOP_LEVEL_KEYS,
    ReleaseManifestVerificationError,
    load_manifest,
    payload_digest,
    policy_digest,
    selected_records,
)
from acceptance.release_manifest import (
    main as release_manifest_main,
)
from acceptance.release_manifest import (
    verify_illustrative_manifest as verify_compact_illustrative_manifest,
)
from acceptance.release_manifest import (
    verify_release_manifest as verify_compact_release_manifest,
)
from acceptance.self_improvement_oracle import (
    SelfImprovementVerificationError,
    _member,
    _validate_topology,
    expected_response,
    main,
    verify,
    verify_illustrative_release_manifest,
    verify_maintainer_repository,
    verify_release_manifest,
    verify_scope_change_record,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "acceptance" / "fixtures" / "self-improvement-package"
SCOPE_CHANGE_FIXTURE = ROOT / "acceptance" / "fixtures" / "scope-change-package"
MANIFEST_PATH = "release-manifest.json"
RELEASE_ID = "test-candidate"
DECLARED_REF = "agent-warmboot-v0.0.0-test"
LIMITS = list(REQUIRED_KNOWN_UNPROVED)


def _write(path: Path, body: bytes, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    path.chmod(0o755 if executable else 0o644)


def _release_tree(root: Path) -> dict[str, object]:
    _write(root / "WARMBOOT.md", b"# Warmboot\n\nProvider-neutral entry.\n")
    _write(root / "bin/warmboot", b"# Synthetic inert helper fixture\n", executable=True)
    _write(root / "docs/release.md", b"# Release policy\n")
    _write(root / "docs/source-refresh.md", b"# Admitting reusable lessons\n")
    _write(root / "templates/project-docs/README.md", b"# Template\n")
    _write(root / "scratch/omitted.md", b"scratch\n")
    policy = {
        "include": ["."],
        "exclude": [
            {
                "path": MANIFEST_PATH,
                "scope": "FILE",
                "reason": "The commit-contained manifest cannot hash its own bytes.",
                "bound_receipt": "docs/release.md",
            },
            {
                "path": "scratch",
                "scope": "SUBTREE",
                "reason": "Local scratch is not consumer payload.",
                "bound_receipt": "docs/release.md",
            },
        ],
    }
    manifest: dict[str, object] = {
        "schema_version": 1,
        "manifest_kind": "RELEASE",
        "representation": REPRESENTATION,
        "release": {
            "id": RELEASE_ID,
            "status": "CANDIDATE",
            "identity_kind": IDENTITY_KIND,
            "declared_ref": DECLARED_REF,
            "payload_sha256": payload_digest(selected_records(root, policy)),
        },
        "digest_algorithm": "sha256",
        "record_encoding": RECORD_ENCODING,
        "payload_policy": policy,
        "payload_policy_sha256": policy_digest(policy),
        "lineage_receipts": [
            {
                "path": "docs/release.md",
                "sha256": hashlib.sha256((root / "docs/release.md").read_bytes()).hexdigest(),
            },
            {
                "path": "docs/source-refresh.md",
                "sha256": hashlib.sha256(
                    (root / "docs/source-refresh.md").read_bytes()
                ).hexdigest(),
            },
        ],
        "claims": copy.deepcopy(CLAIMS),
        "known_unproved": copy.deepcopy(LIMITS),
    }
    _write(root / MANIFEST_PATH, (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode())
    return manifest


def _verify_tree(manifest: dict[str, object], root: Path, policy_sha: str) -> None:
    verify_compact_release_manifest(
        manifest,
        root,
        MANIFEST_PATH,
        expected_policy_sha256=policy_sha,
        expected_release_id=RELEASE_ID,
        expected_declared_ref=DECLARED_REF,
    )


class SelfImprovementOracleTests(unittest.TestCase):
    def test_accepts_planning_only_fixture_and_maintainer_routes(self) -> None:
        result = json.loads((FIXTURE / "planner-result.json").read_text(encoding="utf-8"))
        verify(FIXTURE, result, ROOT)

    def test_derived_response_matches_frozen_fixture(self) -> None:
        result = json.loads((FIXTURE / "planner-result.json").read_text(encoding="utf-8"))
        verify(FIXTURE, result, ROOT)
        self.assertEqual(expected_response(FIXTURE), result)
        self.assertEqual(result["evidence"]["runtime_claim"], "UNPROVED_NOT_RUN")
        self.assertFalse(result["authority"]["may_edit"])
        self.assertFalse(result["checkpoint_publication"]["may_publish"])

    def test_rejects_duplicate_or_boolean_like_request_authority_and_handoff_schema(self) -> None:
        """Raw request/HANDOFF evidence requires unique keys and exact primitive types."""
        cases = (
            ("duplicate authority", "request.json", None),
            ("numeric planning authority", "request.json", ("authority", "may_plan", 1)),
            ("numeric edit authority", "request.json", ("authority", "may_edit", 0)),
            ("boolean handoff schema", "HANDOFF.json", ("schema_version", True)),
        )
        for name, relative, mutation in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(FIXTURE, package)
                path = package / relative
                if mutation is None:
                    text = path.read_text(encoding="utf-8")
                    path.write_text(
                        text.replace(
                            '  "authority": {',
                            '  "authority": {"may_plan": true, "may_edit": true, '
                            '"may_commit": true, "may_publish": true, '
                            '"source_repositories": "READ_ONLY"},\n  "authority": {',
                            1,
                        ),
                        encoding="utf-8",
                    )
                else:
                    raw = json.loads(path.read_text(encoding="utf-8"))
                    if len(mutation) == 3:
                        raw[mutation[0]][mutation[1]] = mutation[2]
                    else:
                        raw[mutation[0]] = mutation[1]
                    path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
                with self.assertRaises(SelfImprovementVerificationError):
                    expected_response(package)

    def test_rejects_authority_or_topology_promotion(self) -> None:
        result = expected_response(FIXTURE)
        result["authority"]["may_commit"] = True
        result["topology"]["coordinator_role"] = "IMPLEMENTER"
        with self.assertRaises(SelfImprovementVerificationError):
            verify(FIXTURE, result)

    def test_rejects_boolean_like_planner_result_scalars(self) -> None:
        """Result equality cannot let numeric values stand in for typed status scalars."""
        cases = (
            ("schema_version", (), True, "schema_version"),
            ("may_plan", ("authority", "may_plan"), 1, "exact booleans"),
            ("may_edit", ("authority", "may_edit"), 0, "exact booleans"),
            ("may_commit", ("authority", "may_commit"), 0, "exact booleans"),
            ("may_publish", ("authority", "may_publish"), 0, "exact booleans"),
            (
                "checkpoint publication",
                ("checkpoint_publication", "may_publish"),
                0,
                "checkpoint_publication.may_publish",
            ),
            (
                "recovery authority",
                ("recovery", "authority_renewed"),
                0,
                "recovery.authority_renewed",
            ),
        )
        for name, path, value, error in cases:
            with self.subTest(name=name):
                result = expected_response(FIXTURE)
                if not path:
                    result["schema_version"] = value
                else:
                    result[path[0]][path[1]] = value
                with self.assertRaisesRegex(SelfImprovementVerificationError, error):
                    verify(FIXTURE, result)

    def test_directly_rejects_high_risk_architecture_delivery_owner_merge(self) -> None:
        result = expected_response(FIXTURE)
        result["topology"]["exploration_concern_owners"]["testing_bootstrap_release"] = result[
            "topology"
        ]["exploration_concern_owners"]["architecture_risk_privacy"]
        with self.assertRaisesRegex(
            SelfImprovementVerificationError,
            "high-risk architecture and delivery concerns must be separated",
        ):
            verify(FIXTURE, result)

    def test_directly_rejects_coordinator_as_exploration_owner(self) -> None:
        topology = copy.deepcopy(expected_response(FIXTURE)["topology"])
        previous = topology["exploration_concern_owners"]["objective_context"]
        topology["exploration_concern_owners"]["objective_context"] = topology["coordinator"]
        topology["exploration_owners"].remove(previous)
        topology["exploration_owners"].append(topology["coordinator"])
        with self.assertRaisesRegex(
            SelfImprovementVerificationError,
            "coordinator must not own exploration concerns",
        ):
            _validate_topology(topology)

    def test_scope_change_renews_only_affected_lane_and_preserves_receipt(self) -> None:
        record = json.loads(
            (SCOPE_CHANGE_FIXTURE / "scope-change.json").read_text(encoding="utf-8")
        )
        verify_scope_change_record(SCOPE_CHANGE_FIXTURE, record)

    def test_scope_change_rejects_blank_addendum_text(self) -> None:
        original = json.loads(
            (SCOPE_CHANGE_FIXTURE / "scope-change.json").read_text(encoding="utf-8")
        )
        for field in ("id", "requirement"):
            with self.subTest(field=field):
                malformed = copy.deepcopy(original)
                malformed["addendum"][field] = " "
                with self.assertRaisesRegex(
                    SelfImprovementVerificationError,
                    f"scope-change addendum {field} must be canonical non-empty text",
                ):
                    verify_scope_change_record(SCOPE_CHANGE_FIXTURE, malformed)

    def test_scope_change_rejects_renewing_unaffected_lane(self) -> None:
        record = json.loads(
            (SCOPE_CHANGE_FIXTURE / "scope-change.json").read_text(encoding="utf-8")
        )
        record["disposition"]["lane_actions"]["documentation-baseline"] = "RENEW"
        with self.assertRaisesRegex(
            SelfImprovementVerificationError,
            "unaffected lane action must be UNAFFECTED",
        ):
            verify_scope_change_record(SCOPE_CHANGE_FIXTURE, record)

    def test_scope_change_rejects_coordinator_rotation_or_author_review(self) -> None:
        original = json.loads(
            (SCOPE_CHANGE_FIXTURE / "scope-change.json").read_text(encoding="utf-8")
        )
        rotated = copy.deepcopy(original)
        rotated["disposition"]["coordinator"] = "replacement-coordinator"
        with self.assertRaisesRegex(
            SelfImprovementVerificationError,
            "scope revision must not rotate the coordinator",
        ):
            verify_scope_change_record(SCOPE_CHANGE_FIXTURE, rotated)

        self_reviewed = copy.deepcopy(original)
        self_reviewed["review"]["reviewer"] = self_reviewed["lanes"][0]["owner"]
        with self.assertRaisesRegex(
            SelfImprovementVerificationError,
            "reviewer must not be an author",
        ):
            verify_scope_change_record(SCOPE_CHANGE_FIXTURE, self_reviewed)

    def test_scope_change_rejects_identity_aliases_and_duplicate_owners(self) -> None:
        """Canonical identity keys preserve lane and review independence."""
        original = json.loads(
            (SCOPE_CHANGE_FIXTURE / "scope-change.json").read_text(encoding="utf-8")
        )
        cases = (
            (
                "padded coordinator alias",
                lambda record: record["lanes"][0].update({"owner": f" {record['coordinator']} "}),
                "canonical",
            ),
            (
                "case reviewer alias",
                lambda record: record["review"].update({"reviewer": record["coordinator"].upper()}),
                "reviewer must not be an author",
            ),
            (
                "duplicate lane owner",
                lambda record: record["lanes"][1].update({"owner": record["lanes"][0]["owner"]}),
                "lane owners must be unique identities",
            ),
            (
                "duplicate lane owner alias",
                lambda record: record["lanes"][1].update(
                    {"owner": record["lanes"][0]["owner"].upper()}
                ),
                "lane owners must be unique identities",
            ),
            (
                "duplicate author id",
                lambda record: record["review"]["author_ids"].append(
                    record["review"]["author_ids"][0]
                ),
                "review authors must cover",
            ),
            (
                "duplicate author id alias",
                lambda record: record["review"]["author_ids"].append(
                    record["review"]["author_ids"][0].upper()
                ),
                "review authors must cover",
            ),
        )
        for name, mutate, error in cases:
            with self.subTest(name=name):
                malformed = copy.deepcopy(original)
                mutate(malformed)
                with self.assertRaisesRegex(SelfImprovementVerificationError, error):
                    verify_scope_change_record(SCOPE_CHANGE_FIXTURE, malformed)

    def test_rejects_synthetic_ignorables_in_role_identities(self) -> None:
        """Every role identity reached by the helper rejects DICP/runtime-Cf controls."""
        original = json.loads(
            (SCOPE_CHANGE_FIXTURE / "scope-change.json").read_text(encoding="utf-8")
        )
        scope_cases = (
            (
                "coordinator",
                lambda record, control: record.update(
                    {"coordinator": f"maintainer{control}-coordinator"}
                ),
            ),
            (
                "lane owner",
                lambda record, control: record["lanes"][0].update(
                    {"owner": f"research{control}-owner"}
                ),
            ),
            (
                "reviewer",
                lambda record, control: record["review"].update(
                    {"reviewer": f"independent{control}-reviewer"}
                ),
            ),
            (
                "author id",
                lambda record, control: record["review"]["author_ids"].__setitem__(
                    0, f"maintainer{control}-coordinator"
                ),
            ),
        )
        for control in ("\u034f", "\ufe0f", "\U000e0100", "\u0600"):
            for name, mutate in scope_cases:
                with self.subTest(control=f"U+{ord(control):04X}", role=name):
                    malformed = copy.deepcopy(original)
                    mutate(malformed, control)
                    with self.assertRaisesRegex(
                        SelfImprovementVerificationError, "synthetic Unicode ignorables"
                    ):
                        verify_scope_change_record(SCOPE_CHANGE_FIXTURE, malformed)

        topology = copy.deepcopy(expected_response(FIXTURE)["topology"])
        topology_cases = (
            ("holder", "git_release_holder"),
            ("challenger", "challenger"),
        )
        for control in ("\u034f", "\ufe0f", "\U000e0100", "\u0600"):
            for name, field in topology_cases:
                with self.subTest(control=f"U+{ord(control):04X}", role=name):
                    malformed = copy.deepcopy(topology)
                    malformed[field] = f"{malformed[field]}{control}"
                    with self.assertRaisesRegex(
                        SelfImprovementVerificationError, "synthetic Unicode ignorables"
                    ):
                        _validate_topology(malformed)

    def test_unsafe_unicode_evidence_characters_reject_identity(self) -> None:
        """Every self-improvement identity route rejects unsafe Unicode evidence."""
        unsafe = ("\x00", "\x07", "\x7f", "\x85", "\ud800", "\ue000", "\u0378")
        original = json.loads(
            (SCOPE_CHANGE_FIXTURE / "scope-change.json").read_text(encoding="utf-8")
        )
        scope_cases = (
            (
                "coordinator",
                lambda record, character: record.update(
                    {"coordinator": f"maintainer{character}-coordinator"}
                ),
            ),
            (
                "lane owner",
                lambda record, character: record["lanes"][0].update(
                    {"owner": f"research{character}-owner"}
                ),
            ),
            (
                "reviewer",
                lambda record, character: record["review"].update(
                    {"reviewer": f"independent{character}-reviewer"}
                ),
            ),
            (
                "author id",
                lambda record, character: record["review"]["author_ids"].__setitem__(
                    0, f"maintainer{character}-coordinator"
                ),
            ),
        )
        for character in unsafe:
            for name, mutate in scope_cases:
                with self.subTest(codepoint=f"U+{ord(character):04X}", role=name):
                    malformed = copy.deepcopy(original)
                    mutate(malformed, character)
                    with self.assertRaisesRegex(
                        SelfImprovementVerificationError,
                        "unsafe Unicode evidence characters",
                    ):
                        verify_scope_change_record(SCOPE_CHANGE_FIXTURE, malformed)

        topology = copy.deepcopy(expected_response(FIXTURE)["topology"])
        for character in unsafe:
            for field in ("git_release_holder", "challenger"):
                with self.subTest(codepoint=f"U+{ord(character):04X}", role=field):
                    malformed = copy.deepcopy(topology)
                    malformed[field] = f"{malformed[field]}{character}unsafe"
                    with self.assertRaisesRegex(
                        SelfImprovementVerificationError,
                        "unsafe Unicode evidence characters",
                    ):
                        _validate_topology(malformed)

        ordinary = copy.deepcopy(original)
        ordinary["review"]["reviewer"] = "réviewer-distinct"
        verify_scope_change_record(SCOPE_CHANGE_FIXTURE, ordinary)

    def test_scope_change_stop_requires_non_coordinator_next_holder(self) -> None:
        record = json.loads(
            (SCOPE_CHANGE_FIXTURE / "scope-change.json").read_text(encoding="utf-8")
        )
        record["disposition"]["lane_actions"]["maintainability-research"] = "STOP"
        record["disposition"]["stopped_lane_remaining_outcome"] = (
            "Reassign the unproved maintainability synthesis."
        )
        record["disposition"]["next_holder"] = record["coordinator"]
        with self.assertRaisesRegex(
            SelfImprovementVerificationError,
            "stopped lane next holder must be non-coordinator text",
        ):
            verify_scope_change_record(SCOPE_CHANGE_FIXTURE, record)

    def test_scope_change_stop_fields_are_typed_and_action_consistent(self) -> None:
        original = json.loads(
            (SCOPE_CHANGE_FIXTURE / "scope-change.json").read_text(encoding="utf-8")
        )

        inconsistent = copy.deepcopy(original)
        inconsistent["disposition"]["next_holder"] = "unused-holder"
        with self.assertRaisesRegex(
            SelfImprovementVerificationError,
            "stop fields must be null when no lane is stopped",
        ):
            verify_scope_change_record(SCOPE_CHANGE_FIXTURE, inconsistent)

        for remaining, holder in (
            (None, "replacement-research-owner"),
            (" ", "replacement-research-owner"),
            ("Reassign the unproved work.", None),
            ("Reassign the unproved work.", " "),
        ):
            with self.subTest(remaining=remaining, holder=holder):
                malformed = copy.deepcopy(original)
                malformed["disposition"]["lane_actions"]["maintainability-research"] = "STOP"
                malformed["disposition"]["stopped_lane_remaining_outcome"] = remaining
                malformed["disposition"]["next_holder"] = holder
                with self.assertRaises(SelfImprovementVerificationError):
                    verify_scope_change_record(SCOPE_CHANGE_FIXTURE, malformed)

        valid = copy.deepcopy(original)
        valid["disposition"]["lane_actions"]["maintainability-research"] = "STOP"
        valid["disposition"]["stopped_lane_remaining_outcome"] = (
            "Reassign the unproved maintainability synthesis."
        )
        valid["disposition"]["next_holder"] = "replacement-research-owner"
        verify_scope_change_record(SCOPE_CHANGE_FIXTURE, valid)

    def test_rejects_stale_handoff_reported_current(self) -> None:
        result = expected_response(FIXTURE)
        result["recovery"]["freshness"] = "CURRENT"
        result["recovery"]["next_action"] = "CONTINUE"
        with self.assertRaises(SelfImprovementVerificationError):
            verify(FIXTURE, result)

    def test_rejects_symlinked_handoff_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(FIXTURE, package)
            outside = Path(directory) / "outside.txt"
            outside.write_text("outside\n", encoding="utf-8")
            source = package / "candidate-input.txt"
            source.unlink()
            source.symlink_to(outside)
            with self.assertRaises(SelfImprovementVerificationError):
                expected_response(package)

    def test_names_a_missing_package_or_release_member(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(FIXTURE, package)
            (package / "candidate-input.txt").unlink()
            with self.assertRaisesRegex(
                SelfImprovementVerificationError, "handoff source must exist"
            ):
                expected_response(package)
            root = Path(directory) / "tree"
            root.mkdir()
            (root / "present.txt").write_text("present\n", encoding="utf-8")
            policy = {"include": ["missing"], "exclude": []}
            with self.assertRaisesRegex(ReleaseManifestVerificationError, "missing must exist"):
                selected_records(root, policy)

    def test_file_exclusion_of_a_directory_keeps_its_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "tree"
            root.mkdir()
            policy = _release_tree(root)["payload_policy"]
            manifest_rule, scratch_rule = policy["exclude"]
            policy = {**policy, "exclude": [manifest_rule, {**scratch_rule, "scope": "FILE"}]}
            paths = {record["path"] for record in selected_records(root, policy)}
            self.assertIn("scratch/omitted.md", paths)

    @unittest.skipIf(os.geteuid() == 0, "root can read mode-000 paths")
    def test_release_fails_on_anything_it_cannot_inspect_even_if_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "tree"
            root.mkdir()
            manifest = _release_tree(root)
            policy = manifest["payload_policy"]
            manifest_rule, scratch_rule = policy["exclude"]
            scratch = root / "scratch"
            exclusions = {
                None: [],
                "FILE": [{**scratch_rule, "scope": "FILE"}],
                "SUBTREE": [scratch_rule],
            }
            for mode in (0, 0o444):
                for scope, rules in exclusions.items():
                    varied = {**policy, "exclude": [manifest_rule, *rules]}
                    with self.subTest(mode=oct(mode), scope=scope):
                        scratch.chmod(mode)
                        try:
                            with self.assertRaisesRegex(
                                ReleaseManifestVerificationError, "include path . cannot be listed"
                            ):
                                selected_records(root, varied)
                        finally:
                            scratch.chmod(0o755)
            payload = root / "docs" / "source-refresh.md"
            payload.chmod(0)
            stderr = io.StringIO()
            try:
                with redirect_stderr(stderr), redirect_stdout(io.StringIO()):
                    status = release_manifest_main(
                        [
                            "--repository",
                            str(root),
                            "--manifest",
                            MANIFEST_PATH,
                            "--expected-policy-sha256",
                            str(manifest["payload_policy_sha256"]),
                            "--expected-release-id",
                            RELEASE_ID,
                            "--expected-declared-ref",
                            DECLARED_REF,
                        ]
                    )
            finally:
                payload.chmod(0o644)
            self.assertEqual(status, 1)
            self.assertTrue(stderr.getvalue().startswith("FAIL:"), stderr.getvalue())

    def test_release_cli_reports_an_unusable_repository_path_as_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stderr = io.StringIO()
            with redirect_stderr(stderr), redirect_stdout(io.StringIO()):
                status = release_manifest_main(
                    [
                        "--repository",
                        str(Path(directory) / ("a" * 300)),
                        "--manifest",
                        MANIFEST_PATH,
                        "--expected-policy-sha256",
                        "0" * 64,
                        "--expected-release-id",
                        RELEASE_ID,
                        "--expected-declared-ref",
                        DECLARED_REF,
                    ]
                )
            self.assertEqual(status, 1)
            self.assertTrue(stderr.getvalue().startswith("FAIL:"), stderr.getvalue())

    def test_cli_reports_an_unusable_path_or_unreadable_member_as_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(FIXTURE, package)
            result = str(package / "planner-result.json")
            long_path = str(Path(directory) / ("a" * 300))
            source = package / "candidate-input.txt"
            cases = [
                (["--package", str(package), "--result", long_path], 0o644),
                (["--package", long_path, "--result", result], 0o644),
                (["--package", str(package), "--result", result, "--repository", long_path], 0o644),
            ]
            if os.geteuid() != 0:
                cases.append((["--package", str(package), "--result", result], 0))
            for arguments, mode in cases:
                with self.subTest(arguments=arguments, mode=mode):
                    source.chmod(mode)
                    stderr = io.StringIO()
                    try:
                        with redirect_stderr(stderr), redirect_stdout(io.StringIO()):
                            status = main(arguments)
                    finally:
                        source.chmod(0o644)
                    self.assertEqual(status, 1)
                    self.assertTrue(stderr.getvalue().startswith("FAIL:"), stderr.getvalue())

    def test_cli_reports_an_undecodable_maintainer_file_as_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            untracked = (".git", ".acceptance-work", "__pycache__", ".mypy_cache")
            shutil.copytree(ROOT, repository, ignore=shutil.ignore_patterns(*untracked))
            arguments = ["--package", str(FIXTURE), "--repository", str(repository)]
            arguments += ["--result", str(FIXTURE / "planner-result.json")]
            for name in ("README.md", "MAINTAINING.md", "WARMBOOT.md"):
                with self.subTest(name=name):
                    path = repository / name
                    original = path.read_bytes()
                    path.write_bytes(original + b"\xff\n")
                    stderr = io.StringIO()
                    try:
                        with redirect_stderr(stderr), redirect_stdout(io.StringIO()):
                            status = main(arguments)
                    finally:
                        path.write_bytes(original)
                    self.assertEqual(status, 1)
                    self.assertIn("can't decode", stderr.getvalue())

    def test_names_a_member_that_cannot_be_checked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(
                SelfImprovementVerificationError, "probe cannot be checked"
            ):
                _member(root, "a" * 300, "probe")
            policy = {"include": ["a" * 300], "exclude": []}
            with self.assertRaisesRegex(ReleaseManifestVerificationError, "cannot be checked"):
                selected_records(root, policy)
            if os.geteuid() == 0:
                return
            locked = root / "locked"
            locked.mkdir()
            (locked / "inside.txt").write_text("inside\n", encoding="utf-8")
            locked.chmod(0)
            try:
                policy = {"include": ["locked/inside.txt"], "exclude": []}
                with self.assertRaisesRegex(ReleaseManifestVerificationError, "cannot be checked"):
                    selected_records(root, policy)
            finally:
                locked.chmod(0o755)

    def test_release_example_is_compact_and_conservatively_non_release(self) -> None:
        schema = json.loads(
            (ROOT / "docs/releases/release-manifest.schema.json").read_text(encoding="utf-8")
        )
        manifest = json.loads(
            (ROOT / "docs/releases/release-manifest.example.json").read_text(encoding="utf-8")
        )
        verify_illustrative_release_manifest(manifest)
        verify_compact_illustrative_manifest(manifest)
        with self.assertRaisesRegex(
            SelfImprovementVerificationError,
            "not admissible as release-candidate proof",
        ):
            verify_release_manifest(manifest)
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), TOP_LEVEL_KEYS)
        self.assertEqual(set(schema["properties"]), TOP_LEVEL_KEYS)
        self.assertEqual(set(schema["properties"]["release"]["required"]), RELEASE_KEYS)
        self.assertEqual(schema["properties"]["representation"]["const"], REPRESENTATION)
        self.assertEqual(schema["properties"]["record_encoding"]["const"], RECORD_ENCODING)
        self.assertEqual(
            schema["properties"]["claims"]["properties"]["release_ready"]["const"], False
        )
        self.assertEqual(manifest["representation"], REPRESENTATION)
        self.assertEqual(manifest["release"]["status"], "CANDIDATE")
        self.assertEqual(manifest["claims"], CLAIMS)
        self.assertEqual(manifest["known_unproved"], LIMITS)
        self.assertEqual(schema["properties"]["known_unproved"]["minItems"], 4)
        self.assertEqual(schema["properties"]["known_unproved"]["maxItems"], 4)
        self.assertNotIn("artifact_groups", manifest)
        self.assertNotIn("resolved_commit", manifest["release"])

    def test_compact_manifest_rejects_all_25_accepted_adversarial_classes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen = Path(directory) / "frozen"
            frozen.mkdir()
            base = _release_tree(frozen)
            expected_policy = str(base["payload_policy_sha256"])

            def selected_byte(receipt: dict, tree: Path) -> None:
                (tree / "WARMBOOT.md").write_text("mutated\n", encoding="utf-8")

            def added(receipt: dict, tree: Path) -> None:
                _write(tree / "docs/new.md", b"new\n")

            def missing(receipt: dict, tree: Path) -> None:
                (tree / "templates/project-docs/README.md").unlink()

            def symlink(receipt: dict, tree: Path) -> None:
                victim = tree / "WARMBOOT.md"
                victim.unlink()
                victim.symlink_to("docs/release.md")

            def exclusion_reason(receipt: dict, tree: Path) -> None:
                receipt["payload_policy"]["exclude"][0]["reason"] = "because convenient"
                receipt["payload_policy_sha256"] = policy_digest(receipt["payload_policy"])

            def widened_exclusion(receipt: dict, tree: Path) -> None:
                receipt["payload_policy"]["exclude"].append(
                    {
                        "path": "templates",
                        "scope": "SUBTREE",
                        "reason": "Hide an eligible subtree.",
                        "bound_receipt": "docs/release.md",
                    }
                )
                receipt["payload_policy"]["exclude"] = sorted(
                    receipt["payload_policy"]["exclude"], key=lambda item: item["path"]
                )
                receipt["payload_policy_sha256"] = policy_digest(receipt["payload_policy"])

            def lineage(receipt: dict, tree: Path) -> None:
                (tree / "docs/source-refresh.md").write_text("changed\n", encoding="utf-8")

            def declared_ref(receipt: dict, tree: Path) -> None:
                receipt["release"]["declared_ref"] = "other-tag"

            def false_ready(receipt: dict, tree: Path) -> None:
                receipt["claims"]["release_ready"] = True

            def false_remote(receipt: dict, tree: Path) -> None:
                receipt["claims"]["remote_authenticity"] = "TRUSTED_REMOTE"

            def known_state(receipt: dict, tree: Path) -> None:
                receipt["known_unproved"][0]["state"] = "PROVED"

            def known_boundary(receipt: dict, tree: Path) -> None:
                receipt["known_unproved"][0]["boundary"] = "Remote authenticity was verified."

            def algorithm(receipt: dict, tree: Path) -> None:
                receipt["digest_algorithm"] = "sha1"

            def release_id(receipt: dict, tree: Path) -> None:
                receipt["release"]["id"] = "other-release"

            def schema(receipt: dict, tree: Path) -> None:
                receipt["schema_version"] = 999

            def kind(receipt: dict, tree: Path) -> None:
                receipt["manifest_kind"] = "FINAL_TRUSTED_RELEASE"

            def top_ready(receipt: dict, tree: Path) -> None:
                receipt["release_ready"] = True

            def release_remote(receipt: dict, tree: Path) -> None:
                receipt["release"]["remote_authenticity"] = "TRUSTED_REMOTE"

            def extra_trust(receipt: dict, tree: Path) -> None:
                receipt["trusted_origin"] = {"state": "VERIFIED"}

            def bool_claim(receipt: dict, tree: Path) -> None:
                receipt["claims"]["release_ready"] = 0

            def encoding(receipt: dict, tree: Path) -> None:
                receipt["record_encoding"] = "undocumented bytes"

            def unknown(receipt: dict, tree: Path) -> None:
                receipt["unchecked_metadata"] = "accepted elsewhere"

            def executable_mode(receipt: dict, tree: Path) -> None:
                (tree / "bin/warmboot").chmod(0o644)

            def float_byte(receipt: dict, tree: Path) -> None:
                receipt["per_file_entries"] = [{"path": "WARMBOOT.md", "bytes": 1.0}]

            def boolean_byte(receipt: dict, tree: Path) -> None:
                receipt["per_file_entries"] = [{"path": "WARMBOOT.md", "bytes": True}]

            cases = {
                "selected_byte_mutation": selected_byte,
                "added_eligible_file": added,
                "missing_file": missing,
                "file_type_to_symlink": symlink,
                "unjustified_exclusion": exclusion_reason,
                "widened_exclusion": widened_exclusion,
                "changed_lineage_receipt": lineage,
                "declared_tag_receipt_mismatch": declared_ref,
                "false_release_ready_claim": false_ready,
                "false_remote_authenticity_claim": false_remote,
                "known_unproved_state_changed_to_proved": known_state,
                "known_unproved_boundary_rewritten": known_boundary,
                "digest_algorithm_mismatch": algorithm,
                "release_id_mismatch": release_id,
                "schema_version_mismatch": schema,
                "manifest_kind_mismatch": kind,
                "top_level_release_ready_claim": top_ready,
                "release_scoped_remote_authenticity_claim": release_remote,
                "extra_top_level_trusted_authenticity_claim": extra_trust,
                "release_ready_boolean_type_substitution": bool_claim,
                "encoding_declaration_mismatch": encoding,
                "unknown_top_level_field": unknown,
                "executable_mode_mutation": executable_mode,
                "json_roundtripped_float_byte_count": float_byte,
                "json_roundtripped_boolean_byte_count": boolean_byte,
            }
            self.assertEqual(len(cases), 25)
            for name, mutate in cases.items():
                with self.subTest(name=name), tempfile.TemporaryDirectory() as case_dir:
                    tree = Path(case_dir) / "tree"
                    shutil.copytree(frozen, tree, symlinks=True)
                    receipt = json.loads(json.dumps(base))
                    mutate(receipt, tree)
                    with self.assertRaises(ReleaseManifestVerificationError):
                        _verify_tree(receipt, tree, expected_policy)

    def test_compact_manifest_rejects_traversal_self_inclusion_and_special_type(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "tree"
            root.mkdir()
            manifest = _release_tree(root)
            policy_sha = str(manifest["payload_policy_sha256"])

            traversal = copy.deepcopy(manifest)
            traversal["payload_policy"]["include"] = ["../outside"]
            with self.assertRaisesRegex(ReleaseManifestVerificationError, "canonical"):
                verify_compact_release_manifest(traversal)

            invalid_domain = copy.deepcopy(manifest)
            invalid_domain["release"]["id"] = " "
            invalid_domain["release"]["declared_ref"] = "refs/heads/main"
            with self.assertRaisesRegex(ReleaseManifestVerificationError, "release id"):
                verify_compact_release_manifest(invalid_domain)

            self_including = copy.deepcopy(manifest)
            self_including["payload_policy"]["exclude"] = [
                item
                for item in self_including["payload_policy"]["exclude"]
                if item["path"] != MANIFEST_PATH
            ]
            self_including["payload_policy_sha256"] = policy_digest(
                self_including["payload_policy"]
            )
            with self.assertRaisesRegex(
                ReleaseManifestVerificationError, "exact FILE policy exclusion"
            ):
                verify_compact_release_manifest(
                    self_including,
                    root,
                    MANIFEST_PATH,
                    expected_policy_sha256=self_including["payload_policy_sha256"],
                    expected_release_id=RELEASE_ID,
                    expected_declared_ref=DECLARED_REF,
                )

            if hasattr(os, "mkfifo"):
                os.mkfifo(root / "unexpected.pipe")
                with self.assertRaisesRegex(ReleaseManifestVerificationError, "not a regular file"):
                    _verify_tree(manifest, root, policy_sha)

    def test_declared_tag_domain_is_conservative_and_component_safe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "tree"
            root.mkdir()
            base = _release_tree(root)
            schema = json.loads(
                (ROOT / "docs/releases/release-manifest.schema.json").read_text(encoding="utf-8")
            )
            schema_tag_pattern = schema["$defs"]["short_tag"]["pattern"]
            for valid in (
                "v1.0.0",
                "agent-warmboot-v1",
                "release/2026-08-01",
                "feature_name-2",
            ):
                with self.subTest(valid=valid):
                    self.assertRegex(valid, schema_tag_pattern)
                    manifest = copy.deepcopy(base)
                    manifest["release"]["declared_ref"] = valid
                    verify_compact_release_manifest(manifest)

            invalid = (
                "",
                ".",
                "..",
                "@",
                "-release",
                "/release",
                "release/",
                "refs/tags/release",
                ".hidden",
                "release/.hidden",
                "release/.",
                "release/..",
                "release//candidate",
                "release/../candidate",
                "release.lock",
                "release.lock/candidate",
                "release/candidate.lock",
                "release./candidate",
                "release/candidate.",
                "release@{candidate",
                "release candidate",
                "release~candidate",
                "release^candidate",
                "release:candidate",
                "release?candidate",
                "release*candidate",
                "release[candidate",
                "release\\candidate",
                "caf\u00e9",
                "cafe\u0301",
            )
            for candidate in invalid:
                with self.subTest(invalid=candidate):
                    self.assertNotRegex(candidate, schema_tag_pattern)
                    manifest = copy.deepcopy(base)
                    manifest["release"]["declared_ref"] = candidate
                    with self.assertRaisesRegex(
                        ReleaseManifestVerificationError,
                        "declared annotated tag|invalid domain",
                    ):
                        verify_compact_release_manifest(manifest)

    def test_known_unproved_is_exact_semantic_not_phrase_matching(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "tree"
            root.mkdir()
            base = _release_tree(root)
            variants: dict[str, list[dict[str, str]]] = {
                "contradictory_authenticity_claim": copy.deepcopy(LIMITS),
                "proved_state": copy.deepcopy(LIMITS),
                "renamed_domain": copy.deepcopy(LIMITS),
                "missing_domain": copy.deepcopy(LIMITS[:-1]),
                "duplicate_domain": copy.deepcopy(LIMITS + [LIMITS[-1]]),
                "reordered_domains": list(reversed(copy.deepcopy(LIMITS))),
            }
            variants["contradictory_authenticity_claim"][-1]["boundary"] = (
                "Remote authenticity was verified."
            )
            variants["proved_state"][0]["state"] = "PROVED"
            variants["renamed_domain"][0]["domain"] = "TAG_AUTHENTICITY"
            for name, limits in variants.items():
                with self.subTest(name=name):
                    manifest = copy.deepcopy(base)
                    manifest["known_unproved"] = limits
                    with self.assertRaisesRegex(
                        ReleaseManifestVerificationError,
                        "exactly retain the four conservative authenticity boundaries",
                    ):
                        verify_compact_release_manifest(manifest)

    def test_illustrative_manifest_never_enters_release_or_cli_proof(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "tree"
            root.mkdir()
            manifest = _release_tree(root)
            manifest["manifest_kind"] = "ILLUSTRATIVE_NON_RELEASE"
            _write(
                root / MANIFEST_PATH,
                (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
            )
            verify_compact_illustrative_manifest(manifest)
            with self.assertRaisesRegex(
                ReleaseManifestVerificationError,
                "not admissible as release-candidate proof",
            ):
                verify_compact_release_manifest(manifest)
            with self.assertRaisesRegex(
                ReleaseManifestVerificationError,
                "not admissible as release-candidate proof",
            ):
                _verify_tree(manifest, root, str(manifest["payload_policy_sha256"]))

            error = io.StringIO()
            with redirect_stderr(error):
                result = release_manifest_main(
                    [
                        "--repository",
                        str(root),
                        "--manifest",
                        MANIFEST_PATH,
                        "--expected-policy-sha256",
                        str(manifest["payload_policy_sha256"]),
                        "--expected-release-id",
                        RELEASE_ID,
                        "--expected-declared-ref",
                        DECLARED_REF,
                    ]
                )
            self.assertEqual(result, 1)
            self.assertIn("not admissible as release-candidate proof", error.getvalue())

    def test_raw_manifest_loaders_reject_unsafe_duplicate_claims_before_safe_values(self) -> None:
        """Neither raw manifest reader may silently keep the later conservative claims."""
        unsafe_claims = (
            '  "claims": {"release_ready": true, "tag_verified": true, '
            '"remote_authenticity": "PROVED"},\n  "claims": {'
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "tree"
            root.mkdir()
            manifest = _release_tree(root)
            manifest_path = root / MANIFEST_PATH
            manifest_path.write_text(
                manifest_path.read_text(encoding="utf-8").replace(
                    '  "claims": {', unsafe_claims, 1
                ),
                encoding="utf-8",
            )
            error = io.StringIO()
            with redirect_stderr(error):
                result = release_manifest_main(
                    [
                        "--repository",
                        str(root),
                        "--manifest",
                        MANIFEST_PATH,
                        "--expected-policy-sha256",
                        str(manifest["payload_policy_sha256"]),
                        "--expected-release-id",
                        RELEASE_ID,
                        "--expected-declared-ref",
                        DECLARED_REF,
                    ]
                )
            self.assertEqual(result, 1)
            self.assertIn("duplicate JSON object key: claims", error.getvalue())

            illustrative = Path(directory) / "illustrative.json"
            illustrative.write_text(
                (ROOT / "docs/releases/release-manifest.example.json")
                .read_text(encoding="utf-8")
                .replace('  "claims": {', unsafe_claims, 1),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ReleaseManifestVerificationError, "duplicate JSON object key: claims"
            ):
                verify_compact_illustrative_manifest(load_manifest(illustrative))

    def test_compact_manifest_reproduces_from_second_clean_copy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "tree"
            second = Path(directory) / "second"
            root.mkdir()
            manifest = _release_tree(root)
            shutil.copytree(root, second, symlinks=True)
            policy_sha = str(manifest["payload_policy_sha256"])
            _verify_tree(manifest, root, policy_sha)
            _verify_tree(manifest, second, policy_sha)
            self.assertEqual(
                payload_digest(selected_records(root, manifest["payload_policy"])),
                payload_digest(selected_records(second, manifest["payload_policy"])),
            )

    def test_cli_proves_local_completeness_but_not_tag_remote_or_signature(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "tree"
            root.mkdir()
            manifest = _release_tree(root)
            output = io.StringIO()
            with redirect_stdout(output):
                result = release_manifest_main(
                    [
                        "--repository",
                        str(root),
                        "--manifest",
                        MANIFEST_PATH,
                        "--expected-policy-sha256",
                        str(manifest["payload_policy_sha256"]),
                        "--expected-release-id",
                        RELEASE_ID,
                        "--expected-declared-ref",
                        DECLARED_REF,
                    ]
                )
            self.assertEqual(result, 0)
            receipt = json.loads(output.getvalue())
            self.assertEqual(receipt["completeness"], "VERIFIED_AGAINST_EXPANDED_FROZEN_POLICY")
            self.assertFalse(receipt["release_ready"])
            self.assertFalse(receipt["tag_verified"])
            self.assertEqual(receipt["remote_authenticity"], "UNPROVED_LOCAL_ONLY")
            self.assertEqual(receipt["signature_authenticity"], "UNPROVED_NOT_EVALUATED")

    def test_readme_prompts_and_root_self_adoption_are_routed(self) -> None:
        verify_maintainer_repository(ROOT)
        standards = (ROOT / "docs/engineering-standards.md").read_text(encoding="utf-8")
        testing = (ROOT / "docs/testing.md").read_text(encoding="utf-8")
        invariants = (ROOT / "docs/invariants.md").read_text(encoding="utf-8")
        disposition = (ROOT / "docs/adoption-disposition.md").read_text(encoding="utf-8")
        self.assertIn("ADOPT`, `MERGE INTO EXISTING`, `CITE ONLY` or `OMIT", standards)
        self.assertIn("Deterministic closing set", testing)
        self.assertIn("WB-I01", invariants)
        self.assertIn("Warmboot self-adoption disposition", disposition)


if __name__ == "__main__":
    unittest.main()
