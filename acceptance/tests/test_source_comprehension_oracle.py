"""Regression tests for the deliberately fixture-specific source-comprehension oracle."""

from __future__ import annotations

import contextlib
import io
import json
import multiprocessing
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from acceptance.source_comprehension_oracle import (
    SourceComprehensionError,
    _java_identifier_start,
    _relative_file,
    main,
    verify_case,
)
from acceptance.unicode_policy import NON_MARKDOWN_LINE_SEPARATORS


def _match_declaration_gap(gap: str) -> None:
    """Run the declaration-gap match in a child process so a hang can be bounded."""
    from acceptance.source_comprehension_oracle import JAVA_DECLARATION_GAP_RE

    JAVA_DECLARATION_GAP_RE.fullmatch(gap)


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "acceptance" / "fixtures" / "source-comprehension"
SECOND_DECLARATION_VARIANTS = (
    ("class", "class Extra {}"),
    ("interface", "interface Extra {}"),
    ("enum", "enum Extra { VALUE }"),
    ("record", "record Extra() {}"),
    ("annotation interface", "@interface Extra {}"),
    ("nested class", None),
    ("Unicode class", "class Éxtra {}"),
    ("Unicode interface", "interface Éxtra {}"),
    ("Unicode enum", "enum Éxtra { VALUE }"),
    ("Unicode record", "record Éxtra() {}"),
    ("Unicode annotation interface", "@interface Éxtra {}"),
    ("currency-symbol class", "class €xtra {}"),
    ("dollar class", "class $Extra {}"),
    ("underscore class", "class _Extra {}"),
    ("supplementary-letter class", "class 𐐀xtra {}"),
    ("letter-number class", "class Ⅰxtra {}"),
    ("connector-punctuation class", "class ‿xtra {}"),
)
ESCAPED_SECOND_DECLARATION_VARIANTS = (
    ("class", r"\u0063lass EscapedClass {}"),
    ("interface", r"\u0069nterface EscapedInterface {}"),
    ("enum", r"\u0065num EscapedEnum { VALUE }"),
    ("record", r"\u0072ecord EscapedRecord() {}"),
    ("annotation interface", r"@\u0069nterface EscapedAnnotation {}"),
    ("repeated-u class", r"\uuuu0063lass RepeatedUClass {}"),
)
INSTANCEOF_EXPRESSION_MEMBERS = (
    (
        "class literal",
        (
            "    static boolean classLiteral() {\n"
            "        return String.class instanceof Object;\n"
            "    }"
        ),
    ),
    (
        "contextual record",
        (
            "    static boolean contextualRecord(Object record) {\n"
            "        return record instanceof String;\n"
            "    }"
        ),
    ),
)
MULTILINE_GENERIC_PRIMARY_RECORD = "public record OrderId<\n    É\n>(É value) {}"
MULTILINE_GENERIC_SECOND_RECORD = "record Éxtra<\n    T\n>(T value) {}"


