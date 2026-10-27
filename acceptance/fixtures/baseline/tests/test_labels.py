"""Check the synthetic target label formatter without creating runtime artifacts."""

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from labels import normalize_label  # noqa: E402


class NormalizeLabelTests(unittest.TestCase):
    def test_collapses_whitespace_and_normalizes_case(self) -> None:
        self.assertEqual(normalize_label("  Fresh   AGENT  "), "fresh agent")


if __name__ == "__main__":
    unittest.main()
