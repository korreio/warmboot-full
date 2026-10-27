"""Direct regressions for the shared strict JSON decoder and every loader that uses it.

Every acceptance loader catches ``json.JSONDecodeError`` and reports it as its own
verification error. These pin that the decoder's depth and integer-size limits arrive
as that error, so no loader turns a malformed document into a traceback.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from acceptance import (
    capability_oracle,
    kickoff_oracle,
    oracle,
    release_manifest,
    self_improvement_oracle,
    source_comprehension_oracle,
    upgrade_oracle,
)
from acceptance.strict_json import DuplicateJsonKeyError, loads


def limit_documents() -> dict[str, str]:
    documents = {"deep-nesting": "[" * 200000 + "]" * 200000}
    limit = getattr(sys, "get_int_max_str_digits", lambda: 0)()
    if limit:
        documents["long-integer"] = "[" + "1" * (limit + 1) + "]"
    return documents


class StrictJsonLimitTests(unittest.TestCase):
    def test_decoder_limits_raise_json_decode_error(self) -> None:
        for name, document in limit_documents().items():
            for raw in (document, document.encode("utf-8")):
                with self.subTest(document=name, kind=type(raw).__name__):
                    with self.assertRaises(json.JSONDecodeError):
                        loads(raw)
        with self.assertRaises(DuplicateJsonKeyError):
            loads('{"key": 1, "key": 2}')
        self.assertEqual(loads('{"key": [1, 2]}'), {"key": [1, 2]})

    def test_every_loader_reports_decoder_limits_as_its_own_error(self) -> None:
        loaders = (
            (
                lambda path: capability_oracle._load_json(path, "selection"),
                capability_oracle.CapabilityVerificationError,
            ),
            (lambda path: oracle._load_json(str(path)), oracle.VerificationError),
            (kickoff_oracle._load, kickoff_oracle.KickoffVerificationError),
            (
                lambda path: source_comprehension_oracle.verify_case(path.parent),
                source_comprehension_oracle.SourceComprehensionError,
            ),
            (release_manifest.load_manifest, release_manifest.ReleaseManifestVerificationError),
            (
                lambda path: self_improvement_oracle._read_json(path, "result"),
                self_improvement_oracle.SelfImprovementVerificationError,
            ),
            (
                lambda path: upgrade_oracle._read_json(path, "result"),
                upgrade_oracle.UpgradeVerificationError,
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review-case.json"
            for name, document in limit_documents().items():
                path.write_text(document, encoding="utf-8")
                for load, error in loaders:
                    with self.subTest(document=name, error=error.__name__):
                        # Each error subclasses ValueError, so a raw decoder ValueError fails here.
                        with self.assertRaises(error):
                            load(path)


if __name__ == "__main__":
    unittest.main()
