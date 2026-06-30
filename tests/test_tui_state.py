from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from codex_token_usage.keybindings import KeybindingConfig, update_keybinding
from codex_token_usage.models import (
    SessionMetadata,
    SessionUsage,
    TokenBreakdown,
    UsageDataset,
)
from codex_token_usage.pricing import ModelPrice
from codex_token_usage.theme import ThemeConfig, themed_bar_segments
from codex_token_usage.tui import (
    CursesUi,
    TuiOptions,
    TuiState,
    appearance_preview_block_height,
    appearance_setting_label,
    cycle_theme_color_mode,
    cycle_theme_preset,
    display_setting_label,
    flag_picker_block_height,
    flag_picker_page_size,
    flag_picker_visible_rows,
    flag_display_name,
    parse_settings_lightness,
    parse_settings_model_width,
    parse_settings_rate,
    settings_model_names,
    settings_price_source,
    settings_rate_text,
    theme_current_preset,
    theme_current_preset_label,
    theme_preset_label,
    truncate,
    usage_bar,
    visible_start,
)


class TuiStateTests(unittest.TestCase):
    def test_view_switching_selection_sort_filter_and_quit(self) -> None:
        state = TuiState(dataset=dataset(), today=date(2026, 6, 29))

        state = state.next_view()
        self.assertEqual(state.view, "daily")
        state = state.previous_view()
        self.assertEqual(state.view, "overview")

        state = state.next_view().next_view()
        self.assertEqual(state.view, "weekly")
        self.assertEqual([row.key for row in state.weekly_rows()], ["2026-W23"])
        self.assertEqual(state.weekly_rows()[0].tokens.total_tokens, 30)

        state = state.next_view()
        self.assertEqual(state.view, "monthly")
        self.assertEqual([row.key for row in state.monthly_rows()], ["2026-06"])
        self.assertEqual(state.monthly_rows()[0].tokens.total_tokens, 30)

        state = state.next_view()
        self.assertEqual(state.view, "hourly")
        self.assertEqual(
            [row.key for row in state.hourly_rows()],
            ["2026-06-02 00:00", "2026-06-01 00:00"],
        )

        state = state.next_view()
        self.assertEqual(state.view, "sessions")
        self.assertEqual(state.selected_session().session_id, "beta")
        state = state.move_selection(1)
        self.assertEqual(state.selected_session().session_id, "alpha")

        state = state.cycle_sort()
        self.assertEqual(state.sort_field, "input")
        self.assertEqual(
            [session.session_id for session in state.visible_sessions()],
            ["alpha", "beta"],
        )
        state = state.set_filter("other")
        self.assertEqual(len(state.visible_sessions()), 1)
        self.assertEqual(state.selected_session().session_id, "beta")

        state = state.open_details()
        self.assertEqual(state.view, "details")
        state = state.quit()
        self.assertTrue(state.should_quit)

    def test_date_preset_and_reload(self) -> None:
        state = TuiState(dataset=dataset(), today=date(2026, 6, 29))

        state = state.cycle_date_preset()
        self.assertEqual(state.date_preset, "today")
        self.assertEqual(len(state.visible_sessions()), 0)

        state = state.set_all_time()
        self.assertEqual(state.date_preset, "all")
        self.assertIsNone(state.since)
        self.assertIsNone(state.until)
        self.assertEqual(state.range_label(), "all time")
        self.assertEqual(len(state.visible_sessions()), 2)

        reloaded = state.reload(lambda since, until: dataset(extra=True))
        self.assertEqual(reloaded.status, "reloaded 3 sessions")

    def test_reverse_sort_paging_and_jumps(self) -> None:
        state = TuiState(dataset=dataset(count=15), today=date(2026, 6, 29))

        self.assertEqual(state.selected_session().session_id, "s14")

        state = state.toggle_sort_direction()
        self.assertFalse(state.sort_descending)
        self.assertEqual(state.selected_session().session_id, "s00")

        state = state.page_selection(1, page_size=10)
        self.assertEqual(state.selected_index, 10)
        self.assertEqual(state.selected_session().session_id, "s10")

        state = state.select_last()
        self.assertEqual(state.selected_session().session_id, "s14")
        state = state.select_first()
        self.assertEqual(state.selected_session().session_id, "s00")

    def test_grouped_rows_follow_tui_sort(self) -> None:
        state = TuiState(dataset=dataset(), today=date(2026, 6, 29))

        self.assertEqual(
            [row.key for row in state.hourly_rows()],
            ["2026-06-02 00:00", "2026-06-01 00:00"],
        )

        state = state.cycle_sort()
        self.assertEqual(state.sort_field, "input")
        self.assertEqual(
            [row.key for row in state.hourly_rows()],
            ["2026-06-01 00:00", "2026-06-02 00:00"],
        )

        state = state.toggle_sort_direction()
        self.assertEqual(
            [row.key for row in state.hourly_rows()],
            ["2026-06-02 00:00", "2026-06-01 00:00"],
        )

    def test_date_window_shift(self) -> None:
        state = TuiState(
            dataset=dataset(),
            since=date(2026, 6, 1),
            until=date(2026, 6, 7),
            today=date(2026, 6, 29),
        )

        state = state.shift_date_window(1)
        self.assertEqual(state.since, date(2026, 6, 8))
        self.assertEqual(state.until, date(2026, 6, 14))

        state = state.shift_date_window(-1)
        self.assertEqual(state.since, date(2026, 6, 1))
        self.assertEqual(state.until, date(2026, 6, 7))

    def test_help_and_filter_clear_cancel(self) -> None:
        state = TuiState(dataset=dataset())

        state = state.open_help()
        self.assertTrue(state.help_open)
        state = state.close_help()
        self.assertFalse(state.help_open)

        state = state.set_filter("repo")
        self.assertEqual(state.filter_text, "repo")
        state = state.clear_filter()
        self.assertEqual(state.filter_text, "")
        self.assertEqual(state.status, "filter cleared")

        state = state.cancel_filter()
        self.assertEqual(state.status, "filter canceled")

    def test_details_back_navigation_and_reload_preserves_selection(self) -> None:
        state = TuiState(dataset=dataset(extra=True), today=date(2026, 6, 29))
        state = state.move_selection(1)
        selected_id = state.selected_session().session_id

        state = state.open_details()
        self.assertEqual(state.view, "details")
        state = state.close_details()
        self.assertEqual(state.view, "overview")

        reloaded = state.reload(lambda since, until: dataset(extra=True))
        self.assertEqual(reloaded.selected_session().session_id, selected_id)

    def test_graph_helpers(self) -> None:
        self.assertEqual(usage_bar(0, 100, 5), ".....")
        self.assertEqual(usage_bar(50, 100, 5), "##...")
        self.assertEqual(usage_bar(100, 100, 5), "#####")
        self.assertEqual(visible_start(12, 10, 20), 3)
        self.assertEqual(truncate("abcdef", 4), "abc~")
        self.assertEqual(CursesUi.session_model_width(160), 24)
        self.assertEqual(CursesUi.session_model_width(160, configured_width=12), 12)

    def test_curses_ui_uses_default_and_custom_keybindings(self) -> None:
        state = TuiState(dataset=dataset())
        ui = CursesUi(None, state, TuiOptions(codex_home=Path("/tmp")))

        ui.handle_key(ord("j"))
        self.assertEqual(ui.state.selected_session().session_id, "alpha")

        keybindings = update_keybinding(
            KeybindingConfig(),
            "next_view",
            ("n",),
        )
        ui = CursesUi(
            None,
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp"), keybindings=keybindings),
        )

        ui.handle_key(ord("n"))
        self.assertEqual(ui.state.view, "daily")

    def test_curses_ui_captures_keybindings(self) -> None:
        ui = CursesUi(
            FakeStdScr([ord("n"), ord("m")]),
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )

        keybindings, status = ui.apply_keybinding_setting(
            KeybindingConfig(),
            "next_view",
        )
        self.assertEqual(keybindings.labels("next_view"), ("n",))
        self.assertEqual(status, "Next view: n")

        keybindings, status = ui.capture_keybinding(
            keybindings,
            "next_view",
            append=True,
        )
        self.assertEqual(keybindings.labels("next_view"), ("n", "m"))
        self.assertEqual(status, "Next view: n, m")

    def test_settings_helpers(self) -> None:
        custom = {"custom-model": ModelPrice(1.0, 0.1, 2.0)}
        names = settings_model_names(dataset(), custom)

        self.assertIn("custom-model", names)
        self.assertIn("gpt-5", names)
        self.assertEqual(settings_price_source("custom-model", custom), "custom")
        self.assertEqual(settings_price_source("gpt-5.3-codex", custom), "built-in")
        self.assertEqual(settings_price_source("unknown-model", custom), "unpriced")
        self.assertEqual(settings_rate_text(custom["custom-model"], "cached"), "0.1")
        self.assertEqual(display_setting_label("estimated_cost"), "estimated cost")
        self.assertEqual(appearance_setting_label("themed_bars"), "themed usage bars")
        self.assertEqual(parse_settings_rate("1.25"), 1.25)
        self.assertEqual(parse_settings_model_width("auto"), None)
        self.assertEqual(parse_settings_model_width("18"), 18)

    def test_settings_theme_helpers(self) -> None:
        theme = ThemeConfig(enabled=False, preset="rainbow", color_mode="8bit")

        self.assertEqual(theme_preset_label(theme), "plain")
        self.assertEqual(theme_current_preset(theme), "rainbow")
        self.assertEqual(theme_current_preset_label(theme), "rainbow (plain)")
        self.assertEqual(theme_current_preset(ThemeConfig(preset="")), "femboy")
        self.assertEqual(flag_display_name("trans"), "transgender")
        theme = cycle_theme_preset(theme)
        self.assertTrue(theme.enabled)
        self.assertEqual(theme.preset, "rainbow")

        theme = cycle_theme_color_mode(theme)
        self.assertEqual(theme.color_mode, "rgb")

        self.assertEqual(parse_settings_lightness("0.6"), 0.6)
        self.assertIsInstance(parse_settings_lightness("1.5"), str)
        self.assertEqual(appearance_preview_block_height(24, 15), 5)
        self.assertEqual(appearance_preview_block_height(30, 15), 5)
        self.assertEqual(flag_picker_block_height(24), 5)
        self.assertEqual(flag_picker_visible_rows(24), 2)
        self.assertEqual(flag_picker_page_size(24), 8)

    def test_themed_bar_segments_and_plain_fallback(self) -> None:
        themed = themed_bar_segments(
            100,
            100,
            10,
            ThemeConfig(enabled=True, preset="rainbow"),
        )
        plain = themed_bar_segments(
            50,
            100,
            5,
            ThemeConfig(enabled=False, preset="rainbow"),
        )

        self.assertEqual("".join(segment.text for segment in themed), "#" * 10)
        self.assertGreater(
            len({segment.color_index for segment in themed if segment.color_index is not None}),
            1,
        )
        self.assertEqual(len(plain), 1)
        self.assertEqual(plain[0].text, "##...")
        self.assertIsNone(plain[0].color_index)


