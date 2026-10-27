"""Render real Markdown Mermaid fences into local PNGs with editable collapsed source.

The optional maintainer command needs an existing ``mmdc`` executable. Rendering is
staged for the whole tree before publication, so a browser failure leaves authored
documents and their previous images intact. Run with ``python3 -B``.

Every diagram renders at its natural size (never shrunk to fit) and one fixed scale, and
its image is shown at that natural size, so text appears at Mermaid's normal size unless
the diagram is wider than a laptop-width Markdown column. Diagrams whose text would then
fall below a readable size are reported as UNREADABLE and need a narrower layout.
"""

import argparse
import contextlib
import hashlib
import html
import json
import math
import os
import re
import stat
import struct
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote

EXCLUDED = {
    ".git",
    ".acceptance-work",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}
BEGIN = "<!-- mermaid-render:begin sha256="
END = "<!-- mermaid-render:end -->"
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)$")
SCALE = 3  # device pixels per diagram pixel, fixed for every render
FONT_PX = 16  # Mermaid's default flowchart text size in diagram pixels
COLUMN_PX = 830  # widest Markdown image display on a laptop-width page
MIN_TEXT_PX = 12  # smallest readable body text at that display width
MAX_SHOWN_HEIGHT_PX = 1000  # taller than about one laptop screen: split at a phase boundary
MARKER = re.compile(re.escape(BEGIN) + r"([0-9a-f]{64}) -->\n")
ACC_TITLE = re.compile(r"^[ \t]*accTitle[ \t]*:[ \t]*(\S[^\r\n]*)$", re.MULTILINE)


class RenderError(Exception):
    """A malformed document or unsafe output must stop the entire render batch."""


@dataclass
class Diagram:
    """One Mermaid diagram found in a document, with its span and source."""

    start: int
    stop: int
    source: str
    owned: bool
    heading: str


def fenced_end(lines, start):
    """Honor the outer fence length so quoted example fences remain literal."""
    opening = FENCE.fullmatch(lines[start].rstrip("\r\n"))
    fence = opening[1]
    closing = re.compile(r"^ {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*$")
    for index in range(start + 1, len(lines)):
        if closing.fullmatch(lines[index].rstrip("\r\n")):
            return index + 1
    raise RenderError("unclosed Markdown fence")


def collapsed(source):
    """Return the source wrapped in a collapsed details block."""
    runs = [len(run) for run in re.findall(r"`+", source)]
    fence = "`" * max(3, max(runs, default=0) + 1)
    return (
        "<details><summary>Mermaid source</summary>\n\n"
        + fence
        + "mermaid\n"
        + source
        + fence
        + "\n\n</details>\n"
    )


def digest(source):
    """Return the digest of a source together with the render policy."""
    # Include rendering policy: changing it invalidates --check receipts.
    policy = (
        "png;dark;background=#0d0d0d;scale="
        + str(SCALE)
        + ";natural-size;img-width;"
        + "readable="
        + str(FONT_PX)
        + ","
        + str(COLUMN_PX)
        + ","
        + str(MIN_TEXT_PX)
        + ";v3\n"
    )
    return hashlib.sha256((policy + source).encode("utf-8")).hexdigest()


def wrapper(source, relative_image, alt, width):
    """Return the image-and-source wrapper for one diagram."""
    # Percent-encoding keeps stems with spaces or parentheses a valid link; the width
    # attribute shows the image at its natural size, capped at the Markdown column,
    # instead of SCALE times larger.
    return (
        BEGIN
        + digest(source)
        + ' -->\n<img src="'
        + quote(relative_image)
        + '" alt="'
        + html.escape(alt, quote=True)
        + '" width="'
        + str(width)
        + '">\n\n'
        + collapsed(source)
        + END
        + "\n"
    )


def unwrap(region):
    """Only our exact wrapper shape confers ownership of an existing PNG."""
    marker = MARKER.match(region)
    if not marker or not region.endswith(END + "\n"):
        raise RenderError("malformed Mermaid render region")
    body = region[marker.end() : -len(END + "\n")]
    match = re.fullmatch(
        r'<img src="(mermaid/[^"\s()]+\.png)" alt="[^"\n]*" '
        r'width="[1-9][0-9]*">\n\n(.*)',
        body,
        re.DOTALL,
    )
    if not match:
        raise RenderError("malformed Mermaid image/source wrapper")
    detail = match[2]
    prefix = "<details><summary>Mermaid source</summary>\n\n"
    suffix = "\n</details>\n"
    if not detail.startswith(prefix) or not detail.endswith(suffix):
        raise RenderError("malformed collapsed Mermaid source")
    inner = detail[len(prefix) : -len(suffix)].splitlines(keepends=True)
    if not inner or not FENCE.fullmatch(inner[0].rstrip("\r\n")):
        raise RenderError("missing Mermaid source fence")
    opening = FENCE.fullmatch(inner[0].rstrip("\r\n"))
    if opening[2].strip() != "mermaid" or fenced_end(inner, 0) != len(inner):
        raise RenderError("mismatched Mermaid source fence")
    source = "".join(inner[1:-1])
    if collapsed(source) != detail:
        raise RenderError("noncanonical collapsed Mermaid source")
    return source, unquote(match[1]), marker[1]


