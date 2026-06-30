# Agent Guide

This repository is a dependency-free Python package for inspecting local Codex
CLI token usage. Keep changes small, behavior-preserving by default, and covered
by focused tests.

## Working Rules

- Use `rg` and `rg --files` for code search.
- Do not add runtime dependencies unless the user explicitly asks for that
  tradeoff.
- Keep public import facades stable:
  - `codex_token_usage.report`
  - `codex_token_usage.theme`
  - `codex_token_usage.tui`
- Prefer focused modules over large files. After the package split, avoid
  rebuilding monolithic TUI, theme, or report modules.
- Keep config compatibility. Do not change the JSON config shape unless the
  change is explicitly requested and tested.
- Preserve local-only behavior. The app reads Codex data from disk and should
  not require network access.
- Use ASCII in new files unless there is a clear reason not to.

## Common Commands

Run the full test suite:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

Run focused suites:

```bash
PYTHONPATH=src python -m unittest tests.test_tui_state
PYTHONPATH=src python -m unittest tests.test_theme
PYTHONPATH=src python -m unittest tests.test_report
```

Check import/compile health:

```bash
python -m compileall src/codex_token_usage
PYTHONPATH=src python -m codex_token_usage --help
```

Smoke-test compatibility facades:

```bash
PYTHONPATH=src python -c "from codex_token_usage.tui import TuiState; from codex_token_usage.theme import ThemeConfig; from codex_token_usage.report import render_report"
```

## Testing Expectations

- Loader changes: update `tests/test_loader.py`.
- Forecast changes: update `tests/test_forecast.py`.
- Theme/config changes: update `tests/test_theme.py`.
- Report output changes: update `tests/test_report.py`.
- TUI state, settings, key handling, and rendering helpers: update
  `tests/test_tui_state.py`.
- CLI parser or command behavior: update `tests/test_cli.py`.

If a bug is found through a key path, add a regression that drives that key path
with `FakeStdScr` when practical.

## Packaging Notes

- Source packages live under `src/codex_token_usage`.
- Package discovery is configured in `pyproject.toml`.
- `theme/flag_presets.json` is package data and must stay listed under
  `codex_token_usage.theme`.
- The console entry point is `codex-token-usage = codex_token_usage.cli:main`.

## Git Hygiene

- Check `git status --short` before editing.
- Do not revert unrelated user changes.
- Do not run destructive git commands unless explicitly requested.
- If asked to commit, stage only the relevant files and use a concise message.
