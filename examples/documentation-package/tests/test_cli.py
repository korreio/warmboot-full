"""Exercise the documentation example CLI and its no-bytecode child boundary."""

import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LabelNormalizerCliTests(unittest.TestCase):
    def bytecode_snapshot(self) -> dict[str, bytes | None]:
        """Map each bytecode cache path to its bytes (None for a cache directory).

        The runner that discovered these tests may already have written caches, so the
        child's boundary is proved by comparing before and after, not by absence.
        """
        return {
            path.relative_to(ROOT).as_posix(): (
                path.read_bytes() if path.is_file() else None
            )
            for path in ROOT.rglob("*")
            if path.name == "__pycache__" or path.suffix == ".pyc"
        }

    def test_prints_one_comparison_key_per_argument(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        # Only the child's -B flag may suppress its bytecode writes here.
        env.pop("PYTHONDONTWRITEBYTECODE", None)
        before = self.bytecode_snapshot()
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "label_normalizer",
                " Warm  BOOT ",
                "Straße",
            ],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "warm boot\nstrasse\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(self.bytecode_snapshot(), before)


if __name__ == "__main__":
    unittest.main()
