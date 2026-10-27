"""Exercise local diagram ownership and batch safety without launching a browser."""

import importlib.util
import io
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Load by path so the suite runs from any working directory without a package.
HELPER = Path(__file__).resolve().parents[1] / "tools" / "render_mermaid_docs.py"
SPEC = importlib.util.spec_from_file_location("render_mermaid_docs", HELPER)
rendering = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rendering)


SOURCE = "flowchart LR\n    Start --> Finish\n"


def png(width=900, height=300):
    # Only the IHDR fields are needed by the renderer's dimension reader.
    return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + struct.pack(">II", width, height)


class MermaidDocsTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.document = self.root / "guide.md"
        self.original = "# Guide\n\n## Task flow\n\n```mermaid\n" + SOURCE + "```\n"
        self.document.write_text(self.original, encoding="utf-8")

    def render_stub(self, command, **kwargs):
        self.assertTrue(kwargs["check"])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(command[command.index("-t") + 1], "dark")
        self.assertEqual(command[command.index("-b") + 1], "#0d0d0d")
        target = Path(command[command.index("-o") + 1])
        target.write_bytes(png())
        return subprocess.CompletedProcess(command, 0)

    def generate(self):
        with patch.object(rendering.subprocess, "run", side_effect=self.render_stub):
            return rendering.process(self.root)

    def test_nested_literal_mermaid_and_excluded_tree_are_ignored(self):
        literal = "# Literal example\n\n````markdown\n```mermaid\ninvalid\n```\n````\n"
        self.document.write_text(literal, encoding="utf-8")
        ignored = self.root / "node_modules"
        ignored.mkdir()
        (ignored / "nested.md").write_text(self.original, encoding="utf-8")
        with patch.object(rendering.subprocess, "run") as renderer:
            self.assertEqual(rendering.process(self.root), (0, []))
        renderer.assert_not_called()
        self.assertEqual(self.document.read_text(encoding="utf-8"), literal)

    def test_render_has_local_image_meaningful_alt_and_exact_editable_source(self):
        self.assertEqual(self.generate(), (1, []))
        result = self.document.read_text(encoding="utf-8")
        self.assertIn(
            '<img src="mermaid/guide-1.png" alt="Task flow diagram 1" width="300">', result
        )
        self.assertIn("<details><summary>Mermaid source</summary>", result)
        self.assertIn("```mermaid\n" + SOURCE + "```", result)
        self.assertEqual((self.root / "mermaid" / "guide-1.png").read_bytes(), png())
        self.assertEqual(rendering.process(self.root, check=True), (1, []))
        self.generate()
        self.assertEqual(self.document.read_text(encoding="utf-8"), result)

    def test_check_detects_original_changed_source_and_missing_png_without_mutation(self):
        before = self.document.read_bytes()
        count, stale = rendering.process(self.root, check=True)
        self.assertEqual(count, 1)
        self.assertEqual(stale, ["guide.md: diagram 1"])
        self.assertEqual(self.document.read_bytes(), before)
        self.assertFalse((self.root / "mermaid").exists())
        self.generate()
        wrapped = self.document.read_text(encoding="utf-8")
        changed = wrapped.replace("Start --> Finish", "Start --> Review")
        self.document.write_text(changed, encoding="utf-8")
        self.assertEqual(rendering.process(self.root, check=True)[1], stale)
        self.assertEqual(self.document.read_text(encoding="utf-8"), changed)
        self.document.write_text(wrapped, encoding="utf-8")
        (self.root / "mermaid" / "guide-1.png").unlink()
        self.assertEqual(rendering.process(self.root, check=True)[1], stale)

    def test_any_render_failure_preserves_all_prior_document_and_image_bytes(self):
        self.generate()
        prior_document = self.document.read_bytes()
        image = self.root / "mermaid" / "guide-1.png"
        prior_image = image.read_bytes()
        second = self.root / "second.md"
        second.write_text(self.original, encoding="utf-8")

        def fail_second(command, **kwargs):
            if Path(command[command.index("-o") + 1]).name == "2.png":
                raise subprocess.CalledProcessError(1, command)
            return self.render_stub(command, **kwargs)

        with patch.object(rendering.subprocess, "run", side_effect=fail_second):
            with self.assertRaisesRegex(rendering.RenderError, "renderer failed"):
                rendering.process(self.root)
        self.assertEqual(self.document.read_bytes(), prior_document)
        self.assertEqual(image.read_bytes(), prior_image)
        self.assertEqual(second.read_text(encoding="utf-8"), self.original)
        self.assertFalse((self.root / "mermaid" / "second-1.png").exists())

    def test_heading_rename_rewrites_wrapper_without_rendering_current_image(self):
        self.generate()
        image = self.root / "mermaid" / "guide-1.png"
        prior_image = image.read_bytes()
        renamed = self.document.read_text(encoding="utf-8").replace("## Task flow", "## Work flow")
        self.document.write_text(renamed, encoding="utf-8")
        self.assertEqual(rendering.process(self.root, check=True)[1], ["guide.md: diagram 1"])
        with (
            patch.object(rendering.subprocess, "run") as renderer,
            patch("sys.stdout", new_callable=io.StringIO) as output,
        ):
            self.assertEqual(rendering.main(["--root", str(self.root)]), 0)
        renderer.assert_not_called()
        self.assertEqual(output.getvalue(), "1 Mermaid diagrams checked, 0 rendered\n")
        self.assertIn(
            '<img src="mermaid/guide-1.png" alt="Work flow diagram 1" width="300">',
            self.document.read_text(encoding="utf-8"),
        )
        self.assertEqual(image.read_bytes(), prior_image)
        self.assertEqual(rendering.process(self.root, check=True), (1, []))

    def test_accessible_title_overrides_heading_alt_text(self):
        titled = self.original.replace(
            "flowchart LR\n", "flowchart LR\n    accTitle: Start [then] finish\n"
        )
        self.document.write_text(titled, encoding="utf-8")
        self.assertEqual(self.generate(), (1, []))
        self.assertIn(
            '<img src="mermaid/guide-1.png" alt="Start then finish" width="300">',
            self.document.read_text(encoding="utf-8"),
        )
        self.assertEqual(rendering.process(self.root, check=True), (1, []))

    def test_check_allocates_no_temporary_directory(self):
        self.generate()
        with (
            patch.object(rendering.tempfile, "TemporaryDirectory") as temporary,
            patch("sys.stdout", new_callable=io.StringIO) as output,
        ):
            self.assertEqual(rendering.process(self.root, check=True), (1, []))
            self.assertEqual(rendering.main(["--root", str(self.root), "--check"]), 0)
        temporary.assert_not_called()
        self.assertEqual(output.getvalue(), "1 Mermaid diagrams checked\n")

    def test_missing_image_is_rendered_again_with_unchanged_source(self):
        self.generate()
        image = self.root / "mermaid" / "guide-1.png"
        image.unlink()
        rendered = []
        with patch.object(rendering.subprocess, "run", side_effect=self.render_stub):
            self.assertEqual(rendering.process(self.root, rendered=rendered), (1, []))
        self.assertEqual(rendered, ["guide.md: diagram 1"])
        self.assertTrue(image.is_file())
        self.assertEqual(rendering.process(self.root, check=True), (1, []))

    def test_editing_one_fence_renders_only_that_diagram(self):
        self.document.write_text(
            self.original + "\n## Second flow\n\n```mermaid\n" + SOURCE + "```\n", encoding="utf-8"
        )
        self.assertEqual(self.generate(), (2, []))
        first = self.root / "mermaid" / "guide-1.png"
        first.write_bytes(png(width=901))
        edited = self.document.read_text(encoding="utf-8")
        head, tail = edited.split("## Second flow")
        self.document.write_text(
            head + "## Second flow" + tail.replace("Start --> Finish", "Start --> Review"),
            encoding="utf-8",
        )
        targets = []

        def record(command, **kwargs):
            targets.append(command[command.index("-o") + 1])
            return self.render_stub(command, **kwargs)

        rendered = []
        with patch.object(rendering.subprocess, "run", side_effect=record):
            self.assertEqual(rendering.process(self.root, rendered=rendered), (2, []))
        self.assertEqual([Path(target).name for target in targets], ["2.png"])
        self.assertEqual(rendered, ["guide.md: diagram 2"])
        self.assertEqual(first.read_bytes(), png(width=901))
        self.assertEqual(rendering.process(self.root, check=True), (2, []))

    def test_document_names_with_spaces_and_parentheses_keep_valid_image_links(self):
        self.document.unlink()
        self.document = self.root / "release notes (draft).md"
        self.document.write_text(self.original, encoding="utf-8")
        self.assertEqual(self.generate(), (1, []))
        result = self.document.read_text(encoding="utf-8")
        self.assertIn('src="mermaid/release%20notes%20%28draft%29-1.png"', result)
        self.assertTrue((self.root / "mermaid" / "release notes (draft)-1.png").is_file())
        self.assertEqual(rendering.process(self.root, check=True), (1, []))

    def test_unowned_or_symlink_output_is_never_overwritten(self):
        directory = self.root / "mermaid"
        directory.mkdir()
        image = directory / "guide-1.png"
        image.write_bytes(b"authored image")
        with self.assertRaisesRegex(rendering.RenderError, "unowned"):
            self.generate()
        self.assertEqual(image.read_bytes(), b"authored image")
        image.unlink()
        image.symlink_to(self.document)
        with self.assertRaisesRegex(rendering.RenderError, "symlink"):
            self.generate()
        self.assertEqual(self.document.read_text(encoding="utf-8"), self.original)

    def test_malformed_fences_and_owned_wrappers_fail_without_rewriting(self):
        cases = ["```mermaid\nflowchart LR\n", rendering.END + "\n"]
        self.generate()
        valid = self.document.read_text(encoding="utf-8")
        cases.extend(
            (
                valid.replace("</details>", "</summary>"),
                valid.replace(rendering.END, ""),
                valid.replace("```\n\n</details>", "~~~\n\n</details>"),
            )
        )
        for malformed in cases:
            with self.subTest(content=malformed):
                self.document.write_text(malformed, encoding="utf-8")
                with self.assertRaises(rendering.RenderError):
                    rendering.process(self.root, check=True)
                self.assertEqual(self.document.read_text(encoding="utf-8"), malformed)

    def test_every_render_uses_the_fixed_scale_and_local_browser_config(self):
        commands = []
        config = self.root / "browser.json"
        config.write_text("{}", encoding="utf-8")

        def wide(command, **kwargs):
            commands.append(command)
            target = Path(command[command.index("-o") + 1])
            target.write_bytes(png(width=2500))
            return subprocess.CompletedProcess(command, 0)

        with patch.object(rendering.subprocess, "run", side_effect=wide):
            rendering.process(self.root, puppeteer_config=config)
        self.assertEqual([command[-1] for command in commands], [str(rendering.SCALE)])
        # Natural size: Mermaid must not shrink a wide diagram's text to fit its viewport.
        self.assertTrue(all("-c" in command for command in commands))
        self.assertTrue(
            all(command[command.index("-p") + 1] == str(config) for command in commands)
        )

    def test_tall_images_warn_without_failing(self):
        def tall_png(command, **kwargs):
            # 900 x 3003 device px is 300 x 1001 px natural: shown 1001 px tall at full size.
            Path(command[command.index("-o") + 1]).write_bytes(png(width=900, height=3003))
            return subprocess.CompletedProcess(command, 0)

        with patch.object(rendering.subprocess, "run", side_effect=tall_png):
            rendering.process(self.root)
        tall = []
        self.assertEqual(rendering.process(self.root, check=True, tall=tall), (1, []))
        self.assertEqual(tall, ["guide.md: diagram 1 (shown about 1001 px tall)"])
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            status = rendering.main(["--root", str(self.root), "--check"])
        self.assertEqual(status, 0)
        self.assertIn(
            "WARNING: tall diagram, consider splitting: guide.md: diagram 1", output.getvalue()
        )

    def test_too_wide_images_are_reported_unreadable_in_both_modes(self):
        limit = rendering.FONT_PX * rendering.SCALE * rendering.COLUMN_PX // rendering.MIN_TEXT_PX
        for width, readable in ((limit, True), (limit + 1, False)):
            with self.subTest(width=width):

                def sized(command, *, size=width, **kwargs):
                    Path(command[command.index("-o") + 1]).write_bytes(png(width=size))
                    return subprocess.CompletedProcess(command, 0)

                for image in (self.root / "mermaid").glob("*.png"):
                    image.unlink()
                self.document.write_text(self.original, encoding="utf-8")
                generated = []
                with patch.object(rendering.subprocess, "run", side_effect=sized):
                    rendering.process(self.root, unreadable=generated)
                checked = []
                self.assertEqual(
                    rendering.process(self.root, check=True, unreadable=checked), (1, [])
                )
                expected = (
                    []
                    if readable
                    else [
                        "guide.md: diagram 1 (text about 12.0 px at 830 px; "
                        + str(-(-width // rendering.SCALE))
                        + " px natural width)"
                    ]
                )
                self.assertEqual(generated, expected)
                self.assertEqual(checked, expected)
                self.assertIn(
                    'width="' + str(rendering.COLUMN_PX) + '">',
                    self.document.read_text(encoding="utf-8"),
                )
                with patch("sys.stdout", new_callable=io.StringIO) as output:
                    status = rendering.main(["--root", str(self.root), "--check"])
                self.assertEqual(status, 0 if readable else 1)
                self.assertEqual("UNREADABLE: " in output.getvalue(), not readable)

    @unittest.skipIf(os.geteuid() == 0, "root can list a mode-000 directory")
    def test_check_fails_closed_on_a_directory_it_cannot_list(self):
        locked = self.root / "locked"
        locked.mkdir()
        (locked / "hidden.md").write_text(self.original, encoding="utf-8")
        locked.chmod(0)
        self.addCleanup(locked.chmod, 0o700)
        with patch("sys.stderr", new_callable=io.StringIO) as errors:
            status = rendering.main(["--root", str(self.root), "--check"])
        self.assertEqual(status, 2)
        self.assertIn(str(self.root.resolve() / "locked"), errors.getvalue())

    @unittest.skipUnless(hasattr(os, "mkfifo"), "needs FIFO support")
    def test_check_refuses_a_markdown_name_that_is_not_a_regular_file(self):
        self.document.unlink()
        stream = self.root / "stream.md"
        os.mkfifo(stream)
        # A separate process with a deadline: reading the FIFO would block forever.
        result = subprocess.run(
            [sys.executable, "-B", str(HELPER), "--root", str(self.root), "--check"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(
            "not a regular file: " + str(self.root.resolve() / "stream.md"), result.stderr
        )
        stream.unlink()
        stream.write_bytes(b"")
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            status = rendering.main(["--root", str(self.root), "--check"])
        self.assertEqual(status, 0)
        self.assertIn("0 Mermaid diagrams checked", output.getvalue())

    def test_a_symlink_loop_as_root_is_a_controlled_error(self):
        loop = self.root / "loop"
        loop.symlink_to("loop")
        with patch("sys.stderr", new_callable=io.StringIO) as errors:
            status = rendering.main(["--root", str(loop), "--check"])
        self.assertEqual(status, 2)
        self.assertIn(str(self.root.resolve() / "loop"), errors.getvalue())


if __name__ == "__main__":
    unittest.main()
