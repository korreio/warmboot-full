"""Exercise prepare in external temporary workspaces and isolated fake repositories."""

import hashlib
import io
import os
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from acceptance.prepare import (
    ACCEPTANCE_WORK_ROOT,
    ROOT,
    PrepareError,
    _safe_workspace,
    _snapshot,
    main,
    prepare,
)

FAKE_WARMBOOT = """\
import sys
from pathlib import Path

command, target, *flags = sys.argv[1:]
root = Path(target)
if command == "init" and "--apply" not in flags:
    print("preview")
elif command == "init" and "--apply" in flags:
    (root / ".agent-warmboot" / "routes").mkdir(parents=True)
    (root / ".agent-warmboot" / "core.md").write_text("core\\n", encoding="utf-8")
    (root / ".agent-warmboot" / "routes" / "default.md").write_text("route\\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("loader\\n", encoding="utf-8")
    (root / "CLAUDE.md").write_text("loader\\n", encoding="utf-8")
elif command == "check":
    required = [root / ".agent-warmboot" / "core.md", root / "AGENTS.md", root / "CLAUDE.md"]
    if not all(path.is_file() for path in required):
        raise SystemExit(1)
    print("check pass")
else:
    raise SystemExit(2)
"""


class PrepareTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repository = Path(__file__).resolve().parents[2]
        self.repository_before = self._repository_snapshot()
        self.addCleanup(self.assert_repository_unchanged)
        self.cli = self.root / "fake-warmboot"
        self.cli.write_text(textwrap.dedent(FAKE_WARMBOOT), encoding="utf-8")
        os.chmod(self.cli, 0o755)

    def _repository_snapshot(self) -> dict[str, tuple[str, str]]:
        snapshot: dict[str, tuple[str, str]] = {}
        for current, directories, files in os.walk(self.repository):
            directories[:] = [name for name in directories if name != ".git"]
            root = Path(current)
            for name in directories:
                path = root / name
                snapshot[path.relative_to(self.repository).as_posix()] = ("directory", "")
            for name in files:
                path = root / name
                relative = path.relative_to(self.repository).as_posix()
                if path.is_symlink():
                    snapshot[relative] = ("symlink", os.readlink(path))
                else:
                    snapshot[relative] = (
                        "file",
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                    )
        return snapshot

    def assert_repository_unchanged(self) -> None:
        self.assertEqual(self._repository_snapshot(), self.repository_before)

    def test_snapshot_sees_every_kind_of_change(self) -> None:
        changes = {
            "created directory": lambda tree: (tree / "new").mkdir(),
            "removed directory": lambda tree: (tree / "empty").rmdir(),
            "dangling symlink": lambda tree: (tree / "link").symlink_to("missing"),
            "file mode": lambda tree: (tree / "file.txt").chmod(0o755),
            "root mode": lambda tree: tree.chmod(0o700),
        }
        if hasattr(os, "mkfifo"):
            changes["named pipe"] = lambda tree: os.mkfifo(tree / "pipe")
        for name, change in changes.items():
            with self.subTest(change=name):
                tree = self.root / name.replace(" ", "-")
                (tree / "empty").mkdir(parents=True)
                (tree / "file.txt").write_text("file\n", encoding="utf-8")
                (tree / "file.txt").chmod(0o644)
                tree.chmod(0o755)
                before = _snapshot(tree)
                change(tree)
                self.assertNotEqual(_snapshot(tree), before)

    def test_snapshot_records_a_linked_root_without_following_it(self) -> None:
        target = self.root / "target"
        (target / "deep").mkdir(parents=True)
        (target / "deep" / "secret.txt").write_text("secret\n", encoding="utf-8")
        workspace = self.root / "workspace"
        workspace.mkdir()
        before = _snapshot(workspace)
        workspace.rmdir()
        workspace.symlink_to(target)
        after = _snapshot(workspace)
        self.assertEqual(sorted(after), ["."])
        self.assertNotEqual(after, before)

    def test_unknown_home_directory_is_named_as_unresolvable(self) -> None:
        with self.assertRaisesRegex(PrepareError, "workspace cannot be resolved"):
            _safe_workspace(Path("~no-such-warmboot-user/workspace"))

    @unittest.skipIf(os.geteuid() == 0, "root can read mode-000 paths")
    def test_snapshot_fails_on_anything_it_cannot_read(self) -> None:
        tree = self.root / "tree"
        locked = tree / "locked"
        locked.mkdir(parents=True)
        (locked / "file.txt").write_text("file\n", encoding="utf-8")
        for target, mode, restore in (
            (locked, 0, 0o755),
            (locked, 0o444, 0o755),
            (locked / "file.txt", 0, 0o644),
        ):
            with self.subTest(target=target.name, mode=oct(mode)):
                target.chmod(mode)
                try:
                    with self.assertRaisesRegex(PrepareError, "workspace cannot be read"):
                        _snapshot(tree)
                finally:
                    target.chmod(restore)

    def test_before_preview_that_creates_a_directory_fails(self) -> None:
        cli = self.root / "mutating-warmboot"
        source = textwrap.dedent(FAKE_WARMBOOT)
        source = source.replace('    print("preview")', '    (root / "staging").mkdir()')
        cli.write_text(source, encoding="utf-8")
        with self.assertRaisesRegex(PrepareError, "preview mutated"):
            prepare("before", self.root / "before", cli)

    def test_symlink_loop_workspace_or_cli_fails_as_a_line(self) -> None:
        loop = self.root / "loop"
        loop.symlink_to("loop")
        for arguments in (
            ["before", "--workspace", str(loop)],
            ["before", "--workspace", str(self.root / "ws"), "--warmboot", str(loop)],
        ):
            with self.subTest(arguments=arguments):
                stderr = io.StringIO()
                with redirect_stderr(stderr), redirect_stdout(io.StringIO()):
                    status = main(arguments)
                self.assertEqual(status, 1)
                self.assertTrue(stderr.getvalue().startswith("FAIL:"), stderr.getvalue())

    def test_before_preview_is_non_mutating(self) -> None:
        result = prepare("before", self.root / "before", self.cli)
        self.assertTrue(result["preview_non_mutating"])
        self.assertFalse((self.root / "before" / ".agent-warmboot").exists())
        self.assert_repository_unchanged()

    def test_after_applies_and_checks(self) -> None:
        result = prepare("after", self.root / "after", self.cli)
        self.assertEqual(result["installed_state_check"], "PASS")
        self.assertTrue((self.root / "after" / ".agent-warmboot" / "core.md").is_file())
        self.assert_repository_unchanged()

    def test_system_temp_child_is_allowed_without_repository_residue(self) -> None:
        workspace = self.root / "prepare-self-test"
        result = prepare("before", workspace, self.cli)
        self.assertTrue(result["preview_non_mutating"])
        self.assertTrue((workspace / "TASK.md").is_file())
        self.assert_repository_unchanged()

    def test_arbitrary_deep_non_temp_path_is_rejected(self) -> None:
        # Pin the effective system temp root to a controlled location so this verdict
        # never depends on where the checkout lives: a clean verifier checkout may itself
        # sit beneath the system temporary directory. Patching ``SYSTEM_TEMP_ROOT`` exactly
        # as ``_safe_workspace`` reads it, and building the deep target outside that
        # controlled root, ROOT and the scratch root, keeps "an arbitrary deep non-temp
        # path is rejected" hermetic (WB-039).
        controlled_temp = (self.root / "controlled-temp-root").resolve()
        controlled_temp.mkdir()
        unsafe = (
            self.root
            / "outside-every-allowed-root"
            / "agent-warmboot-unsafe"
            / "deep"
            / "workspace"
        )
        with mock.patch("acceptance.prepare.SYSTEM_TEMP_ROOT", controlled_temp):
            with self.assertRaises(PrepareError):
                prepare("before", unsafe, self.cli)
        # Even under gettempdir(), a workspace that CONTAINS the repository root is
        # refused: the repository-root guard does not depend on temp membership.
        nest = self.root / "nest"
        simulated_root = nest / "checkout"
        simulated_root.mkdir(parents=True)
        sentinel = simulated_root / ".git-canary"
        sentinel.write_text("keep\n", encoding="utf-8")
        with mock.patch("acceptance.prepare.ROOT", simulated_root):
            with self.assertRaises(PrepareError):
                prepare("before", nest, self.cli)
        self.assertTrue(sentinel.is_file())

    def test_refuses_repository_root(self) -> None:
        with self.assertRaises(PrepareError):
            prepare("before", Path(__file__).resolve().parents[2], self.cli)
        # A checkout whose ROOT sits UNDER gettempdir() must still be refused, so the
        # guard cannot silently pass by the real checkout's non-temp location.
        simulated_root = self.root / "checkout"
        simulated_root.mkdir()
        sentinel = simulated_root / ".git-canary"
        sentinel.write_text("keep\n", encoding="utf-8")
        with mock.patch("acceptance.prepare.ROOT", simulated_root):
            with self.assertRaises(PrepareError):
                prepare("before", simulated_root, self.cli)
        self.assertTrue(sentinel.is_file())

    def test_refuses_allowed_roots_themselves(self) -> None:
        roots = (
            Path(__file__).resolve().parents[2] / ".acceptance-work",
            Path(tempfile.gettempdir()),
        )
        for root in roots:
            with self.subTest(root=root), self.assertRaises(PrepareError):
                prepare("before", root, self.cli)

    def test_scratch_root_descendant_is_exempt_from_repository_overlap(self) -> None:
        # The dedicated, gitignored ``.acceptance-work`` scratch root is a deliberate
        # allowed workspace root even though it lives under ROOT, so its strict
        # descendants (the bare-CLI default target) are accepted. ROOT itself and every
        # other ROOT descendant are refused, so the guard is neither over- nor
        # under-broad (WB-039).
        with self.assertRaises(PrepareError):
            _safe_workspace(ROOT)
        with self.assertRaises(PrepareError):
            _safe_workspace(ROOT / "acceptance" / "fixtures")
        accepted = _safe_workspace(ACCEPTANCE_WORK_ROOT / "before")
        self.assertEqual(accepted, (ACCEPTANCE_WORK_ROOT / "before").resolve())
        self.assertIn(ACCEPTANCE_WORK_ROOT, accepted.parents)

    def test_scratch_alias_cannot_authorize_repository_deletion(self) -> None:
        """Exercise the overlap guard with aliases; deletion is always mocked.

        Each target names a child of a scratch symlink and resolves to an ancestor of
        the repository, the repository itself or a repository descendant. The guard
        resolves the target at call time and exempts repository descendants only below
        a real scratch directory, so every case is refused before deletion. ROOT is
        patched to an isolated fake checkout; concurrent filesystem reparenting is not
        covered.
        """
        repository = (self.root / "nest" / "checkout").resolve()
        source = repository / "source"
        (source / "nested").mkdir(parents=True)
        scratch = repository / ".acceptance-work"
        cases = (
            (self.root.resolve(), "nest"),
            (repository.parent, "checkout"),
            (repository, "source"),
            (source, "nested"),
        )
        for destination, child in cases:
            with self.subTest(destination=destination, child=child):
                scratch.symlink_to(destination, target_is_directory=True)
                try:
                    with (
                        mock.patch("acceptance.prepare.ROOT", repository),
                        mock.patch("acceptance.prepare.shutil.rmtree") as delete,
                        mock.patch("acceptance.prepare.shutil.copytree") as copy,
                        mock.patch("acceptance.prepare._snapshot", return_value={}),
                        mock.patch("acceptance.prepare._run"),
                    ):
                        try:
                            with self.assertRaises(PrepareError):
                                prepare("before", scratch / child, self.cli)
                        finally:
                            delete.assert_not_called()
                            copy.assert_not_called()
                finally:
                    scratch.unlink()

    def test_call_time_scratch_requires_absent_or_real_directory(self) -> None:
        repository = (self.root / "isolated-checkout").resolve()
        repository.mkdir()
        scratch = repository / ".acceptance-work"
        with mock.patch("acceptance.prepare.ROOT", repository):
            for present in (False, True):
                with self.subTest(present=present):
                    if present:
                        scratch.mkdir()
                    self.assertEqual(_safe_workspace(scratch / "before"), scratch / "before")
                    with self.assertRaises(PrepareError):
                        _safe_workspace(scratch)
            # A symlink below a real scratch root must also resolve outside the
            # exception before any deletion can be considered.
            source = repository / "source"
            source.mkdir()
            (scratch / "escape").symlink_to(source, target_is_directory=True)
            with self.assertRaises(PrepareError):
                _safe_workspace(scratch / "escape" / "child")
            (scratch / "escape").unlink()
            scratch.rmdir()
            for kind in ("file", "fifo", "dangling-symlink"):
                with self.subTest(kind=kind):
                    if kind == "file":
                        scratch.write_text("not a directory\n", encoding="utf-8")
                    elif kind == "fifo":
                        os.mkfifo(scratch)
                    else:
                        scratch.symlink_to(repository / "missing")
                    try:
                        with self.assertRaises(PrepareError):
                            _safe_workspace(scratch / "before")
                    finally:
                        scratch.unlink()
            external = self.root / "external-workspace"
            self.assertEqual(_safe_workspace(external), external.resolve())


if __name__ == "__main__":
    unittest.main()
