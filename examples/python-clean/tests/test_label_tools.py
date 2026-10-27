"""Check whitespace normalization in the small standard-library teaching example."""

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from label_tools import normalize_label  # noqa: E402


class NormalizeLabelTests(unittest.TestCase):
    def test_collapses_whitespace_and_normalizes_case(self) -> None:
        self.assertEqual(normalize_label("  Warm   BOOT  "), "warm boot")


if __name__ == "__main__":
    unittest.main()
