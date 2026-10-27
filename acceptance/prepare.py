"""Reset deterministic before/after fixtures and exercise bin/warmboot."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).resolve().parent / "fixtures" / "baseline"
DEFAULT_WARMBOOT = ROOT / "bin" / "warmboot"
ACCEPTANCE_WORK_ROOT = ROOT / ".acceptance-work"
SYSTEM_TEMP_ROOT = Path(tempfile.gettempdir()).resolve()


class PrepareError(RuntimeError):
    """Raised for an unsafe target or failed warmboot command."""


def _safe_workspace(path: Path) -> Path:
    try:
        resolved = path.expanduser().resolve()
    # A symlink loop on Python 3.11 and 3.12, or an unknown `~user`, raises RuntimeError.
    except RuntimeError as exc:
        raise PrepareError(f"workspace cannot be resolved: {path}: {exc}") from exc
    repository = ROOT.resolve()
    scratch_root = repository / ".acceptance-work"
    # Equality and ancestor refusal cannot depend on scratch membership: a resolved
    # scratch alias must never authorize deletion of the source checkout (WB-048).
    if resolved == repository or resolved in repository.parents:
        raise PrepareError(f"refusing workspace overlapping the repository root: {resolved}")
    # Keep the absent-directory CLI default usable, but only a literal real scratch
    # directory may exempt a source descendant. Resolve the target, not this root,
    # so symlinks within scratch cannot smuggle source paths into the exception.
    try:
        scratch_eligible = stat.S_ISDIR(scratch_root.lstat().st_mode)
    except FileNotFoundError:
        scratch_eligible = True
    within_scratch_root = scratch_eligible and scratch_root in resolved.parents
    if repository in resolved.parents and not within_scratch_root:
        raise PrepareError(
            f"refusing workspace overlapping the repository root: {resolved}; a "
            f"workspace must not equal, contain, or be contained by {repository} "
            f"(except a strict descendant of the dedicated {scratch_root} "
            f"scratch root)"
        )
    for allowed_root in (scratch_root, SYSTEM_TEMP_ROOT):
        try:
            relative = resolved.relative_to(allowed_root)
        except ValueError:
            continue
        if relative.parts:
            return resolved
    raise PrepareError(
        f"refusing unsafe workspace: {resolved}; target must be a strict descendant "
        f"of {scratch_root} or {SYSTEM_TEMP_ROOT}"
    )


def _node(path: Path, mode: int) -> str:
    """Describe one node by type, permission bits and, for a file or link, its content."""
    if stat.S_ISREG(mode):
        content = hashlib.sha256(path.read_bytes()).hexdigest()
    elif stat.S_ISLNK(mode):
        content = str(path.readlink())
    else:
        content = ""
    return f"{stat.S_IFMT(mode):o} {stat.S_IMODE(mode):o} {content}"


def _snapshot(root: Path) -> dict[str, str]:
    """Record every node from root down, failing on any it cannot list, inspect or read."""
    try:
        root_mode = root.lstat().st_mode
        snapshot = {".": _node(root, root_mode)}
        # A root that is no longer a real directory is recorded, never followed.
        pending = [root] if stat.S_ISDIR(root_mode) else []
        while pending:
            for entry in pending.pop().iterdir():
                mode = entry.lstat().st_mode
                snapshot[entry.relative_to(root).as_posix()] = _node(entry, mode)
                if stat.S_ISDIR(mode):
                    pending.append(entry)
    except OSError as exc:
        raise PrepareError(f"workspace cannot be read: {exc}") from exc
    return snapshot


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise PrepareError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def prepare(mode: str, workspace: Path, warmboot: Path) -> dict[str, object]:
    """Copy the fixture into a fresh workspace, run the helper for the mode and return a receipt."""
    workspace = _safe_workspace(workspace)
    try:
        warmboot = warmboot.expanduser().resolve()
    # A symlink loop on Python 3.11 and 3.12, or an unknown `~user`, raises RuntimeError.
    except RuntimeError as exc:
        raise PrepareError(f"warmboot CLI cannot be resolved: {warmboot}: {exc}") from exc
    if not warmboot.is_file():
        raise PrepareError(f"warmboot CLI not found: {warmboot}")

    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        BASELINE,
        workspace,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    baseline = _snapshot(workspace)

    if mode == "before":
        preview = _run([sys.executable, "-B", str(warmboot), "init", str(workspace)])
        if _snapshot(workspace) != baseline:
            raise PrepareError("preview mutated the before fixture")
        return {
            "mode": mode,
            "status": "PASS",
            "workspace": str(workspace),
            "preview_non_mutating": True,
            "preview_stdout": preview.stdout.strip(),
        }

    _run([sys.executable, "-B", str(warmboot), "init", str(workspace), "--apply"])
    check = _run([sys.executable, "-B", str(warmboot), "check", str(workspace)])
    return {
        "mode": mode,
        "status": "PASS",
        "workspace": str(workspace),
        "installed_state_check": "PASS",
        "check_stdout": check.stdout.strip(),
    }


def main(argv: list[str] | None = None) -> int:
    """Run the command line and return the exit code."""
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("before", "after"))
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--warmboot", type=Path, default=DEFAULT_WARMBOOT)
    args = parser.parse_args(argv)
    workspace = args.workspace or ROOT / ".acceptance-work" / args.mode

    try:
        result = prepare(args.mode, workspace, args.warmboot)
    except (OSError, PrepareError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
