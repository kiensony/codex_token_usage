# Codex Token Usage

`codex-token-usage` is a dependency-free local Python app for inspecting Codex CLI token usage. By default it opens a full-screen `curses` TUI. It also supports table, JSON, and CSV output for scripts.

The authoritative token source is `~/.codex/sessions/**/*.jsonl`. For each session, only the last cumulative `token_count` event is counted. The app optionally reads `~/.codex/state_5.sqlite` in read-only mode for safe metadata such as model, working directory, title, and timestamps.

## Usage

```bash
codex-token-usage
codex-token-usage --format table --group-by date
codex-token-usage --format graph --group-by week --since 2026-06-01
codex-token-usage --format json --group-by session --since 2026-06-01
codex-token-usage --format csv --group-by model --top 10
codex-token-usage --format table --group-by project
codex-token-usage --setup
codex-token-usage --format graph --theme all --color always
codex-token-usage --five-hour-token-limit 100000 --weekly-token-limit 2000000
```

Options:

- `--codex-home PATH`: default `~/.codex`
- `-c`, `--config`, `--setup`: open the theme, display column, and model rate setup wizard and exit
- `--since YYYY-MM-DD`
- `--until YYYY-MM-DD`
- `--format table|json|csv|graph`
- `--group-by date|week|month|hour|session|model|project|folder|cwd` (`day` is also accepted as an alias for `date`; `folder` is an alias for `project`)
- `--top N`
- `--include-zero`
- `--five-hour-token-limit TOKENS`: one-run rolling 5-hour warning limit; `0` disables
- `--weekly-token-limit TOKENS`: one-run weekly warning limit; `0` disables
- `--theme PRESET`: one-run Pride theme override, or `plain` to disable
- `--color auto|always|never`: ANSI color policy for `--format graph`
- `--lightness 0..1`: one-run theme brightness override

Settings are stored at `${XDG_CONFIG_HOME:-~/.config}/codex-token-usage/config.json`.
The `--setup` wizard controls the theme, optional display columns, custom model rates, token warning limits, prediction algorithm, and TUI auto refresh interval.
Inside the TUI, `c` opens a curses settings screen for theme, display columns, model column width, model rates, prediction algorithm, auto refresh interval, and main TUI keybindings without leaving the app.
Available presets are loaded from HyFetch's preset table, including `rainbow`, `transgender`, `nonbinary`, `abrosexual`, `aromantic`, `intersex`, `progress`, `baker`, `band`, and many more. Compatibility aliases include `trans`, `nonhuman-unit`, and `ynullflux`.
The TUI applies the selected flag palette to global chrome, headings, selected rows, and usage bars when curses reports color support. Table, JSON, and CSV output stay uncolored.

Project/folder usage groups sessions by their exact recorded working directory (`cwd`). Existing `cwd` reports remain available for compatibility, and the TUI includes a `By Project` tab with the same aggregate columns and sorting controls as the date, week, month, and hour views.

Display settings can show or hide cached tokens, cached %, estimated API cost, reasoning level, cache miss, reasoning tokens, model, and cwd/title columns, and set the session table model column width to `auto` or a fixed 8-40 character width. Appearance settings can change the flag palette with a paged flag picker, color mode, lightness, accent line, and themed usage bars. Estimated cost uses standard OpenAI per-1M-token rates for known models, with any custom rates from setup overriding the built-in table. Unknown models show `n/a`; mixed aggregates with some unknown model rates are marked with `*`.

The overview shows projected usage for the next 5 hours, next day, next week, and next 30-day month. The prediction algorithm is configurable from the Misc settings tab: `recent_rate` projects from the current active usage rate, while `previous_period` assumes the next period will match the previous period's usage. The Misc tab can also set an automatic TUI refresh interval in seconds and customize the shutdown closing-frame interval; `0` or `off` disables auto refresh.

Forecast warnings are disabled until a positive token limit is configured. The 5-hour forecast uses sessions active in the rolling last 5 hours and projects that recent rate across a 5-hour horizon. The weekly forecast uses the current ISO week-to-date rate and projects it through the end of the week. Table and graph reports append compact forecast and prediction sections, JSON reports include a top-level `forecast` object, and weekly CSV rows include forecast columns when limits are enabled.

Example config snippet:

```json
{
  "limits": {
    "five_hour_tokens": 100000,
    "weekly_tokens": 2000000
  },
  "prediction": {
    "algorithm": "recent_rate"
  },
  "misc": {
    "auto_refresh_seconds": 30,
    "shutdown_seconds": 2.45
  }
}
```

Main TUI keybindings can be changed from the Keybindings settings tab or by editing the top-level `keybindings` object in the config file, for example `"next_view": ["n"]`. Missing actions use defaults. Supported key labels include printable characters, `Tab`, `Shift+Tab`, `Enter`, `Esc`, `Backspace`, `Up`, `Down`, `PageUp`, `PageDown`, `Home`, `End`, `Space`, `Comma`, and `Ctrl+A` through `Ctrl+Z`. Settings screens, prompts, and the flag picker keep their fixed local controls.

Default TUI keys:

- `Tab` / `Shift+Tab`: switch views
- Arrow keys or `j`/`k`: move selection
- `PageUp` / `PageDown`: move selection by page
- `Home` / `End`: jump to the first or last session
- `Enter`: open selected session details
- `s`: cycle sort field for the active rows
- `S`: reverse sort direction
- `/`: filter by cwd, model, title, or session id
- `d`: change date range preset
- `A`: show all time
- `[` / `]`: move the active date range backward or forward
- `r`: reload local data
- `c`: open TUI settings for theme, display columns, model width, model rates, and prediction algorithm
- `a`: show about this software
- `?`: show help
- `Backspace` / `Esc`: return from session details
- `q` / `Ctrl+C`: quit with a farewell message
- During farewell, `q` / `Esc`: exit immediately

TUI settings keys:

- `1` / `2` / `3` / `4` / `5`: switch between Model Pricing, Display Columns, Appearance, Keybindings, and Misc tabs
- `h` / `j` / `k` / `l`: move the selected field or row in the active tab
- `Enter`, `Space`, or `e`: edit or toggle the selected item
- Model Pricing tab: `a` adds a custom model rate, `x` removes the selected model's custom override
- Display Columns tab: toggles token/detail columns or edits model width
- Appearance tab: opens a flag picker, cycles color mode, edits lightness, and toggles accent line or themed bars
- Keybindings tab: select an action, `Enter` captures a replacement key, `a` captures an additional key, and `x` resets the selected action to its default
- Misc tab: `Enter` cycles the prediction algorithm, edits auto refresh or shutdown seconds, shows About, or resets all setup after confirmation
- Flag picker: `h` / `j` / `k` / `l` moves between flags, `n` / `p` changes page, `Enter` chooses
- `s`: save settings, confirming first when settings changed
- `q` / `Esc`: cancel settings, confirming discard when settings changed

## Development

Run tests with:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Linux standalone binary

The `Build Linux Binary` GitHub Actions workflow builds a `linux-x86_64` standalone executable with Python bundled by PyInstaller. The installable artifact is named like:

```text
codex-token-usage-0.1.0-linux-x86_64.tar.gz
```

Install from the extracted archive with:

```bash
tar -xzf codex-token-usage-0.1.0-linux-x86_64.tar.gz
cd codex-token-usage-0.1.0-linux-x86_64
sudo ./install.sh
```

To install somewhere else, set `PREFIX` or `BINDIR`:

```bash
PREFIX="$HOME/.local" ./install.sh
```