def diagrams(text, fallback):
    """Return replacement spans without interpreting code nested inside fences."""
    lines = text.splitlines(keepends=True)
    result = []
    heading = fallback
    offset = index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith(BEGIN):
            stop = index + 1
            while stop < len(lines) and lines[stop].rstrip("\r\n") != END:
                if lines[stop].startswith(BEGIN):
                    raise RenderError("nested Mermaid render regions")
                stop += 1
            if stop == len(lines):
                raise RenderError("unclosed Mermaid render region")
            region = "".join(lines[index : stop + 1])
            source, _, _ = unwrap(region)
            length = len(region)
            result.append(Diagram(offset, offset + length, source, True, heading))
            index = stop + 1
        elif line.rstrip("\r\n") == END:
            raise RenderError("orphan Mermaid render region end")
        elif FENCE.fullmatch(line.rstrip("\r\n")):
            opening = FENCE.fullmatch(line.rstrip("\r\n"))
            stop = fenced_end(lines, index)
            length = len("".join(lines[index:stop]))
            if opening[2].strip() == "mermaid":
                source = "".join(lines[index + 1 : stop - 1])
                result.append(Diagram(offset, offset + length, source, False, heading))
            index = stop
        else:
            if re.match(r"^#{1,6}\s+", line):
                heading = re.sub(r"^#{1,6}\s+", "", line).strip().rstrip("#").strip()
            length = len(line)
            index += 1
        offset += length
    return result


def markdown_files(root):
    """Yield the Markdown files under the root, skipping excluded and linked folders.

    A directory that cannot be listed raises its error, so a check never passes over
    Markdown it could not see. A Markdown name that is not a regular file is refused
    before anything opens it: reading a FIFO or device would block or never end.
    """

    def unlisted(error):
        raise error

    for directory, dirs, files in os.walk(root, onerror=unlisted, followlinks=False):
        dirs[:] = sorted(
            name
            for name in dirs
            if name not in EXCLUDED and not (Path(directory) / name).is_symlink()
        )
        for name in sorted(files):
            path = Path(directory) / name
            if path.suffix.lower() != ".md":
                continue
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                continue
            if not stat.S_ISREG(mode):
                raise RenderError("not a regular file: " + str(path))
            yield path


def png_width(path):
    """Return a PNG's pixel width, refusing anything that is not a PNG."""
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:16] != b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR":
        raise RenderError("renderer did not produce a PNG")
    width, height = struct.unpack(">II", header[16:24])
    if not width or not height:
        raise RenderError("renderer produced an empty PNG")
    return width


def natural_width(path):
    """Return the image width in CSS pixels at the render scale."""
    return math.ceil(png_width(path) / SCALE)


def png_height(path):
    """Return a PNG's pixel height."""
    png_width(path)
    return struct.unpack(">I", path.read_bytes()[20:24])[0]


def shown_height_px(path):
    """Return the displayed height in CSS pixels after the width attribute and column fit."""
    width = png_width(path) / SCALE
    return png_height(path) / SCALE * min(width, COLUMN_PX) / width


def displayed_text_px(path):
    """Body-text height in CSS pixels once the image is fitted to the Markdown column."""
    width = png_width(path) / SCALE
    return FONT_PX * min(width, COLUMN_PX) / width


def render(source, target, work, renderer, puppeteer_config):
    """Render one source to a PNG with the pinned theme and scale."""
    input_path = work / "source.mmd"
    input_path.write_text(source, encoding="utf-8")
    # Natural size: Mermaid otherwise shrinks wide diagrams, and their text, to fit.
    config_path = work / "mermaid-config.json"
    config_path.write_text(
        json.dumps(
            {
                kind: {"useMaxWidth": False}
                for kind in (
                    "flowchart",
                    "sequence",
                    "class",
                    "state",
                    "er",
                    "gantt",
                    "journey",
                    "pie",
                )
            }
        ),
        encoding="utf-8",
    )
    command = [
        renderer,
        "-i",
        str(input_path),
        "-o",
        str(target),
        "-t",
        "dark",
        "-b",
        "#0d0d0d",
        "-c",
        str(config_path),
    ]
    if puppeteer_config:
        command += ["-p", str(puppeteer_config)]
    try:
        subprocess.run(command + ["-s", str(SCALE)], check=True, capture_output=True, text=True)
        png_width(target)
    except (OSError, subprocess.CalledProcessError) as error:
        # Browser diagnostics may contain machine paths; keep shipped diagnostics local.
        raise RenderError("Mermaid renderer failed; no documents published") from error


def publish(changes):
    """Atomic replacements plus rollback protect prior bytes on publication errors."""
    originals = {path: path.read_bytes() if path.exists() else None for path in changes}
    installed = []
    try:
        for path, content in changes.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(content)
            try:
                # Replacement must not turn ordinary documents into private temp files.
                mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
                temporary.chmod(mode)
                os.replace(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)
            installed.append(path)
    except OSError:
        for path in reversed(installed):
            if originals[path] is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(originals[path])
        raise


