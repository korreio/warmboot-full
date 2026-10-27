"""Verify normalization invariants and invalid input behavior for the pure core."""

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from label_normalizer import normalize_label  # noqa: E402


class NormalizeLabelTests(unittest.TestCase):
    def test_collapses_whitespace_and_casefolds(self) -> None:
        self.assertEqual(normalize_label("  Warm\t  BOOT  "), "warm boot")

    def test_normalizes_unicode_compatibility_forms(self) -> None:
        self.assertEqual(normalize_label("Ｆｕｌｌｗｉｄｔｈ"), "fullwidth")

    def test_uses_unicode_case_folding(self) -> None:
        self.assertEqual(normalize_label("Straße"), "strasse")

    def test_empty_and_whitespace_only_values_share_the_empty_key(self) -> None:
        self.assertEqual(normalize_label(" \n\t "), "")

    def test_rejects_non_string_input_at_the_public_boundary(self) -> None:
        with self.assertRaisesRegex(TypeError, "^value must be str$"):
            normalize_label(42)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
