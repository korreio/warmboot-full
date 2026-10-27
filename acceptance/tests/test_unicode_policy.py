"""Direct regressions for the CommonMark fence helpers in unicode_policy.

The oracles rely on ``markdown_fence_opening``/``markdown_fence_closing`` to decide
which raw lines are structural fences and which remain literal evidence. These pin the
bounded CommonMark thresholds (at most three leading spaces, a run of at least three
markers) so a relaxed helper cannot silently start hiding or exposing evidence.
"""

import unittest

from acceptance.unicode_policy import markdown_fence_closing, markdown_fence_opening


class MarkdownFenceHelperTests(unittest.TestCase):
    def test_four_space_indent_is_not_a_fence_opening(self) -> None:
        """Four leading spaces are an indented code block, not a fence opening."""
        self.assertEqual(markdown_fence_opening("   ```yaml"), ("`", 3))
        self.assertIsNone(markdown_fence_opening("    ```yaml"))
        self.assertIsNone(markdown_fence_opening("    ~~~"))

    def test_two_backtick_run_is_not_a_fence(self) -> None:
        """A fence opening requires a run of at least three markers."""
        self.assertIsNone(markdown_fence_opening("``"))
        self.assertIsNone(markdown_fence_opening("~~"))
        self.assertEqual(markdown_fence_opening("```"), ("`", 3))

    def test_four_space_indented_closer_is_not_a_valid_closer(self) -> None:
        """Four leading spaces cannot close an open fence."""
        self.assertTrue(markdown_fence_closing("```", ("`", 3)))
        self.assertTrue(markdown_fence_closing("   ```", ("`", 3)))
        self.assertFalse(markdown_fence_closing("    ```", ("`", 3)))


if __name__ == "__main__":
    unittest.main()