def process(
    root,
    *,
    check=False,
    renderer="mmdc",
    puppeteer_config=None,
    rendered=None,
    unreadable=None,
    tall=None,
):
    """Check or generate a whole batch; no output is published until all render.

    In generate mode, ``rendered`` (a list) receives each diagram actually rendered.
    ``unreadable`` (a list) receives each diagram whose image text would display below
    ``MIN_TEXT_PX``; the image is still published so its author can inspect it.
    ``tall`` (a list) receives each diagram shown taller than ``MAX_SHOWN_HEIGHT_PX``; it is
    a warning only.
    """
    try:
        root = Path(root).resolve()
    except RuntimeError as error:
        # Python 3.11 and 3.12 report a symlink loop here as RuntimeError, later ones as OSError.
        raise RenderError(str(error)) from error
    changes = {}
    stale = []
    count = 0
    # --check writes nothing, not even scratch space; only generation stages renders.
    staging = (
        contextlib.nullcontext() if check else tempfile.TemporaryDirectory(prefix="mermaid-docs-")
    )
    with staging as temporary:
        work = Path(temporary) if temporary else None
        for document in markdown_files(root):
            original = document.read_bytes()
            text = original.decode("utf-8")
            pieces = []
            previous = 0
            for number, diagram in enumerate(diagrams(text, document.stem), 1):
                count += 1
                relative = "mermaid/" + document.stem + "-" + str(number) + ".png"
                image = document.parent / relative
                if image.parent.is_symlink() or image.is_symlink():
                    raise RenderError("diagram output cannot be a symlink")
                current = False
                if diagram.owned:
                    _, owned_path, owned_digest = unwrap(text[diagram.start : diagram.stop])
                    if owned_path != relative:
                        raise RenderError(
                            "diagram numbering changed; resolve owned image paths first"
                        )
                    # Same source and policy: only wrapper text (such as alt) may change.
                    current = owned_digest == digest(diagram.source) and image.is_file()
                elif image.exists():
                    raise RenderError(
                        "unowned diagram image already exists: " + str(image.relative_to(root))
                    )
                # Mermaid's own accessible title, when present, is the most specific alt text.
                title = ACC_TITLE.search(diagram.source)
                label = title[1].strip() if title else diagram.heading + " diagram " + str(number)
                alt = re.sub(r"[\[\]\\`*_]", "", label)
                shown = image
                if not check and not current:
                    shown = work / (str(count) + ".png")
                    render(diagram.source, shown, work, renderer, puppeteer_config)
                    changes[image] = shown.read_bytes()
                    if rendered is not None:
                        rendered.append(
                            str(document.relative_to(root)) + ": diagram " + str(number)
                        )
                natural = natural_width(shown) if shown.is_file() else 0
                replacement = wrapper(diagram.source, relative, alt, min(natural, COLUMN_PX))
                if text[diagram.start : diagram.stop] != replacement or not image.is_file():
                    stale.append(str(document.relative_to(root)) + ": diagram " + str(number))
                if unreadable is not None and shown.is_file():
                    text_px = displayed_text_px(shown)
                    if text_px < MIN_TEXT_PX:
                        unreadable.append(
                            str(document.relative_to(root))
                            + ": diagram "
                            + str(number)
                            + " (text about "
                            + format(text_px, ".1f")
                            + " px at "
                            + str(COLUMN_PX)
                            + " px; "
                            + str(natural)
                            + " px natural width)"
                        )
                if tall is not None and shown.is_file():
                    height = shown_height_px(shown)
                    if height > MAX_SHOWN_HEIGHT_PX:
                        tall.append(
                            str(document.relative_to(root))
                            + ": diagram "
                            + str(number)
                            + " (shown about "
                            + str(round(height))
                            + " px tall)"
                        )
                pieces.extend((text[previous : diagram.start], replacement))
                previous = diagram.stop
            if previous:
                pieces.append(text[previous:])
                updated = "".join(pieces).encode("utf-8")
                if updated != original:
                    changes[document] = updated
        if check:
            return count, stale
        publish(changes)
    return count, []


def main(argv=None):
    """Run the command line and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--check", action="store_true", help="check wrappers/digests/images without writing"
    )
    parser.add_argument(
        "--puppeteer-config", type=Path, help="local browser configuration for installed mmdc"
    )
    args = parser.parse_args(argv)
    rendered, unreadable, tall = [], [], []
    try:
        count, stale = process(
            args.root,
            check=args.check,
            puppeteer_config=args.puppeteer_config,
            rendered=rendered,
            unreadable=unreadable,
            tall=tall,
        )
    except (RenderError, OSError, UnicodeError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 2
    for item in stale:
        print("STALE: " + item)
    for item in unreadable:
        print("UNREADABLE: " + item)
    for item in tall:
        print("WARNING: tall diagram, consider splitting: " + item)
    summary = str(count) + " Mermaid diagrams checked"
    if not args.check:
        summary += ", " + str(len(rendered)) + " rendered"
    print(summary)
    return 1 if stale or unreadable else 0


if __name__ == "__main__":
    raise SystemExit(main())