def dataset(extra: bool = False, count: int | None = None) -> UsageDataset:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        if count is not None:
            sessions = [
                session(
                    f"s{index:02d}",
                    index + 1,
                    index + 1,
                    "/repo",
                    f"2026-06-{index + 1:02d}T00:00:00+00:00",
                    root,
                )
                for index in range(count)
            ]
        else:
            sessions = [
                session("alpha", 10, 9, "/repo", "2026-06-01T00:00:00+00:00", root),
                session("beta", 20, 2, "/other", "2026-06-02T00:00:00+00:00", root),
            ]
        if extra:
            sessions.append(
                session("gamma", 1, 1, "/repo", "2026-06-03T00:00:00+00:00", root)
            )
        return UsageDataset(
            sessions=tuple(sessions),
            codex_home=root,
            loaded_at=datetime.now(timezone.utc),
            sqlite_available=False,
        )


def session(
    session_id: str,
    total: int,
    input_tokens: int,
    cwd: str,
    updated_at: str,
    root: Path,
) -> SessionUsage:
    updated = datetime.fromisoformat(updated_at)
    return SessionUsage(
        session_id=session_id,
        path=root / f"{session_id}.jsonl",
        tokens=TokenBreakdown(
            input_tokens=input_tokens,
            output_tokens=total - input_tokens,
            total_tokens=total,
        ),
        metadata=SessionMetadata(
            session_id=session_id,
            model="gpt-5",
            cwd=cwd,
            created_at=updated,
            updated_at=updated,
        ),
        has_token_event=True,
    )


class FakeStdScr:
    def __init__(self, keys: list[int]) -> None:
        self.keys = keys

    def getmaxyx(self) -> tuple[int, int]:
        return (24, 80)

    def move(self, _y: int, _x: int) -> None:
        return None

    def clrtoeol(self) -> None:
        return None

    def addstr(self, _y: int, _x: int, _text: str, _attr: int = 0) -> None:
        return None

    def getch(self) -> int:
        return self.keys.pop(0)


if __name__ == "__main__":
    unittest.main()
