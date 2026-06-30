from __future__ import annotations

import contextlib
import io
import unittest

from codex_token_usage.cli import build_parser


class CliParserTests(unittest.TestCase):
    def test_setup_aliases_parse(self) -> None:
        for flag in ("-c", "--config", "--setup"):
            with self.subTest(flag=flag):
                args = build_parser().parse_args([flag])
                self.assertTrue(args.setup)

    def test_theme_color_and_lightness_parse(self) -> None:
        args = build_parser().parse_args(
            ["--theme", "trans", "--color", "always", "--lightness", "0.5"]
        )

        self.assertEqual(args.theme, "trans")
        self.assertEqual(args.color, "always")
        self.assertEqual(args.lightness, 0.5)

    def test_plain_theme_override_parse(self) -> None:
        args = build_parser().parse_args(["--theme", "plain"])

        self.assertEqual(args.theme, "plain")

    def test_all_theme_override_parse(self) -> None:
        args = build_parser().parse_args(["--theme", "all"])

        self.assertEqual(args.theme, "all")

    def test_week_and_month_grouping_parse(self) -> None:
        for group_by in ("week", "month"):
            with self.subTest(group_by=group_by):
                args = build_parser().parse_args(["--group-by", group_by])
                self.assertEqual(args.group_by, group_by)

    def test_invalid_lightness_rejected(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            build_parser().parse_args(["--lightness", "1.1"])


if __name__ == "__main__":
    unittest.main()
