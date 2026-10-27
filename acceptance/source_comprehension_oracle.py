"""Verify the repository's small synthetic source-comprehension cases.

This is intentionally *not* a Java parser, comment-quality classifier, or reusable
project linter. It only checks independently declared literal evidence in the bounded
fixtures under ``acceptance/fixtures/source-comprehension``. Real projects must adopt
their language/community form and use human review of the complete changed-source set.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

if __package__:
    from .strict_json import DuplicateJsonKeyError
    from .strict_json import loads as strict_json_loads
    from .unicode_policy import (
        is_synthetic_ignorable,
        is_unsafe_evidence_character,
        markdown_fence_closing,
        markdown_fence_opening,
        nfkc_casefold,
        split_markdown_lines,
    )
else:
    from strict_json import DuplicateJsonKeyError
    from strict_json import loads as strict_json_loads
    from unicode_policy import (  # type: ignore[no-redef]
        is_synthetic_ignorable,
        is_unsafe_evidence_character,
        markdown_fence_closing,
        markdown_fence_opening,
        nfkc_casefold,
        split_markdown_lines,
    )


CASE_KEYS = {
    "schema_version",
    "purpose",
    "language_native_form",
    "source_path",
    "classification",
    "orientation_fragment",
    "required_local_fragments",
    "exact_adr_anchor",
    "changed_source_assessed",
    "author",
    "reviewer",
    "verdict",
    "limitation",
}
ADR_KEYS = {"document", "source_fragment", "heading"}
ATX_HEADING_RE = re.compile(r"#{1,6} (?=[^\r\n]*[^\s#])\S(?:[^\r\n]*\S)?\Z")
JAVA_NATIVE_FORM = "Java Javadoc or file-level comment immediately before the authored type"
TYPE_RE = re.compile(
    r"""
    (?:
        @\s*interface
      | \b(?:class|interface|enum)
      # A record header may span lines, but the name and generic own disjoint delimiters.
      | \brecord(?=\s+[^\s<>(){};]+\s*(?:<[^(){};]*>\s*)?\()
    )
    \s+(?P<identifier>\S)
    """,
    re.VERBOSE,
)
JAVA_UNICODE_ESCAPE_RE = re.compile(r"\\u+[0-9A-Fa-f]{4}")
# The bounded Java form permits only whitespace, flat annotations, and standard
# declaration modifiers between the declared orientation comment and its type token.
JAVA_DECLARATION_GAP_RE = re.compile(
    r"""
    (?:
        \s
      | @[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*(?:\s*\([^()]*\))?
      | \b(?:public|protected|private|abstract|static|final|sealed|non-sealed|strictfp)\b
    )*
    \Z
    """,
    re.VERBOSE,
)


class SourceComprehensionError(ValueError):
    """Raised when a synthetic case lacks its declared comprehension evidence."""


def _is_canonical_atx_heading(value: Any) -> bool:
    """Require visible material beyond ATX syntax and synthetic ignorables.

    Assigned ignorables remain valid alongside visible Unicode content so variation
    selectors and joiners do not make otherwise material headings invalid.
    """
    if not isinstance(value, str) or ATX_HEADING_RE.fullmatch(value) is None:
        return False

    content = value.split(" ", 1)[1]
    comment_free: list[str] = []
    position = 0
    while position < len(content):
        start = content.find("<!--", position)
        if start == -1:
            comment_free.append(content[position:])
            break
        comment_free.append(content[position:start])
        end = content.find("-->", start + 2)
        if end == -1:
            comment_free.append(content[start:])
            break
        position = end + 3

    return any(
        character != "#" and not character.isspace() and not is_synthetic_ignorable(character)
        for character in "".join(comment_free)
    )


def _java_identifier_start(character: str) -> bool:
    """Recognize the bounded Java identifier-start categories used by these fixtures."""
    category = unicodedata.category(character)
    return (
        character in {"$", "_"}
        or category.startswith("L")
        or category
        in {
            "Nl",
            "Sc",
            "Pc",
        }
    )


def _java_type_declaration_candidate(code: str, match: re.Match[str]) -> bool:
    """Keep bounded declarations, excluding class literals after member selection."""
    if not _java_identifier_start(match.group("identifier")):
        return False
    return not code[: match.start()].rstrip().endswith(".")


def _visible_raw_line_count(text: str, exact_line: str) -> int:
    """Count exact raw lines outside bounded comments and Markdown fences.

    This deliberately recognizes only HTML comments and standard backtick/tilde
    fence shapes needed by the fixture; it is not a general Markdown parser.
    """
    count = 0
    in_html_comment = False
    fence: tuple[str, int] | None = None

    for raw_line in split_markdown_lines(text):
        if fence is not None:
            if markdown_fence_closing(raw_line, fence):
                fence = None
            continue

        if not in_html_comment:
            if raw_line == exact_line:
                count += 1
                continue
            opening = markdown_fence_opening(raw_line)
            if opening is not None:
                fence = opening
                continue

        position = 0
        while position < len(raw_line):
            if in_html_comment:
                end = raw_line.find("-->", position)
                if end == -1:
                    break
                in_html_comment = False
                position = end + 3
                continue
            start = raw_line.find("<!--", position)
            if start == -1:
                break
            in_html_comment = True
            position = start + 4
    return count


def _java_lexical_view(source: str) -> tuple[str, list[tuple[int, int]]]:
    """Mask bounded Java comments/literals while retaining source positions.

    This is deliberately not a Java parser. It only prevents literal type tokens from
    selecting a fixture declaration and returns the real comment spans needed here.
    """
    masked = list(source)
    comments: list[tuple[int, int]] = []

    def obscure(start: int, end: int) -> None:
        for position in range(start, end):
            if masked[position] != "\n":
                masked[position] = " "

    def unescaped_triple_quote(start: int) -> bool:
        backslashes = 0
        position = start - 1
        while position >= 0 and source[position] == "\\":
            backslashes += 1
            position -= 1
        return backslashes % 2 == 0

    def text_block_end(start: int) -> int:
        position = source.find('"""', start)
        while position != -1:
            if unescaped_triple_quote(position):
                return position + 3
            position = source.find('"""', position + 1)
        return len(source)

    index = 0
    while index < len(source):
        if source.startswith("//", index):
            end = source.find("\n", index)
            end = len(source) if end == -1 else end
            comments.append((index, end))
            obscure(index, end)
            index = end
        elif source.startswith("/*", index):
            closing = source.find("*/", index + 2)
            end = len(source) if closing == -1 else closing + 2
            comments.append((index, end))
            obscure(index, end)
            index = end
        elif source.startswith('"""', index):
            end = text_block_end(index + 3)
            obscure(index, end)
            index = end
        elif source[index] in {'"', "'"}:
            delimiter = source[index]
            end = index + 1
            while end < len(source):
                if source[end] == "\\":
                    end += 2
                elif source[end] == delimiter:
                    end += 1
                    break
                else:
                    end += 1
            obscure(index, min(end, len(source)))
            index = end
        else:
            index += 1
    return "".join(masked), comments


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SourceComprehensionError(f"{label} must be non-empty text")
    return value


def _identity_key(value: Any, label: str) -> str:
    """Return an alias-resistant key for one canonical evidence identity."""
    text = _text(value, label)
    if text != text.strip():
        raise SourceComprehensionError(f"{label} must be canonical non-empty text")
    if any(is_unsafe_evidence_character(character) for character in text):
        raise SourceComprehensionError(
            f"{label} must not contain unsafe Unicode evidence characters"
        )
    if any(is_synthetic_ignorable(character) for character in text):
        raise SourceComprehensionError(f"{label} must not contain synthetic Unicode ignorables")
    return nfkc_casefold(text)


def _relative_file(root: Path, value: Any, label: str) -> Path:
    text = _text(value, label)
    relative = Path(text)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise SourceComprehensionError(f"{label} must be a canonical relative path")
    path = root / relative
    # Before Python 3.14, is_symlink() raises for an over-long or unsearchable component.
    try:
        if path.is_symlink():
            raise SourceComprehensionError(f"{label} must not be a symlink")
        resolved = path.resolve(strict=True)
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise SourceComprehensionError(f"{label} must exist") from exc
    except OSError as exc:
        raise SourceComprehensionError(f"{label} cannot be checked: {exc.strerror}") from exc
    except RuntimeError as exc:  # Python 3.11 and 3.12 report a symlink loop this way.
        raise SourceComprehensionError(f"{label} cannot be checked: symlink loop") from exc
    try:
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise SourceComprehensionError(f"{label} escapes its case") from exc
    if not path.is_file():
        raise SourceComprehensionError(f"{label} must name a regular file")
    return path


def verify_case(case_root: Path) -> None:
    """Verify one declared fixture case; make no claim about arbitrary source."""
    try:
        root = case_root.resolve(strict=True)
    except RuntimeError as exc:  # Python 3.11 and 3.12 report a symlink loop this way.
        raise SourceComprehensionError(f"case path is a symlink loop: {case_root}") from exc
    record_path = _relative_file(root, "review-case.json", "case record")
    try:
        record = strict_json_loads(record_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateJsonKeyError) as exc:
        raise SourceComprehensionError(f"case record must be valid UTF-8 JSON: {exc}") from exc
    if not isinstance(record, dict) or set(record) != CASE_KEYS:
        raise SourceComprehensionError("case record keys differ from the fixture contract")
    if type(record["schema_version"]) is not int or record["schema_version"] != 1:
        raise SourceComprehensionError("schema_version must be integer 1")
    _text(record["purpose"], "purpose")
    if record["language_native_form"] != JAVA_NATIVE_FORM:
        raise SourceComprehensionError("fixture must declare the bounded Java-native form")
    classification = record["classification"]
    if classification not in {"SIMPLE", "CONSEQUENTIAL"}:
        raise SourceComprehensionError("classification must be SIMPLE or CONSEQUENTIAL")

    source_path = _relative_file(root, record["source_path"], "source_path")
    if source_path.suffix != ".java":
        raise SourceComprehensionError("fixture source_path must be Java")
    source = source_path.read_text(encoding="utf-8")
    if JAVA_UNICODE_ESCAPE_RE.search(source):
        raise SourceComprehensionError(
            "fixture source must not contain raw Java Unicode escape syntax"
        )
    code, comment_spans = _java_lexical_view(source)
    type_matches = [
        match for match in TYPE_RE.finditer(code) if _java_type_declaration_candidate(code, match)
    ]
    if len(type_matches) != 1:
        raise SourceComprehensionError(
            "fixture source must contain exactly one supported authored Java type declaration"
        )
    type_match = type_matches[0]

    orientation = _text(record["orientation_fragment"], "orientation_fragment")
    declaration_comment = next(
        (
            (start, orientation_end)
            for start, orientation_end in comment_spans
            if (
                orientation in source[start:orientation_end]
                and orientation_end <= type_match.start()
                and not any(
                    orientation_end <= comment_start < type_match.start()
                    for comment_start, _ in comment_spans
                )
                and JAVA_DECLARATION_GAP_RE.fullmatch(code[orientation_end : type_match.start()])
            )
        ),
        None,
    )
    if declaration_comment is None:
        raise SourceComprehensionError(
            "language-native orientation must immediately orient the authored type"
        )
    declaration_text = source[slice(*declaration_comment)]

    fragments = record["required_local_fragments"]
    if not isinstance(fragments, list) or any(
        not isinstance(item, str) or not item.strip() for item in fragments
    ):
        raise SourceComprehensionError("required_local_fragments must be a text list")
    if classification == "CONSEQUENTIAL" and not fragments:
        raise SourceComprehensionError("consequential source needs declared local rationale")
    for fragment in fragments:
        if fragment not in declaration_text:
            raise SourceComprehensionError(
                f"applicable local rationale is missing declared fragment: {fragment}"
            )

    anchor = record["exact_adr_anchor"]
    if anchor is not None:
        if not isinstance(anchor, dict) or set(anchor) != ADR_KEYS:
            raise SourceComprehensionError("exact_adr_anchor keys differ")
        source_fragment = _text(anchor["source_fragment"], "ADR source_fragment")
        if source_fragment not in declaration_text:
            raise SourceComprehensionError(
                "exact ADR anchor is missing from the declaration orientation"
            )
        document = _relative_file(root, anchor["document"], "ADR document")
        heading = anchor["heading"]
        if isinstance(heading, str) and any(
            is_unsafe_evidence_character(character) for character in heading
        ):
            raise SourceComprehensionError(
                "ADR heading must not contain unsafe Unicode evidence characters"
            )
        if not _is_canonical_atx_heading(heading):
            raise SourceComprehensionError("ADR heading must be a canonical one-line ATX heading")
        if _visible_raw_line_count(document.read_text(encoding="utf-8"), heading) != 1:
            raise SourceComprehensionError(
                "ADR heading target must appear exactly once as a visible raw line"
            )

    if record["changed_source_assessed"] is not True:
        raise SourceComprehensionError("changed-source assessment must be explicit")
    author = _identity_key(record["author"], "author")
    reviewer = _identity_key(record["reviewer"], "reviewer")
    if reviewer == author:
        raise SourceComprehensionError("changed source needs a non-author reviewer")
    if record["verdict"] != "CLEAN":
        raise SourceComprehensionError("accepted fixture verdict must be CLEAN")
    limitation = _text(record["limitation"], "limitation")
    if "not" not in limitation.lower() or "linter" not in limitation.lower():
        raise SourceComprehensionError("fixture must state its non-generalization limit")


def main(argv: list[str] | None = None) -> int:
    """Run the command line; return 0 on a pass and exit with status 1 on a failed case."""
    parser = argparse.ArgumentParser()
    parser.add_argument("case", type=Path)
    args = parser.parse_args(argv)
    try:
        verify_case(args.case)
    except (OSError, UnicodeDecodeError, SourceComprehensionError) as exc:
        parser.exit(1, f"FAIL: {exc}\n")
    print("PASS: bounded source-comprehension fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
