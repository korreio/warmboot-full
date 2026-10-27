"""Decode bounded acceptance JSON without silently replacing duplicate object keys."""

from __future__ import annotations

import json
from typing import Any


class DuplicateJsonKeyError(ValueError):
    """Raised when any object in an acceptance JSON document repeats a key."""


def loads(document: str | bytes | bytearray) -> Any:
    """Decode JSON text or raw bytes while rejecting duplicate keys recursively.

    Nesting deeper than the decoder's stack and integers longer than the interpreter's
    digit limit raise ``json.JSONDecodeError``, which every caller already reports.
    """

    def object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise DuplicateJsonKeyError(f"duplicate JSON object key: {key}")
            result[key] = value
        return result

    try:
        return json.loads(document, object_pairs_hook=object_without_duplicate_keys)
    except (json.JSONDecodeError, DuplicateJsonKeyError, UnicodeDecodeError):
        raise
    except RecursionError:
        raise json.JSONDecodeError("JSON nesting exceeds the decoder depth limit", "", 0) from None
    except ValueError as exc:
        raise json.JSONDecodeError(f"JSON value exceeds a decoder limit: {exc}", "", 0) from None