class SourceComprehensionOracleTests(unittest.TestCase):
    def test_cli_reports_a_missing_case_or_undecodable_source_as_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            case = Path(directory) / "case"
            shutil.copytree(FIXTURES / "accepted-consequential", case)
            (case / "src" / "DeadlineBudget.java").write_bytes(b"\xff\xfe not text\n")
            for target in (Path(directory) / "absent-case", case):
                with self.subTest(target=target.name):
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as exit_:
                        main([str(target)])
                    self.assertEqual(exit_.exception.code, 1)
                    self.assertTrue(stderr.getvalue().startswith("FAIL:"), stderr.getvalue())

    def test_case_path_that_cannot_be_checked_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(SourceComprehensionError, "source cannot be checked"):
                _relative_file(Path(directory), "a" * 300, "source")

    def copy_case(self, name: str) -> tuple[tempfile.TemporaryDirectory, Path]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        target = Path(temporary.name) / name
        shutil.copytree(FIXTURES / name, target)
        return temporary, target

    def mutate_text(self, case: Path, relative: str, old: str, new: str = "") -> None:
        path = case / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def mutate_record(self, case: Path, key: str, value: object) -> None:
        path = case / "review-case.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        record[key] = value
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def add_second_declaration(self, case: Path, declaration: str | None) -> Path:
        path = case / "src" / "OrderId.java"
        source = path.read_text(encoding="utf-8")
        if declaration is None:
            source = source.replace(
                "public record OrderId(String value) {}",
                "public record OrderId(String value) { static class Nested {} }",
                1,
            )
        else:
            source += f"\n{declaration}\n"
        path.write_text(source, encoding="utf-8")
        return path

    def test_rejects_nontrivial_source_without_orientation(self) -> None:
        _, case = self.copy_case("missing-orientation")
        with self.assertRaisesRegex(SourceComprehensionError, "orientation"):
            verify_case(case)

    def test_rejects_tests_and_unlinked_adr_as_source_substitutes(self) -> None:
        _, case = self.copy_case("tests-and-unlinked-adr")
        with self.assertRaisesRegex(SourceComprehensionError, "local rationale"):
            verify_case(case)

    def test_accepts_concise_native_contract_local_rationale_and_exact_adr_anchor(self) -> None:
        _, case = self.copy_case("accepted-consequential")
        verify_case(case)

    def test_accepts_one_sentence_orientation_for_simple_source(self) -> None:
        _, case = self.copy_case("accepted-simple")
        verify_case(case)

    def test_allows_only_whitespace_or_annotations_after_orientation(self) -> None:
        _, case = self.copy_case("accepted-simple")
        self.mutate_text(
            case,
            "src/OrderId.java",
            "*/\npublic record",
            "*/\n@Deprecated\npublic record",
        )
        verify_case(case)

    def test_declaration_gap_regex_stays_linear_on_adversarial_whitespace(self) -> None:
        """A long whitespace gap before an unmatchable token must not hang the oracle.

        The gap is attacker-controlled fixture bytes. Matching must be bounded (linear)
        rather than backtracking catastrophically, so it completes well within a small
        wall-clock budget instead of tens of seconds to hours.
        """
        gap = " " * 48 + "!"  # >=40 contiguous whitespace, then an unmatchable token
        process = multiprocessing.Process(target=_match_declaration_gap, args=(gap,))
        process.start()
        process.join(timeout=10)
        timed_out = process.is_alive()
        if timed_out:
            process.terminate()
            process.join()
        self.assertFalse(
            timed_out,
            "JAVA_DECLARATION_GAP_RE backtracked catastrophically on a bounded gap",
        )
        self.assertEqual(process.exitcode, 0)

    def test_allows_flat_annotation_string_char_and_text_block_arguments(self) -> None:
        _, case = self.copy_case("accepted-simple")
        annotation_gap = (
            "*/\n"
            + '@SuppressWarnings("why (bounded)")\n'
            + "@Label('(')\n"
            + '@Label("""\n'
            + "    class TextBlockFake\n"
            + '    """)\n'
            + "public record"
        )
        self.mutate_text(
            case,
            "src/OrderId.java",
            "*/\npublic record",
            annotation_gap,
        )
        verify_case(case)

    def test_ignores_decoy_type_tokens_in_comments_and_annotation_strings(self) -> None:
        _, case = self.copy_case("accepted-simple")
        self.mutate_text(
            case,
            "src/OrderId.java",
            "\n/** Carries",
            "\n// class CommentFake must not select a type.\n/** Carries",
        )
        self.mutate_text(
            case,
            "src/OrderId.java",
            "*/\npublic record",
            '*/\n@Label("class Fake")\npublic record',
        )
        verify_case(case)

    def test_accepts_primary_annotation_declaration_adjacency_forms(self) -> None:
        """Annotation declarations start at @ across Java's lexical-space forms."""
        for name, declaration in (
            ("compact", "@interface"),
            ("spaced", "@ interface"),
            ("comment separated", "@/* declaration marker */interface"),
        ):
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-simple")
                path = case / "src" / "OrderId.java"
                source = path.read_text(encoding="utf-8")
                path.write_text(
                    source.replace(
                        "public record OrderId(String value) {}",
                        f"public {declaration} OrderId {{}}",
                        1,
                    ),
                    encoding="utf-8",
                )
                verify_case(case)

    @unittest.skipUnless(shutil.which("javac"), "javac is unavailable")
    def test_primary_annotation_declaration_adjacency_forms_are_valid_java(self) -> None:
        """The annotation adjacency GREENs are compiler-valid controls."""
        for name, declaration in (
            ("compact", "@interface"),
            ("spaced", "@ interface"),
            ("comment separated", "@/* declaration marker */interface"),
        ):
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-simple")
                path = case / "src" / "OrderId.java"
                source = path.read_text(encoding="utf-8")
                path.write_text(
                    source.replace(
                        "public record OrderId(String value) {}",
                        f"public {declaration} OrderId {{}}",
                        1,
                    ),
                    encoding="utf-8",
                )
                with tempfile.TemporaryDirectory() as output:
                    completed = subprocess.run(
                        ["javac", "-d", output, str(path)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_accepts_literal_unicode_primary_declarations(self) -> None:
        """Literal Unicode identifiers and annotation syntax remain supported controls."""
        for name, declaration in (
            ("record", "record Éxtra(String value) {}"),
            ("annotation interface", "@interface Éxtra {}"),
        ):
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-simple")
                path = case / "src" / "OrderId.java"
                source = path.read_text(encoding="utf-8")
                path.write_text(
                    source.replace("public record OrderId(String value) {}", declaration, 1),
                    encoding="utf-8",
                )
                verify_case(case)

    def test_accepts_multiline_unicode_generic_primary_record(self) -> None:
        """A multiline generic header still identifies the primary record."""
        _, case = self.copy_case("accepted-simple")
        self.mutate_text(
            case,
            "src/OrderId.java",
            "public record OrderId(String value) {}",
            MULTILINE_GENERIC_PRIMARY_RECORD,
        )
        verify_case(case)

    def test_rejects_multiline_unicode_generic_second_record(self) -> None:
        """A multiline generic header cannot hide a second record declaration."""
        _, case = self.copy_case("accepted-simple")
        path = case / "src" / "OrderId.java"
        path.write_text(
            path.read_text(encoding="utf-8") + f"\n{MULTILINE_GENERIC_SECOND_RECORD}\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            SourceComprehensionError,
            "exactly one supported authored Java type declaration",
        ):
            verify_case(case)

    def test_record_name_cannot_absorb_malformed_generic_delimiters(self) -> None:
        """Malformed generic text is not a second bounded record declaration."""
        for name, declaration in (
            ("parenthesis", "record R<T(call)>(T value) {}"),
            ("braces", "record R<T{part}>(T value) {}"),
            ("semicolon", "record R<T;part>(T value) {}"),
        ):
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-simple")
                path = case / "src" / "OrderId.java"
                path.write_text(
                    path.read_text(encoding="utf-8") + f"\n{declaration}\n",
                    encoding="utf-8",
                )
                verify_case(case)

    @unittest.skipUnless(shutil.which("javac"), "javac is unavailable")
    def test_multiline_unicode_generic_record_controls_are_valid_java(self) -> None:
        """Both multiline generic semantic controls remain compiler-valid."""
        for name in ("primary", "second declaration"):
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-simple")
                path = case / "src" / "OrderId.java"
                source = path.read_text(encoding="utf-8")
                if name == "primary":
                    source = source.replace(
                        "public record OrderId(String value) {}",
                        MULTILINE_GENERIC_PRIMARY_RECORD,
                        1,
                    )
                else:
                    source += f"\n{MULTILINE_GENERIC_SECOND_RECORD}\n"
                path.write_text(source, encoding="utf-8")
                with tempfile.TemporaryDirectory() as output:
                    completed = subprocess.run(
                        ["javac", "-d", output, str(path)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                self.assertEqual(completed.returncode, 0, completed.stderr)

    @unittest.skipUnless(shutil.which("javac"), "javac is unavailable")
    def test_literal_unicode_primary_declarations_are_valid_java(self) -> None:
        """Literal Unicode declaration GREENs are compiler-valid controls."""
        for name, declaration in (
            ("record", "record Éxtra(String value) {}"),
            ("annotation interface", "@interface Éxtra {}"),
        ):
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-simple")
                path = case / "src" / "OrderId.java"
                source = path.read_text(encoding="utf-8")
                path.write_text(
                    source.replace("public record OrderId(String value) {}", declaration, 1),
                    encoding="utf-8",
                )
                with tempfile.TemporaryDirectory() as output:
                    completed = subprocess.run(
                        ["javac", "-d", output, str(path)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_accepts_contextual_record_uses_without_extra_declarations(self) -> None:
        """Contextual record variables and calls are not declaration-name tokens."""
        _, case = self.copy_case("accepted-simple")
        path = case / "src" / "OrderId.java"
        source = path.read_text(encoding="utf-8")
        path.write_text(
            source.replace(
                "public record OrderId(String value) {}",
                "public record OrderId(String value) {\n"
                "    static int record = 0;\n"
                "    static int record() { return record; }\n"
                "    static int current() { return record(); }\n"
                "}",
                1,
            ),
            encoding="utf-8",
        )
        verify_case(case)

    def test_accepts_instanceof_expressions_without_extra_declarations(self) -> None:
        """Class literals and contextual record operands are expression tokens."""
        for name, member in INSTANCEOF_EXPRESSION_MEMBERS:
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-simple")
                path = case / "src" / "OrderId.java"
                source = path.read_text(encoding="utf-8")
                path.write_text(
                    source.replace(
                        "public record OrderId(String value) {}",
                        f"public record OrderId(String value) {{\n{member}\n}}",
                        1,
                    ),
                    encoding="utf-8",
                )
                verify_case(case)

    @unittest.skipUnless(shutil.which("javac"), "javac is unavailable")
    def test_instanceof_expression_controls_are_valid_java(self) -> None:
        """The expression-token GREENs remain compiler-valid controls."""
        for name, member in INSTANCEOF_EXPRESSION_MEMBERS:
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-simple")
                path = case / "src" / "OrderId.java"
                source = path.read_text(encoding="utf-8")
                path.write_text(
                    source.replace(
                        "public record OrderId(String value) {}",
                        f"public record OrderId(String value) {{\n{member}\n}}",
                        1,
                    ),
                    encoding="utf-8",
                )
                with tempfile.TemporaryDirectory() as output:
                    completed = subprocess.run(
                        ["javac", "-d", output, str(path)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                self.assertEqual(completed.returncode, 0, completed.stderr)

    @unittest.skipUnless(shutil.which("javac"), "javac is unavailable")
    def test_contextual_record_uses_are_valid_java(self) -> None:
        """The contextual-record GREEN remains a compiler-valid control."""
        _, case = self.copy_case("accepted-simple")
        path = case / "src" / "OrderId.java"
        source = path.read_text(encoding="utf-8")
        path.write_text(
            source.replace(
                "public record OrderId(String value) {}",
                "public record OrderId(String value) {\n"
                "    static int record = 0;\n"
                "    static int record() { return record; }\n"
                "    static int current() { return record(); }\n"
                "}",
                1,
            ),
            encoding="utf-8",
        )
        with tempfile.TemporaryDirectory() as output:
            completed = subprocess.run(
                ["javac", "-d", output, str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_java_identifier_start_categories_are_bounded(self) -> None:
        """The declaration-name gate admits Java categories, not arbitrary syntax."""
        for character in ("$", "_", "É", "Ⅰ", "€", "‿", "𐐀"):
            with self.subTest(character=character):
                self.assertTrue(_java_identifier_start(character))
        for character in ("=", "(", "0", "!"):
            with self.subTest(character=character):
                self.assertFalse(_java_identifier_start(character))

    def test_rejects_raw_java_unicode_escape_syntax_before_lexing(self) -> None:
        """Valid javac escapes fail closed rather than bypassing the bounded lexical view."""
        diagnostic = "fixture source must not contain raw Java Unicode escape syntax"
        for name, declaration in ESCAPED_SECOND_DECLARATION_VARIANTS:
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-simple")
                path = case / "src" / "OrderId.java"
                path.write_text(
                    path.read_text(encoding="utf-8") + f"\n{declaration}\n",
                    encoding="utf-8",
                )
                with self.assertRaises(SourceComprehensionError) as caught:
                    verify_case(case)
                self.assertEqual(str(caught.exception), diagnostic)

    @unittest.skipUnless(shutil.which("javac"), "javac is unavailable")
    def test_raw_java_unicode_escape_rejections_use_valid_java_controls(self) -> None:
        """Every raw-escape RED remains a compiler-valid control."""
        for name, declaration in ESCAPED_SECOND_DECLARATION_VARIANTS:
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-simple")
                path = case / "src" / "OrderId.java"
                path.write_text(
                    path.read_text(encoding="utf-8") + f"\n{declaration}\n",
                    encoding="utf-8",
                )
                with tempfile.TemporaryDirectory() as output:
                    completed = subprocess.run(
                        ["javac", "-d", output, str(path)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_rejects_every_second_supported_java_declaration(self) -> None:
        """The bounded fixture proves one declaration, not merely the first one found."""
        diagnostic = (
            "fixture source must contain exactly one supported authored Java type declaration"
        )
        for name, declaration in SECOND_DECLARATION_VARIANTS:
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-simple")
                self.add_second_declaration(case, declaration)
                with self.assertRaises(SourceComprehensionError) as caught:
                    verify_case(case)
                self.assertEqual(str(caught.exception), diagnostic)

    @unittest.skipUnless(shutil.which("javac"), "javac is unavailable")
    def test_second_declaration_rejections_use_valid_java_controls(self) -> None:
        """Each exact-one RED remains valid Java rather than a parser-error substitute."""
        for name, declaration in SECOND_DECLARATION_VARIANTS:
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-simple")
                path = self.add_second_declaration(case, declaration)
                with tempfile.TemporaryDirectory() as output:
                    completed = subprocess.run(
                        ["javac", "-d", output, str(path)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_accepts_overlapping_escaped_text_block_closer(self) -> None:
        _, case = self.copy_case("accepted-simple")
        path = case / "src/OrderId.java"
        overlapping_close = "\\" + ('"' * 4) + ")"
        self.mutate_text(
            case,
            "src/OrderId.java",
            "*/\npublic record",
            '*/\n@SuppressWarnings("""\n    ' + overlapping_close + "\npublic record",
        )
        self.assertIn(b"\\\x22\x22\x22\x22\x29", path.read_bytes())
        verify_case(case)

    @unittest.skipUnless(shutil.which("javac"), "javac is unavailable")
    def test_overlapping_escaped_text_block_closer_is_valid_java(self) -> None:
        """The overlapping text-block GREEN is a compiler-valid control."""
        _, case = self.copy_case("accepted-simple")
        path = case / "src/OrderId.java"
        overlapping_close = "\\" + ('"' * 4) + ")"
        self.mutate_text(
            case,
            "src/OrderId.java",
            "*/\npublic record",
            '*/\n@SuppressWarnings("""\n    ' + overlapping_close + "\npublic record",
        )
        with tempfile.TemporaryDirectory() as output:
            completed = subprocess.run(
                ["javac", "-d", output, str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_rejects_escaped_text_block_decoy_in_valid_java_source(self) -> None:
        _, case = self.copy_case("accepted-simple")
        path = case / "src/OrderId.java"
        source = path.read_text(encoding="utf-8")
        orientation = (
            "/** Carries the stable identifier used to correlate one order across adapters. */\n"
        )
        self.assertIn(orientation, source)
        decoy = (
            '@SuppressWarnings("""\n'
            + r'    \"""'
            + "\n"
            + "    /** Carries the stable identifier used to correlate one order across adapters. */\n"
            + "    class Fake {}\n"
            + '    """)\n'
        )
        path.write_text(source.replace(orientation, decoy, 1), encoding="utf-8")
        with self.assertRaisesRegex(SourceComprehensionError, "orientation"):
            verify_case(case)

    @unittest.skipUnless(shutil.which("javac"), "javac is unavailable")
    def test_escaped_text_block_decoy_is_valid_java(self) -> None:
        """The escaped text-block RED input itself remains compiler-valid."""
        _, case = self.copy_case("accepted-simple")
        path = case / "src/OrderId.java"
        source = path.read_text(encoding="utf-8")
        orientation = (
            "/** Carries the stable identifier used to correlate one order across adapters. */\n"
        )
        decoy = (
            '@SuppressWarnings("""\n'
            + r'    \"""'
            + "\n"
            + "    /** Carries the stable identifier used to correlate one order across adapters. */\n"
            + "    class Fake {}\n"
            + '    """)\n'
        )
        path.write_text(source.replace(orientation, decoy, 1), encoding="utf-8")
        with tempfile.TemporaryDirectory() as output:
            completed = subprocess.run(
                ["javac", "-d", output, str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_rejects_boolean_schema_version_and_displaced_orientation(self) -> None:
        _, case = self.copy_case("accepted-consequential")
        self.mutate_record(case, "schema_version", True)
        with self.assertRaisesRegex(SourceComprehensionError, "schema_version"):
            verify_case(case)

        _, case = self.copy_case("accepted-consequential")
        self.mutate_text(
            case,
            "src/DeadlineBudget.java",
            "*/\npublic final class",
            "*/\n// A later comment displaces the declared orientation.\npublic final class",
        )
        with self.assertRaisesRegex(SourceComprehensionError, "immediately orient"):
            verify_case(case)

    def test_rejects_duplicate_verdict_before_safe_value(self) -> None:
        """A later CLEAN verdict must not silently replace an earlier FINDING."""
        _, case = self.copy_case("accepted-simple")
        path = case / "review-case.json"
        record = path.read_text(encoding="utf-8")
        path.write_text(
            record.replace(
                '  "verdict": "CLEAN",',
                '  "verdict": "FINDING",\n  "verdict": "CLEAN",',
                1,
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(SourceComprehensionError, "duplicate JSON object key: verdict"):
            verify_case(case)

    def test_requires_local_rationale_in_the_declaration_comment(self) -> None:
        fragments = (
            "All stored and returned durations are monotonic milliseconds",
            "exhaustion fails closed before another attempt starts",
        )
        for fragment in fragments:
            with self.subTest(fragment=fragment):
                _, case = self.copy_case("accepted-consequential")
                path = case / "src/DeadlineBudget.java"
                source = path.read_text(encoding="utf-8")
                self.assertIn(fragment, source)
                path.write_text(
                    source.replace(fragment, "", 1) + f"\n// {fragment}\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(SourceComprehensionError, "local rationale"):
                    verify_case(case)

    def test_rejects_adr_anchor_relocated_to_trailing_comment(self) -> None:
        """An exact ADR link elsewhere cannot replace declaration-adjacent rationale."""
        _, case = self.copy_case("accepted-consequential")
        path = case / "src" / "DeadlineBudget.java"
        source = path.read_text(encoding="utf-8")
        fragment = "docs/adr/0001-deadline-policy.md#monotonic-budget"
        self.assertIn(fragment, source)
        path.write_text(
            source.replace(fragment, "", 1) + f"\n// {fragment}\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(SourceComprehensionError, "exact ADR anchor"):
            verify_case(case)

        _, unchanged = self.copy_case("accepted-consequential")
        verify_case(unchanged)
        self.assertIn(
            "## Monotonic budget",
            (unchanged / "docs/adr/0001-deadline-policy.md").read_text(encoding="utf-8"),
        )

    def test_adr_heading_record_requires_canonical_one_line_atx_form(self) -> None:
        """A unique visible prose line is not a declared ATX heading target."""
        diagnostic = "ADR heading must be a canonical one-line ATX heading"
        malformed = (
            (
                "existing unique prose line",
                (
                    "One monotonic budget spans all retry attempts so retries cannot "
                    "extend the caller's"
                ),
            ),
            ("no hash", "Monotonic budget"),
            ("seven hashes", "####### Monotonic budget"),
            ("missing space", "##Monotonic budget"),
            ("empty string", ""),
            ("empty content", "## "),
            ("double separator space", "##  Monotonic budget"),
            ("leading padding", " ## Monotonic budget"),
            ("trailing padding", "## Monotonic budget "),
        )
        for name, heading in malformed:
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-consequential")
                record_path = case / "review-case.json"
                record = json.loads(record_path.read_text(encoding="utf-8"))
                record["exact_adr_anchor"]["heading"] = heading
                record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
                with self.assertRaises(SourceComprehensionError) as caught:
                    verify_case(case)
                self.assertEqual(str(caught.exception), diagnostic)

        original_heading = "## Monotonic budget"
        for invalid_heading in ("## #", "## ###"):
            with self.subTest(atomic_hash_only=invalid_heading):
                _, case = self.copy_case("accepted-consequential")
                self.mutate_text(
                    case,
                    "docs/adr/0001-deadline-policy.md",
                    original_heading,
                    invalid_heading,
                )
                record_path = case / "review-case.json"
                record = json.loads(record_path.read_text(encoding="utf-8"))
                record["exact_adr_anchor"]["heading"] = invalid_heading
                record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
                with self.assertRaises(SourceComprehensionError) as caught:
                    verify_case(case)
                self.assertEqual(str(caught.exception), diagnostic)

        for valid_heading in (r"## \#", "## Ordinary heading"):
            with self.subTest(atomic_material_heading=valid_heading):
                _, case = self.copy_case("accepted-consequential")
                self.mutate_text(
                    case,
                    "docs/adr/0001-deadline-policy.md",
                    original_heading,
                    valid_heading,
                )
                record_path = case / "review-case.json"
                record = json.loads(record_path.read_text(encoding="utf-8"))
                record["exact_adr_anchor"]["heading"] = valid_heading
                record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
                verify_case(case)

    def test_adr_heading_requires_visible_content_beyond_synthetic_ignorables(
        self,
    ) -> None:
        """Default-ignorables alone cannot manufacture material ATX content."""
        original_heading = "## Monotonic budget"
        diagnostic = "ADR heading must be a canonical one-line ATX heading"
        for character in ("\u034f", "\ufe00", "\U000e0100"):
            with self.subTest(only_content=f"U+{ord(character):04X}"):
                _, case = self.copy_case("accepted-consequential")
                synthetic_heading = f"## {character}"
                self.mutate_text(
                    case,
                    "docs/adr/0001-deadline-policy.md",
                    original_heading,
                    synthetic_heading,
                )
                record_path = case / "review-case.json"
                record = json.loads(record_path.read_text(encoding="utf-8"))
                record["exact_adr_anchor"]["heading"] = synthetic_heading
                record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
                with self.assertRaises(SourceComprehensionError) as caught:
                    verify_case(case)
                self.assertEqual(str(caught.exception), diagnostic)

        for visible_heading in ("## É\u034f", "## 文\ufe00", "## 👩‍💻"):
            with self.subTest(mixed_visible_content=visible_heading):
                _, case = self.copy_case("accepted-consequential")
                self.mutate_text(
                    case,
                    "docs/adr/0001-deadline-policy.md",
                    original_heading,
                    visible_heading,
                )
                record_path = case / "review-case.json"
                record = json.loads(record_path.read_text(encoding="utf-8"))
                record["exact_adr_anchor"]["heading"] = visible_heading
                record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
                verify_case(case)

    def test_adr_heading_requires_material_content_after_inline_comments(self) -> None:
        """Only complete inline comments disappear from rendered heading material."""
        original_heading = "## Monotonic budget"
        diagnostic = "ADR heading must be a canonical one-line ATX heading"
        for name, heading in (
            ("closed comment only", "## <!-- hidden -->"),
            ("adjacent comments", "## <!-- one --><!-- two -->"),
            ("spaced comments", "## <!-- one --> <!-- two -->"),
            ("comment and closing hashes", "## <!-- hidden --> ###"),
            ("comment and synthetic residue", "## <!-- hidden --> \u034f"),
            ("short complete comment", "## <!-->"),
            ("short hyphenated complete comment", "## <!--->"),
        ):
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-consequential")
                self.mutate_text(
                    case,
                    "docs/adr/0001-deadline-policy.md",
                    original_heading,
                    heading,
                )
                record_path = case / "review-case.json"
                record = json.loads(record_path.read_text(encoding="utf-8"))
                record["exact_adr_anchor"]["heading"] = heading
                record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
                with self.assertRaises(SourceComprehensionError) as caught:
                    verify_case(case)
                self.assertEqual(str(caught.exception), diagnostic)

        for name, heading in (
            ("visible before comment", "## Visible policy <!-- note -->"),
            ("visible after comment", "## <!-- note --> Visible policy"),
            ("unclosed comment is literal", "## <!-- visible literal"),
            (
                "complete comments and unclosed tail",
                "## <!-- one --><!-- two --> <!-- visible literal",
            ),
        ):
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-consequential")
                self.mutate_text(
                    case,
                    "docs/adr/0001-deadline-policy.md",
                    original_heading,
                    heading,
                )
                record_path = case / "review-case.json"
                record = json.loads(record_path.read_text(encoding="utf-8"))
                record["exact_adr_anchor"]["heading"] = heading
                record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
                verify_case(case)

    def test_adr_target_requires_one_exact_visible_raw_heading(self) -> None:
        """Hidden, quoted, prefixed, prose-only, or duplicate targets cannot rescue ADR."""
        heading = "## Monotonic budget"
        diagnostic = "ADR heading target must appear exactly once as a visible raw line"
        replacements = (
            ("multiline HTML comment", f"<!--\n{heading}\n-->"),
            ("same-line HTML comment", f"<!-- {heading} -->"),
            ("backtick fence", f"```markdown\n{heading}\n```"),
            ("tilde fence", f"~~~markdown\n{heading}\n~~~"),
            ("blockquote", f"> {heading}"),
            ("prefixed heading", f"Policy target: {heading}"),
            ("substring prose", f"See `{heading}` for the retry policy."),
            ("duplicate visible heading", f"{heading}\n\n{heading}"),
        )
        for name, replacement in replacements:
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-consequential")
                self.mutate_text(
                    case,
                    "docs/adr/0001-deadline-policy.md",
                    heading,
                    replacement,
                )
                with self.assertRaisesRegex(SourceComprehensionError, diagnostic):
                    verify_case(case)

        _, baseline = self.copy_case("accepted-consequential")
        verify_case(baseline)

        _, renamed = self.copy_case("accepted-consequential")
        replacement_heading = "## Shared monotonic deadline"
        self.mutate_text(
            renamed,
            "docs/adr/0001-deadline-policy.md",
            heading,
            replacement_heading,
        )
        record_path = renamed / "review-case.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        record["exact_adr_anchor"]["heading"] = replacement_heading
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        verify_case(renamed)

    def test_non_markdown_separators_cannot_create_visible_adr_heading(self) -> None:
        """Python-only line boundaries remain content before an exact ADR heading."""
        heading = "## Monotonic budget"
        diagnostic = "ADR heading target must appear exactly once as a visible raw line"
        for separator_name, separator in NON_MARKDOWN_LINE_SEPARATORS:
            with self.subTest(separator=separator_name):
                _, case = self.copy_case("accepted-consequential")
                self.mutate_text(
                    case,
                    "docs/adr/0001-deadline-policy.md",
                    heading,
                    separator + heading,
                )
                with self.assertRaisesRegex(SourceComprehensionError, diagnostic):
                    verify_case(case)

    def test_backtick_in_info_string_does_not_hide_visible_adr_heading(self) -> None:
        """An invalid backtick-fence info string remains ordinary visible prose."""
        _, case = self.copy_case("accepted-consequential")
        heading = "## Monotonic budget"
        self.mutate_text(
            case,
            "docs/adr/0001-deadline-policy.md",
            heading,
            "```lang`invalid\n" + heading,
        )
        verify_case(case)

    def test_comment_text_cannot_synthesize_or_leak_from_fences_before_adr(
        self,
    ) -> None:
        """Comment syntax outside/inside fence info cannot hide the later ADR target."""
        heading = "## Monotonic budget"
        prefixes = (
            ("comment-stripped lookalike", "<!--x-->```markdown"),
            ("backtick info literal", "```markdown <!--\ndecoy\n```"),
            ("tilde info literal", "~~~markdown <!--\ndecoy\n~~~"),
        )
        for name, prefix in prefixes:
            with self.subTest(name=name):
                _, case = self.copy_case("accepted-consequential")
                self.mutate_text(
                    case,
                    "docs/adr/0001-deadline-policy.md",
                    heading,
                    prefix + "\n" + heading,
                )
                verify_case(case)

    def test_visible_adr_heading_accepts_commonmark_line_endings(self) -> None:
        """LF, CRLF, and CR remain valid around the exact raw ADR heading."""
        for name, line_ending in (("LF", "\n"), ("CRLF", "\r\n"), ("CR", "\r")):
            with self.subTest(line_ending=name):
                _, case = self.copy_case("accepted-consequential")
                path = case / "docs/adr/0001-deadline-policy.md"
                path.write_bytes(path.read_bytes().replace(b"\n", line_ending.encode()))
                verify_case(case)

    def test_mutations_remove_load_bearing_source_and_review_evidence(self) -> None:
        mutations = (
            (
                "class contract",
                "src/DeadlineBudget.java",
                "Coordinates the request deadline budget shared by retry attempts.",
                "",
                "orientation",
            ),
            (
                "units",
                "src/DeadlineBudget.java",
                "All stored and returned durations are monotonic milliseconds",
                "Stored and returned durations use the caller's clock",
                "applicable local rationale",
            ),
            (
                "failure",
                "src/DeadlineBudget.java",
                "exhaustion fails closed before another attempt starts",
                "exhaustion is reported later",
                "applicable local rationale",
            ),
            (
                "ADR source anchor",
                "src/DeadlineBudget.java",
                "docs/adr/0001-deadline-policy.md#monotonic-budget",
                "docs/adr/0001-deadline-policy.md",
                "exact ADR anchor",
            ),
            (
                "ADR target heading",
                "docs/adr/0001-deadline-policy.md",
                "## Monotonic budget",
                "## Deadline notes",
                "ADR heading",
            ),
        )
        for label, relative, old, new, expected in mutations:
            with self.subTest(label=label):
                _, case = self.copy_case("accepted-consequential")
                self.mutate_text(case, relative, old, new)
                with self.assertRaisesRegex(SourceComprehensionError, expected):
                    verify_case(case)

        _, case = self.copy_case("accepted-consequential")
        self.mutate_record(case, "changed_source_assessed", False)
        with self.assertRaisesRegex(SourceComprehensionError, "changed-source assessment"):
            verify_case(case)

        _, case = self.copy_case("accepted-consequential")
        self.mutate_record(case, "reviewer", "example-writer")
        with self.assertRaisesRegex(SourceComprehensionError, "non-author"):
            verify_case(case)

    def test_rejects_padded_or_aliased_self_review_identity(self) -> None:
        """Whitespace, case, and compatibility aliases cannot manufacture independence."""
        for reviewer, error in (
            (" example-writer ", "canonical"),
            ("EXAMPLE-WRITER", "non-author"),
            ("ｅｘａｍｐｌｅ－ｗｒｉｔｅｒ", "non-author"),
        ):
            with self.subTest(reviewer=reviewer):
                _, case = self.copy_case("accepted-consequential")
                self.mutate_record(case, "reviewer", reviewer)
                with self.assertRaisesRegex(SourceComprehensionError, error):
                    verify_case(case)

    def test_rejects_synthetic_ignorables_in_author_or_reviewer(self) -> None:
        """DICP and runtime-Cf controls cannot alter either review identity."""
        for field in ("author", "reviewer"):
            for control in ("\u034f", "\ufe0f", "\U000e0100", "\u0600"):
                value = f"example{control}-writer"
                with self.subTest(field=field, codepoint=f"U+{ord(control):04X}"):
                    _, case = self.copy_case("accepted-consequential")
                    self.mutate_record(case, field, value)
                    with self.assertRaisesRegex(
                        SourceComprehensionError, "synthetic Unicode ignorables"
                    ):
                        verify_case(case)

    def test_unsafe_unicode_evidence_characters_reject_identity_and_heading(self) -> None:
        """Control, surrogate, private-use, and unassigned evidence fails ingress."""
        unsafe = (
            "\x00",
            "\x07",
            "\x7f",
            "\x85",
            "\t",
            "\n",
            "\ud800",
            "\ue000",
            "\u0378",
        )
        for field in ("author", "reviewer"):
            for character in unsafe:
                with self.subTest(field=field, codepoint=f"U+{ord(character):04X}"):
                    _, case = self.copy_case("accepted-consequential")
                    self.mutate_record(case, field, f"example{character}-writer")
                    with self.assertRaisesRegex(
                        SourceComprehensionError,
                        "unsafe Unicode evidence characters",
                    ):
                        verify_case(case)

        for character in unsafe:
            with self.subTest(heading=f"U+{ord(character):04X}"):
                _, case = self.copy_case("accepted-consequential")
                record_path = case / "review-case.json"
                record = json.loads(record_path.read_text(encoding="utf-8"))
                record["exact_adr_anchor"]["heading"] = f"## Monotonic{character} budget"
                record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
                with self.assertRaisesRegex(
                    SourceComprehensionError,
                    "ADR heading must not contain unsafe Unicode evidence characters",
                ):
                    verify_case(case)

        _, ordinary = self.copy_case("accepted-consequential")
        self.mutate_record(ordinary, "author", "éxample-writer")
        verify_case(ordinary)


if __name__ == "__main__":
    unittest.main()
