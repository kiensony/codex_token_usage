from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .loader import load_usage, parse_date
from .report import render_report
from .theme import (
    PLAIN_THEME_NAMES,
    PRESET_NAMES,
    apply_theme_overrides,
    load_theme_config,
    parse_lightness,
    run_setup_wizard,
    should_use_ansi_color,
)
from .tui import TuiOptions, run_tui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-token-usage",
        description="Inspect local Codex CLI token usage.",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path("~/.codex"),
        help="Path to the Codex home directory (default: ~/.codex).",
    )
    parser.add_argument(
        "--format",
        choices=("table", "json", "csv", "graph"),
        help="Print a non-interactive report instead of opening the TUI.",
    )
    parser.add_argument(
        "-c",
        "--config",
        "--setup",
        dest="setup",
        action="store_true",
        help="Open the Pride theme setup wizard and exit.",
    )
    parser.add_argument(
        "--theme",
        choices=(*PRESET_NAMES, *PLAIN_THEME_NAMES),
        help="Use a Pride theme preset for this run. Use 'plain' to disable.",
    )
    parser.add_argument(
        "--color",
        choices=("auto", "always", "never"),
        default="auto",
        help="Control ANSI color for --format graph output (default: auto).",
    )
    parser.add_argument(
        "--lightness",
        type=parse_lightness_arg,
        help="Override theme lightness for this run with a value from 0 to 1.",
    )
    parser.add_argument(
        "--since",
        type=parse_date,
        help="Include sessions on or after this date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--until",
        type=parse_date,
        help="Include sessions on or before this date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--group-by",
        choices=("date", "week", "month", "hour", "session", "day", "model", "cwd"),
        default="date",
        help=(
            "Report grouping for non-interactive output. "
            "'day' is an alias for 'date'."
        ),
    )
    parser.add_argument(
        "--top",
        type=int,
        help="Limit non-interactive output to the top N rows.",
    )
    parser.add_argument(
        "--include-zero",
        action="store_true",
        help="Include sessions with no token_count event or zero tokens.",
    )
    return parser


def parse_lightness_arg(value: str) -> float:
    try:
        return parse_lightness(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.setup:
        return run_setup_wizard()

    if args.since and args.until and args.since > args.until:
        parser.error("--since must be on or before --until")

    theme_result = load_theme_config()
    theme = apply_theme_overrides(
        theme_result.config,
        preset=args.theme,
        lightness=args.lightness,
    )

    if args.format:
        dataset = load_usage(
            codex_home=args.codex_home,
            since=args.since,
            until=args.until,
            include_zero=args.include_zero,
        )
        sys.stdout.write(
            render_report(
                dataset,
                output_format=args.format,
                group_by=args.group_by,
                top=args.top,
                theme=theme,
                color_enabled=(
                    args.format == "graph"
                    and should_use_ansi_color(args.color, sys.stdout)
                ),
            )
        )
        return 0

    return run_tui(
        TuiOptions(
            codex_home=args.codex_home,
            since=args.since,
            until=args.until,
            include_zero=args.include_zero,
            theme=theme,
            display=theme_result.display,
            pricing=theme_result.pricing,
            theme_status=theme_result.status,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
