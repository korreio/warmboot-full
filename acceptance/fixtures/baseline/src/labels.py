"""Testable source used by the deterministic warm-boot acceptance fixture."""


def normalize_label(value: str) -> str:
    """Collapse whitespace and normalize case without changing word order."""

    return " ".join(value.split()).casefold()
