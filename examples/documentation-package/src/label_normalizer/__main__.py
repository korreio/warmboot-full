"""Command-line adapter for label comparison-key normalization."""

import argparse
from collections.abc import Sequence

from .core import normalize_label


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser without performing process I/O."""

    parser = argparse.ArgumentParser(
        prog="label-normalize",
        description=(
            "Convert labels to comparison keys. Keep original display text; "
            "normalization is intentionally destructive."
        ),
    )
    parser.add_argument("labels", nargs="+", help="one or more labels to normalize")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Print one normalized comparison key per argument."""

    args = build_parser().parse_args(argv)
    for label in args.labels:
        print(normalize_label(label))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
