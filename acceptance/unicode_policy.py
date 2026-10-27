"""Shared Unicode normalization and evidence-ingress policy for acceptance data.

The explicit Default_Ignorable_Code_Point ranges keep the designed collision set
stable across Python Unicode database revisions. Runtime ``Cf`` is unioned in so
newly assigned formatting controls still fail closed; ordinary combining marks do not.
Separately, unsafe ``Cc``, ``Cs``, ``Co``, and ``Cn`` code points are rejected at
evidence ingress rather than interpreted through normalization.
Markdown line parsing recognizes only CommonMark CR/LF endings so Python-only Unicode
line separators remain literal evidence content.
"""

from __future__ import annotations

import unicodedata
from bisect import bisect_right

# Unicode DerivedCoreProperties.txt Default_Ignorable_Code_Point ranges. The table
# deliberately expands to 4,174 code points; runtime category Cf is a separate union.
# Consolidated Unicode data; Unicode-3.0 terms are retained in root NOTICE.
DEFAULT_IGNORABLE_CODE_POINT_RANGES: tuple[tuple[int, int], ...] = (
    (0x00AD, 0x00AD),
    (0x034F, 0x034F),
    (0x061C, 0x061C),
    (0x115F, 0x1160),
    (0x17B4, 0x17B5),
    (0x180B, 0x180F),
    (0x200B, 0x200F),
    (0x202A, 0x202E),
    (0x2060, 0x206F),
    (0x3164, 0x3164),
    (0xFE00, 0xFE0F),
    (0xFEFF, 0xFEFF),
    (0xFFA0, 0xFFA0),
    (0xFFF0, 0xFFF8),
    (0x1BCA0, 0x1BCA3),
    (0x1D173, 0x1D17A),
    (0xE0000, 0xE0FFF),
)
_DEFAULT_IGNORABLE_STARTS = tuple(start for start, _ in DEFAULT_IGNORABLE_CODE_POINT_RANGES)
# Python treats these as line boundaries, but CommonMark does not. Markdown parsing
# must retain them as ordinary content instead of delegating to ``str.splitlines``.
NON_MARKDOWN_LINE_SEPARATORS = (
    ("VT", "\x0b"),
    ("FF", "\x0c"),
    ("FS", "\x1c"),
    ("GS", "\x1d"),
    ("RS", "\x1e"),
    ("NEL", "\x85"),
    ("LINE SEPARATOR", "\u2028"),
    ("PARAGRAPH SEPARATOR", "\u2029"),
)


def split_markdown_lines(value: str) -> list[str]:
    """Split CommonMark lines on LF, CRLF, or CR and retain every other separator."""
    if not value:
        return []
    lines = value.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if lines[-1] == "":
        lines.pop()
    return lines


def markdown_fence_opening(line: str) -> tuple[str, int] | None:
    """Return a bounded CommonMark fence marker and its maximal opening run."""
    indent = 0
    while indent < len(line) and line[indent] == " ":
        indent += 1
    if indent > 3 or indent == len(line) or line[indent] not in {"`", "~"}:
        return None

    character = line[indent]
    end = indent
    while end < len(line) and line[end] == character:
        end += 1
    length = end - indent
    if length < 3:
        return None
    if character == "`" and "`" in line[end:]:
        return None
    return character, length


def markdown_fence_closing(line: str, opening: tuple[str, int]) -> bool:
    """Return whether a raw line closes one bounded CommonMark fence opening."""
    character, minimum = opening
    indent = 0
    while indent < len(line) and line[indent] == " ":
        indent += 1
    if indent > 3:
        return False

    end = indent
    while end < len(line) and line[end] == character:
        end += 1
    return end - indent >= minimum and all(remainder in {" ", "\t"} for remainder in line[end:])


def visible_markdown_lines(value: str) -> list[str]:
    """Return raw lines visible outside bounded HTML comments and fenced code blocks.

    Uses the same raw-fence-before-comment ordering as the safety-block reader: a
    fenced code block hides every line between its opening and closing markers, and a
    bounded ``<!-- -->`` comment hides every line whose start falls inside it. Callers
    apply their own line matching to the returned visible lines only; this is not a
    general Markdown parser and recognizes only these two bounded shapes.
    """
    visible: list[str] = []
    in_html_comment = False
    fence: tuple[str, int] | None = None

    for raw_line in split_markdown_lines(value):
        if fence is not None:
            if markdown_fence_closing(raw_line, fence):
                fence = None
            continue

        if not in_html_comment:
            opening = markdown_fence_opening(raw_line)
            if opening is not None:
                fence = opening
                continue
            visible.append(raw_line)

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

    return visible


def split_markdown_table_cells(line: str) -> list[str]:
    """Split a row after removing at most one optional outer pipe on each side."""
    row = line.strip(" \t")
    row = row.removeprefix("|")
    row = row.removesuffix("|")
    return [cell.strip(" \t") for cell in row.split("|")]


def is_default_ignorable_code_point(character: str) -> bool:
    """Return whether one character belongs to the explicit designed range table."""
    if not isinstance(character, str) or len(character) != 1:
        raise ValueError("Unicode policy predicates require exactly one character")
    codepoint = ord(character)
    index = bisect_right(_DEFAULT_IGNORABLE_STARTS, codepoint) - 1
    return index >= 0 and codepoint <= DEFAULT_IGNORABLE_CODE_POINT_RANGES[index][1]


def is_synthetic_ignorable(character: str) -> bool:
    """Union designed default-ignorables with the runtime's formatting controls."""
    return is_default_ignorable_code_point(character) or unicodedata.category(character) == "Cf"


def is_unsafe_evidence_character(character: str) -> bool:
    """Return whether a one-character string is unsafe as literal acceptance evidence.

    Formatting controls remain in the synthetic-ignorable policy so emoji ZWJ
    materiality keeps its designed interpretations. Other Unicode ``C`` categories
    fail closed instead of becoming invisible or environment-specific evidence.
    """
    if not isinstance(character, str) or len(character) != 1:
        raise ValueError("Unicode policy predicates require exactly one character")
    return unicodedata.category(character) in {"Cc", "Cs", "Co", "Cn"}


def nfkc_casefold(value: str) -> str:
    """Apply the double-NFKC case-fold form used for evidence collision keys."""
    return unicodedata.normalize("NFKC", unicodedata.normalize("NFKC", value).casefold())


def replace_synthetic_ignorables(value: str, replacement: str) -> str:
    """Replace every designed/runtime ignorable without interpreting its position."""
    return "".join(
        replacement if is_synthetic_ignorable(character) else character for character in value
    )
