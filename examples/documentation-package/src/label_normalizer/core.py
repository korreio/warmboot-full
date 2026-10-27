"""Own the pure, destructive comparison-key normalization policy."""

import unicodedata


def normalize_label(value: str) -> str:
    """Return a Unicode-aware comparison key, not preserved display text.

    Compatibility forms are normalized first because NFKC can change characters that
    later participate in whitespace/case handling; splitting earlier could miss them.
    Runs of Unicode whitespace then collapse to one ASCII space before Unicode-aware
    case folding. Punctuation and word order are otherwise retained. Cross-cutting
    rationale: ``docs/adr/0001-python-standard-library-core.md#normalization-order``.
    """

    if not isinstance(value, str):
        raise TypeError("value must be str")

    compatible = unicodedata.normalize("NFKC", value)
    return " ".join(compatible.split()).casefold()
