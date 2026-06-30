# Codebase Guide

`codex-token-usage` is a local, dependency-free Python application for reading
Codex CLI usage data and presenting it through a curses TUI or script-friendly
reports.

## Data Flow

1. `cli.py` parses command-line options.
2. `loader.py` reads `~/.codex/sessions/**/*.jsonl` and optional SQLite
   metadata from `~/.codex/state_5.sqlite`.
3. `models.py` represents sessions, token counts, metadata, and datasets.
4. Reports use `report/`; the interactive app uses `tui/`.
5. Theme, display, pricing, keybinding, limit, prediction, refresh, and shutdown
   settings are loaded through `theme/`.

Only the last cumulative token-count event in a session is counted.

## Top-Level Modules

- `cli.py`: argparse entry point, setup mode, report mode, and TUI launch.
- `loader.py`: JSONL parsing, SQLite metadata reads, date filtering, and session
  assembly.
- `models.py`: immutable data models for token breakdowns, sessions, metadata,
  and datasets.
- `pricing.py`: built-in model rates, custom pricing support, and cost
  estimates.
- `forecast.py`: token limits, rolling 5-hour and weekly forecasts, usage
  predictions, and forecast serialization.
- `keybindings.py`: default TUI keybindings, config parsing, key normalization,
  conflict validation, and keymap generation.

## Report Package

Public imports are re-exported from `codex_token_usage.report`.

- `report/models.py`: `ReportRow` and report grouping constants.
- `report/rows.py`: session filtering, grouping, and row aggregation.
- `report/renderers.py`: table, JSON, CSV, graph, and top-level report
  rendering.
- `report/forecast_display.py`: forecast and prediction report appendices.
- `report/formatting.py`: number formatting, table formatting, CSV/JSON helpers,
  and group aliases.

Keep output formats stable unless tests and README examples are updated.

## Theme Package

Public imports are re-exported from `codex_token_usage.theme`.

- `theme/models.py`: theme/display/config result dataclasses and constants.
- `theme/presets.py`: Pride flag preset loading, aliases, and defaults.
- `theme/config.py`: config path, config load/save, parse helpers, validation,
  and one-run theme overrides.
- `theme/rendering.py`: palettes, lightness adjustment, themed bars, and ANSI
  color conversion.
- `theme/setup_wizard.py`: non-curses setup wizard and prompt helpers.
- `theme/flag_presets.json`: packaged preset data.

The persisted config shape is part of the app contract. Preserve existing keys
and defaults unless a migration is intentionally designed.

## TUI Package

Public imports are re-exported from `codex_token_usage.tui`.

- `tui/app.py`: `run_tui`, `CursesUi`, main loop, key dispatch, reload, and
  auto-refresh scheduling.
- `tui/state.py`: immutable TUI state, view/date/sort constants, filtering,
  grouping accessors, and sort keys.
- `tui/views.py`: main screens for overview, grouped rows, sessions, and details.
- `tui/view_overlays.py`: help, about, farewell, key-value rendering, and footer.
- `tui/theme_renderer.py`: curses color pairs, themed text, themed bars, and
  safe writes.
- `tui/prompts.py`: text prompts, confirmations, model-rate prompts, and filter
  input.
- `tui/settings_screen.py`: settings event loop and tab navigation.
- `tui/settings_rendering.py`: settings tab rendering.
- `tui/settings_actions.py`: settings edit/apply handlers and key capture.
- `tui/settings_flag_picker.py`: paged flag picker.
- `tui/settings_model.py`: settings labels, parser adapters, snapshots,
  appearance/about/farewell text helpers, and settings constants.
- `tui/forecast_display.py`: forecast labels for TUI overview rows.
- `tui/formatting.py`: terminal layout helpers, visible-row math, truncation, and
  plain usage bars.

The TUI tests use `FakeStdScr` to exercise key paths without launching a real
curses UI. Prefer that pattern for regression tests.

## Config And User Data

- Default Codex home: `~/.codex`.
- Session source: `~/.codex/sessions/**/*.jsonl`.
- Optional metadata source: `~/.codex/state_5.sqlite`.
- Settings path:
  `${XDG_CONFIG_HOME:-~/.config}/codex-token-usage/config.json`.

The app should handle missing, malformed, or partial local data gracefully.

## Compatibility Boundaries

- `codex_token_usage.report`, `codex_token_usage.theme`, and
  `codex_token_usage.tui` are compatibility facades. Keep commonly imported
  helpers re-exported there.
- CLI flags and README examples should remain accurate.
- Report aliases are `day -> date` and `folder -> project`.
- Unknown model prices should render as unpriced instead of failing.
- Settings local controls are intentionally fixed even when main TUI keybindings
  are user-configurable.
