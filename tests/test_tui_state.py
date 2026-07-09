from __future__ import annotations

import curses
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest import mock

from codex_token_usage.forecast import LimitConfig, PredictionConfig, make_usage_forecast
from codex_token_usage.keybindings import KeybindingConfig, update_keybinding
from codex_token_usage.models import (
    SessionMetadata,
    SessionUsage,
    TokenBreakdown,
    UsageDataset,
    UsageEvent,
)
from codex_token_usage.pricing import ModelPrice
from codex_token_usage.theme import (
    DisplayConfig,
    PRESET_NAMES,
    ThemeConfig,
    theme_palette,
    themed_bar_segments,
)
from codex_token_usage.tui import (
    ABOUT_DESCRIPTION,
    OFFBOARD_MESSAGE,
    CursesUi,
    TuiOptions,
    TuiState,
    about_content_lines,
    appearance_preview_block_height,
    appearance_setting_label,
    auto_refresh_label,
    current_usage_rate_rows,
    cycle_prediction_algorithm,
    cycle_theme_color_mode,
    cycle_theme_preset,
    default_setup_values,
    display_setting_label,
    flag_picker_block_height,
    farewell_flag_height,
    farewell_frame_delay,
    flag_picker_page_size,
    flag_picker_visible_rows,
    flag_display_name,
    farewell_content_lines,
    forecast_key_values,
    misc_setting_label,
    prediction_algorithm_label,
    prediction_key_values,
    parse_settings_auto_refresh_seconds,
    parse_settings_lightness,
    parse_settings_model_width,
    parse_settings_rate,
    parse_settings_shutdown_seconds,
    pride_community_message,
    pride_message_for_preset,
    pride_messages_for_presets,
    run_tui,
    settings_model_names,
    settings_price_source,
    settings_rate_text,
    settings_snapshot,
    shutdown_seconds_label,
    downsample_series,
    line_chart_rows,
    statistic_line_series,
    statistic_usage_rate_windows,
    theme_current_preset,
    theme_current_preset_label,
    theme_preset_label,
    truncate,
    usage_bar,
    visible_start,
    format_token_count,
)
from codex_token_usage.tui.secret_codes import (
    EFFECT_BIRTHDAY,
    EFFECT_CLAUDE,
    EFFECT_EMERGENCY,
    EFFECT_HEART,
    EFFECT_NYAN,
    EFFECT_PWNED,
    EFFECT_TRANS_FLAG,
    EMERGENCY_CRASH_LINES,
    EMERGENCY_CODES,
    EMERGENCY_EXIT_CODE,
    EMERGENCY_MESSAGE,
    EmergencyCrash,
    SECRET_CODE_EFFECTS,
    SECRET_CODE_KEY,
    SECRET_PROMPT,
    emergency_crash_screen,
)


class TuiStateTests(unittest.TestCase):
    def test_view_switching_selection_sort_filter_and_quit(self) -> None:
        state = TuiState(dataset=dataset(), today=date(2026, 6, 29))

        state = state.next_view()
        self.assertEqual(state.view, "statistic")
        state = state.previous_view()
        self.assertEqual(state.view, "overview")

        state = state.next_view().next_view()
        self.assertEqual(state.view, "daily")
        self.assertEqual(
            [row.key for row in state.daily_rows()],
            ["2026-06-02", "2026-06-01"],
        )

        state = state.next_view()
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
        self.assertEqual(state.view, "models")
        self.assertEqual([row.key for row in state.model_rows()], ["gpt-5"])
        self.assertEqual(state.model_rows()[0].tokens.total_tokens, 30)

        state = state.next_view()
        self.assertEqual(state.view, "projects")
        self.assertEqual([row.key for row in state.project_rows()], ["/other", "/repo"])

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

    def test_project_model_rows_group_tokens_by_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            usage_dataset = UsageDataset(
                sessions=(
                    session(
                        "repo-gpt-a",
                        100,
                        80,
                        "/repo",
                        "2026-06-01T00:00:00+00:00",
                        root,
                        model="gpt-5",
                    ),
                    session(
                        "repo-o4",
                        40,
                        30,
                        "/repo",
                        "2026-06-02T00:00:00+00:00",
                        root,
                        model="o4-mini",
                    ),
                    session(
                        "repo-gpt-b",
                        20,
                        15,
                        "/repo",
                        "2026-06-03T00:00:00+00:00",
                        root,
                        model="gpt-5",
                    ),
                    session(
                        "other",
                        200,
                        100,
                        "/other",
                        "2026-06-04T00:00:00+00:00",
                        root,
                        model="gpt-5",
                    ),
                ),
                codex_home=root,
                loaded_at=datetime.now(timezone.utc),
                sqlite_available=False,
            )
        state = TuiState(dataset=usage_dataset)

        projects = state.project_model_rows()
        repo = next(row for row in projects if row.project.key == "/repo")

        self.assertEqual(repo.project.sessions, 3)
        self.assertEqual(repo.project.tokens.total_tokens, 160)
        self.assertEqual([row.key for row in repo.models], ["gpt-5", "o4-mini"])
        self.assertEqual([row.sessions for row in repo.models], [2, 1])
        self.assertEqual([row.tokens.total_tokens for row in repo.models], [120, 40])

    def test_project_cursor_opens_selected_project_details(self) -> None:
        state = TuiState(dataset=dataset(), today=date(2026, 6, 29))
        while state.view != "projects":
            state = state.next_view()

        self.assertEqual(state.selected_project().project.key, "/other")

        state = state.move_selection(1)
        self.assertEqual(state.selected_project().project.key, "/repo")

        state = state.open_details()
        self.assertEqual(state.view, "details")
        self.assertEqual(state.tab_view, "projects")
        self.assertEqual(state.selected_project().project.key, "/repo")

        state = state.close_details()
        self.assertEqual(state.view, "projects")

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

    def test_about_state_and_keybinding(self) -> None:
        state = TuiState(dataset=dataset())

        state = state.open_about()
        self.assertTrue(state.about_open)
        self.assertFalse(state.help_open)
        state = state.close_about()
        self.assertFalse(state.about_open)

        ui = CursesUi(
            FakeStdScr([]),
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )
        ui.handle_key(ord("a"))
        self.assertTrue(ui.state.about_open)
        ui.handle_key(27)
        self.assertFalse(ui.state.about_open)

    def test_ctrl_c_quits(self) -> None:
        ui = CursesUi(
            FakeStdScr([]),
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )

        ui.handle_key(3)

        self.assertTrue(ui.state.should_quit)

    def test_farewell_force_shutdown_keys(self) -> None:
        ui = CursesUi(
            FakeStdScr([ord("q")]),
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )
        self.assertTrue(ui.wait_for_farewell_frame(2500))

        ui = CursesUi(
            FakeStdScr([27]),
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )
        self.assertTrue(ui.wait_for_farewell_frame(2500))

        ui = CursesUi(
            FakeStdScr([ord("x"), -1]),
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )
        self.assertFalse(ui.wait_for_farewell_frame(2500))

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

    def test_chart_helpers(self) -> None:
        self.assertEqual(usage_bar(0, 100, 5), ".....")
        self.assertEqual(usage_bar(50, 100, 5), "##...")
        self.assertEqual(usage_bar(100, 100, 5), "#####")
        self.assertEqual(downsample_series((1, 2, 3, 4), 2), (2, 4))
        chart = line_chart_rows((0, 5, 10), 15, 3)
        self.assertEqual(chart[0], "     10.0 ┌───┐")
        self.assertEqual(chart[1], "          │ ⢀⠎│")
        self.assertEqual(chart[2], "     5.00 │⢀⠎ │")
        self.assertEqual(chart[3], "          │⡜  │")
        self.assertEqual(chart[4], "        0 └───┘")
        self.assertIn("old", chart[5])
        self.assertNotIn("/", "".join(chart))
        self.assertNotIn("\\", "".join(chart))
        self.assertEqual(visible_start(12, 10, 20), 3)
        self.assertEqual(truncate("abcdef", 4), "abc~")
        self.assertEqual(CursesUi.session_model_width(160), 24)
        self.assertEqual(CursesUi.session_model_width(160, configured_width=12), 12)
        self.assertEqual(farewell_flag_height(20, 4, ((1, 2, 3), (4, 5, 6))), 2)
        self.assertEqual(farewell_flag_height(8, 4, ((1, 2, 3), (4, 5, 6))), 0)
        self.assertEqual(farewell_frame_delay(2.5), 2500)

    def test_safe_addstr_uses_full_available_width(self) -> None:
        stdscr = FakeStdScr([], size=(4, 5))
        ui = CursesUi(stdscr, TuiState(dataset=dataset()), TuiOptions(codex_home=Path("/tmp")))

        ui.safe_addstr(0, 0, "abcde")

        self.assertEqual(stdscr.writes[-1][2], "abcde")

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
        self.assertEqual(ui.state.view, "statistic")

    def test_help_overlay_closes_from_multiple_keys_and_ignores_navigation(self) -> None:
        for close_key in (ord("?"), ord("q"), 27):
            with self.subTest(close_key=close_key):
                ui = CursesUi(
                    None,
                    TuiState(dataset=dataset()).open_help(),
                    TuiOptions(codex_home=Path("/tmp")),
                )

                ui.handle_key(ord("j"))

                self.assertTrue(ui.state.help_open)
                self.assertEqual(ui.state.selected_session().session_id, "beta")

                ui.handle_key(close_key)

                self.assertFalse(ui.state.help_open)
                self.assertFalse(ui.state.should_quit)

    def test_escape_backs_out_of_details_before_quitting(self) -> None:
        ui = CursesUi(
            None,
            TuiState(dataset=dataset()).open_details(),
            TuiOptions(codex_home=Path("/tmp")),
        )

        ui.handle_key(27)

        self.assertEqual(ui.state.view, "overview")
        self.assertFalse(ui.state.should_quit)

        ui.handle_key(27)

        self.assertTrue(ui.state.should_quit)

    def test_filter_prompt_supports_cursor_editing_and_escape_clear(self) -> None:
        ui = CursesUi(
            FakeStdScr(
                [
                    ord("r"),
                    ord("e"),
                    ord("p"),
                    ord("o"),
                    curses.KEY_LEFT,
                    127,
                    ord("x"),
                    10,
                ]
            ),
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )

        ui.handle_key(ord("/"))

        self.assertEqual(ui.state.filter_text, "rexo")
        self.assertEqual(ui.state.status, "filter: rexo")

        ui = CursesUi(
            FakeStdScr([27]),
            TuiState(dataset=dataset()).set_filter("repo"),
            TuiOptions(codex_home=Path("/tmp")),
        )

        ui.handle_key(ord("/"))

        self.assertEqual(ui.state.filter_text, "")
        self.assertEqual(ui.state.status, "filter cleared")

    def test_ctrl_s_opens_hidden_prompt(self) -> None:
        stdscr = FakeStdScr([27])
        ui = CursesUi(
            stdscr,
            TuiState(dataset=dataset(), status="keep"),
            TuiOptions(codex_home=Path("/tmp")),
        )

        ui.handle_key(SECRET_CODE_KEY)

        self.assertIn((23, 0, SECRET_PROMPT, 0), stdscr.writes)
        self.assertEqual(ui.state.status, "keep")

    def test_invalid_secret_code_returns_silently(self) -> None:
        stdscr = FakeStdScr([ord("x"), 10])
        ui = CursesUi(
            stdscr,
            TuiState(dataset=dataset(), status="keep"),
            TuiOptions(codex_home=Path("/tmp")),
        )

        ui.handle_key(SECRET_CODE_KEY)

        self.assertEqual(ui.state.status, "keep")
        self.assertEqual(ui.state.view, "overview")

    def test_secret_codes_route_to_private_effects(self) -> None:
        expected_effects = {
            "2109": EFFECT_BIRTHDAY,
            "1976": EFFECT_HEART,
            "2011": EFFECT_NYAN,
            "iamdeveloper": EFFECT_TRANS_FLAG,
            "claude": EFFECT_CLAUDE,
            "ClaUdE": EFFECT_CLAUDE,
            "pwned": EFFECT_PWNED,
        }
        for code, expected in expected_effects.items():
            with self.subTest(code=code):
                keys = [ord(char) for char in code] + [10]
                ui = CursesUi(
                    FakeStdScr(keys),
                    TuiState(dataset=dataset(), status="keep"),
                    TuiOptions(codex_home=Path("/tmp")),
                )

                with mock.patch(
                    "codex_token_usage.tui.secret_codes.render_secret_effect"
                ) as rendered:
                    ui.handle_key(SECRET_CODE_KEY)

                rendered.assert_called_once_with(ui, expected)
        self.assertEqual(ui.state.status, "keep")

    def test_secret_effect_stays_until_q_or_esc(self) -> None:
        for dismiss_key in (ord("q"), 27):
            with self.subTest(dismiss_key=dismiss_key):
                keys = [ord(char) for char in "1976"] + [10, dismiss_key]
                stdscr = FakeStdScr(keys)
                ui = CursesUi(
                    stdscr,
                    TuiState(dataset=dataset(), status="keep"),
                    TuiOptions(codex_home=Path("/tmp")),
                )

                with mock.patch("codex_token_usage.tui.secret_codes.curses.napms"):
                    ui.handle_key(SECRET_CODE_KEY)

                self.assertIn("     *     ", [write[2] for write in stdscr.writes])
        self.assertEqual(ui.state.status, "keep")

    def test_cake_and_nyan_loop_until_dismissal(self) -> None:
        cases = {
            "2109": ("     |    HAPPY 5TH    |", 90, (24, 80)),
            "2011": ("XXKKK00000000kxO000xxO000000KKXXO", 100, (38, 120)),
        }
        for code, (expected_line, expected_timeout, size) in cases.items():
            with self.subTest(code=code):
                keys = [ord(char) for char in code] + [10, ord("q")]
                stdscr = FakeStdScr(keys, size=size)
                ui = CursesUi(
                    stdscr,
                    TuiState(dataset=dataset(), status="keep"),
                    TuiOptions(codex_home=Path("/tmp")),
                )

                with mock.patch("codex_token_usage.tui.secret_codes.curses.napms"):
                    ui.handle_key(SECRET_CODE_KEY)

                self.assertTrue(
                    any(expected_line in text for _y, _x, text, _attr in stdscr.writes)
                )
                self.assertIn(expected_timeout, stdscr.timeouts)
                self.assertEqual(ui.state.status, "keep")

    def test_nyan_cat_uses_reference_frames_until_dismissal(self) -> None:
        keys = [ord(char) for char in "2011"] + [10, ord("q")]
        stdscr = FakeStdScr(keys, size=(38, 120))
        ui = CursesUi(
            stdscr,
            TuiState(dataset=dataset(), status="keep"),
            TuiOptions(codex_home=Path("/tmp")),
        )
        ui.preview_attr = lambda _rgb, base_attr=0: base_attr

        ui.handle_key(SECRET_CODE_KEY)

        self.assertIn(100, stdscr.timeouts)
        self.assertTrue(
            any(
                "XXKKK00000000kxO000xxO000000KKXXO" in text
                for _y, _x, text, _attr in stdscr.writes
            )
        )
        self.assertTrue(any(attr for _y, _x, _text, attr in stdscr.writes))
        self.assertEqual(ui.state.status, "keep")

    def test_nyan_cat_resizes_to_screen_width_with_320_column_cap(self) -> None:
        cases = (
            ((38, 80), 80),
            ((120, 400), 320),
        )
        for size, expected_width in cases:
            with self.subTest(size=size):
                keys = [ord(char) for char in "2011"] + [10, ord("q")]
                stdscr = FakeStdScr(keys, size=size)
                ui = CursesUi(
                    stdscr,
                    TuiState(dataset=dataset(), status="keep"),
                    TuiOptions(codex_home=Path("/tmp")),
                )
                ui.preview_attr = lambda _rgb, base_attr=0: base_attr

                ui.handle_key(SECRET_CODE_KEY)

                rendered_widths = {len(text) for _y, _x, text, _attr in stdscr.writes}
                self.assertEqual({expected_width}, rendered_widths)
                self.assertTrue(all(x >= 0 for _y, x, _text, _attr in stdscr.writes))
                self.assertEqual(ui.state.status, "keep")

    def test_pwned_secret_shows_fake_root_prompt_and_troll_responses(self) -> None:
        keys = (
            [ord(char) for char in "pwned"]
            + [10]
            + [ord(char) for char in "whoami"]
            + [10]
            + [ord(char) for char in "date"]
            + [10, ord("q")]
        )
        stdscr = FakeStdScr(keys, size=(24, 100))
        ui = CursesUi(
            stdscr,
            TuiState(dataset=dataset(), status="keep"),
            TuiOptions(codex_home=Path("/tmp")),
        )
        ui.preview_attr = lambda _rgb, base_attr=0: base_attr

        with mock.patch(
            "codex_token_usage.tui.secret_codes.socket.gethostname",
            return_value="academy",
        ), mock.patch("codex_token_usage.tui.secret_codes.curses.napms"):
            ui.handle_key(SECRET_CODE_KEY)

        rendered = [write[2] for write in stdscr.writes]
        self.assertIn("[+] success: pretend root shell established", rendered)
        self.assertIn("root@academy:~# whoami", rendered)
        self.assertIn("root@academy:~# date", rendered)
        self.assertTrue(any("you have been trolled" in text for text in rendered))
        self.assertTrue(any("modest elegance" in text for text in rendered))
        self.assertEqual(ui.state.status, "keep")

    def test_pwned_secret_uses_hacker_hostname_fallback(self) -> None:
        keys = [ord(char) for char in "pwned"] + [10, ord("q")]
        stdscr = FakeStdScr(keys, size=(24, 100))
        ui = CursesUi(
            stdscr,
            TuiState(dataset=dataset(), status="keep"),
            TuiOptions(codex_home=Path("/tmp")),
        )
        ui.preview_attr = lambda _rgb, base_attr=0: base_attr

        with mock.patch(
            "codex_token_usage.tui.secret_codes.socket.gethostname",
            side_effect=OSError,
        ), mock.patch("codex_token_usage.tui.secret_codes.curses.napms"):
            ui.handle_key(SECRET_CODE_KEY)

        self.assertIn("root@hacker:~# ", [write[2] for write in stdscr.writes])
        self.assertEqual(ui.state.status, "keep")

    def test_clawd_secret_code_renders_selected_flag_lobster_dance(self) -> None:
        keys = [ord(char) for char in "claude"] + [10, ord("q")]
        stdscr = FakeStdScr(keys, size=(28, 120))
        selected_theme = ThemeConfig(enabled=False, preset="rainbow")
        active_palette = theme_palette(ThemeConfig(enabled=True, preset="rainbow"))
        ui = CursesUi(
            stdscr,
            TuiState(dataset=dataset(), status="keep"),
            TuiOptions(codex_home=Path("/tmp"), theme=selected_theme),
        )
        if not active_palette:
            self.fail("rainbow palette missing from test fixture")

        def preview_attr(rgb: tuple[int, int, int], base_attr: int = 0) -> int:
            if rgb in active_palette:
                return base_attr + (active_palette.index(rgb) + 1) * 1000
            return base_attr

        ui.preview_attr = preview_attr

        ui.handle_key(SECRET_CODE_KEY)

        rendered = [text for _y, _x, text, _attr in stdscr.writes]
        self.assertTrue(any("(o o)" in text for text in rendered))
        self.assertTrue(any("CLAWD" in text for text in rendered))
        self.assertTrue(any("___" in text for text in rendered))
        self.assertIn(140, stdscr.timeouts)

        mascot_attrs = {
            attr
            for _y, _x, text, attr in stdscr.writes
            if text.strip()
        }
        expected_attrs = {
            curses.A_BOLD + (index + 1) * 1000
            for index, _rgb in enumerate(active_palette)
        }
        self.assertTrue(mascot_attrs)
        self.assertTrue(mascot_attrs.issubset(expected_attrs))
        self.assertEqual(ui.state.status, "keep")

    def test_trans_flag_waves_vertically_until_dismissal(self) -> None:
        cases = (
            ((24, 80), 6, 72, 11),
            ((40, 160), 12, 144, 21),
        )
        for size, segment_width, flag_width, flag_height in cases:
            with self.subTest(size=size):
                keys = [ord(char) for char in "iamdeveloper"] + [10, -1, -1, ord("q")]
                stdscr = FakeStdScr(keys, size=size)
                ui = CursesUi(
                    stdscr,
                    TuiState(dataset=dataset(), status="keep"),
                    TuiOptions(codex_home=Path("/tmp")),
                )
                ui.preview_attr = lambda _rgb, base_attr=0: base_attr

                ui.handle_key(SECRET_CODE_KEY)

                self.assertIn(140, stdscr.timeouts)
                rendered_rows = {y for y, _x, _text, _attr in stdscr.writes}
                self.assertEqual(flag_height, max(rendered_rows) - min(rendered_rows) + 1)
                self.assertEqual(
                    {segment_width},
                    {len(text) for _y, _x, text, _attr in stdscr.writes},
                )
                rendered_columns = {x for _y, x, _text, _attr in stdscr.writes}
                self.assertEqual(0, len(rendered_columns) % 2)
                self.assertEqual(flag_width, len(rendered_columns) * segment_width)
                self.assertTrue(
                    all(text.strip() == "" for _y, _x, text, _attr in stdscr.writes)
                )
                self.assertEqual(ui.state.status, "keep")

    def test_emergency_secret_codes_render_warning_and_crash(self) -> None:
        for code in sorted(EMERGENCY_CODES):
            with self.subTest(code=code):
                keys = [ord(char) for char in code] + [10, ord("q")]
                stdscr = FakeStdScr(keys)
                ui = CursesUi(
                    stdscr,
                    TuiState(dataset=dataset(), status="keep"),
                    TuiOptions(codex_home=Path("/tmp")),
                )

                with mock.patch(
                    "codex_token_usage.tui.secret_codes.curses.napms"
                ), self.assertRaises(SystemExit) as raised:
                    ui.handle_key(SECRET_CODE_KEY)

                self.assertEqual(raised.exception.code, EMERGENCY_EXIT_CODE)
                self.assertIsInstance(raised.exception, EmergencyCrash)
                self.assertIn(EMERGENCY_MESSAGE, [write[2] for write in stdscr.writes])
                self.assertTrue(ui._suppress_farewell)
                self.assertEqual(SECRET_CODE_EFFECTS[code], EFFECT_EMERGENCY)

    def test_emergency_crash_screen_renders_after_curses_shutdown(self) -> None:
        with mock.patch(
            "codex_token_usage.tui.app.load_usage",
            return_value=dataset(),
        ), mock.patch(
            "codex_token_usage.tui.app.curses.wrapper",
            side_effect=EmergencyCrash(),
        ), mock.patch(
            "codex_token_usage.tui.app.render_terminal_emergency_crash",
        ) as rendered:
            code = run_tui(TuiOptions(codex_home=Path("/tmp")))

        self.assertEqual(code, EMERGENCY_EXIT_CODE)
        rendered.assert_called_once_with()

        screen = emergency_crash_screen((8, 72))
        for line in EMERGENCY_CRASH_LINES:
            self.assertIn(line, screen)

    def test_custom_keymap_cannot_override_hidden_ctrl_s_handler(self) -> None:
        stdscr = FakeStdScr([ord("x"), 10])
        ui = CursesUi(
            stdscr,
            TuiState(dataset=dataset(), status="keep"),
            TuiOptions(codex_home=Path("/tmp")),
        )
        ui.keymap[SECRET_CODE_KEY] = "next_view"

        ui.handle_key(SECRET_CODE_KEY)

        self.assertEqual(ui.state.view, "overview")
        self.assertEqual(ui.state.status, "keep")
        self.assertIn((23, 0, SECRET_PROMPT, 0), stdscr.writes)

    def test_c_key_opens_settings_without_crashing(self) -> None:
        ui = CursesUi(
            FakeStdScr([ord("q")]),
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )

        ui.handle_key(ord("c"))

        self.assertEqual(ui.state.status, "settings canceled")

    def test_m_key_toggles_supported_display_modes(self) -> None:
        ui = CursesUi(
            None,
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )

        ui.handle_key(ord("m"))

        self.assertEqual(ui.state.statistic_display_mode, "table")
        self.assertEqual(
            ui.state.status,
            "Display mode is available on Statistic or By Project",
        )

        ui.state = ui.state.next_view()
        self.assertEqual(ui.state.view, "statistic")

        ui.handle_key(ord("m"))

        self.assertEqual(ui.state.statistic_display_mode, "line")
        self.assertEqual(ui.state.status, "Statistic display: line")

        ui.handle_key(ord("m"))

        self.assertEqual(ui.state.statistic_display_mode, "table")
        self.assertEqual(ui.state.status, "Statistic display: table")

        while ui.state.view != "projects":
            ui.state = ui.state.next_view()

        ui.handle_key(ord("m"))

        self.assertEqual(ui.state.project_display_mode, "models")
        self.assertEqual(ui.state.status, "Project display: models")

        ui.handle_key(ord("m"))

        self.assertEqual(ui.state.project_display_mode, "projects")
        self.assertEqual(ui.state.status, "Project display: projects")

    def test_curses_ui_captures_keybindings(self) -> None:
        ui = CursesUi(
            FakeStdScr([ord("n"), ord("x")]),
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
        self.assertEqual(keybindings.labels("next_view"), ("n", "x"))
        self.assertEqual(status, "Next view: n, x")

        ui = CursesUi(
            FakeStdScr([SECRET_CODE_KEY]),
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )
        keybindings, status = ui.apply_keybinding_setting(
            KeybindingConfig(),
            "next_view",
        )
        self.assertEqual(keybindings.labels("next_view"), ("Tab",))
        self.assertEqual(status, "Ctrl+S is reserved")

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
        self.assertEqual(display_setting_label("compact_token_counts"), "compact token columns")
        self.assertEqual(appearance_setting_label("themed_bars"), "themed usage bars")
        self.assertEqual(misc_setting_label("about"), "about")
        self.assertEqual(misc_setting_label("reset_setup"), "reset all setup")
        self.assertEqual(misc_setting_label("shutdown_seconds"), "shutdown time")
        self.assertEqual(prediction_algorithm_label("recent_rate"), "recent rate")
        self.assertEqual(auto_refresh_label(None), "off")
        self.assertEqual(auto_refresh_label(1), "1 second")
        self.assertEqual(auto_refresh_label(30), "30 seconds")
        self.assertEqual(shutdown_seconds_label(2.5), "2.5 seconds")
        self.assertEqual(parse_settings_rate("1.25"), 1.25)
        self.assertEqual(parse_settings_model_width("auto"), None)
        self.assertEqual(parse_settings_model_width("18"), 18)
        self.assertEqual(parse_settings_auto_refresh_seconds("off"), None)
        self.assertEqual(parse_settings_auto_refresh_seconds("30"), 30)
        self.assertIn(
            "whole number",
            parse_settings_auto_refresh_seconds("1.5"),
        )
        self.assertEqual(parse_settings_shutdown_seconds("2.5"), 2.5)
        self.assertIn("positive", parse_settings_shutdown_seconds("0"))
        base_snapshot = settings_snapshot(
            ThemeConfig(),
            DisplayConfig(),
            custom,
            KeybindingConfig(),
            LimitConfig(),
            PredictionConfig(),
            None,
            2.45,
        )
        changed_snapshot = settings_snapshot(
            ThemeConfig(),
            DisplayConfig(show_model=False),
            custom,
            KeybindingConfig(),
            LimitConfig(),
            PredictionConfig(),
            None,
            2.45,
        )
        self.assertNotEqual(base_snapshot, changed_snapshot)
        self.assertEqual(
            default_setup_values(),
            (
                ThemeConfig(),
                DisplayConfig(),
                {},
                KeybindingConfig(),
                LimitConfig(),
                PredictionConfig(),
                None,
                2.45,
            ),
        )

    def test_confirm_settings_action(self) -> None:
        ui = CursesUi(
            FakeStdScr([ord("y")]),
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )

        self.assertTrue(ui.confirm_settings_action("Save settings changes? y/N: "))

        ui = CursesUi(
            FakeStdScr([ord("n")]),
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )

        self.assertFalse(ui.confirm_settings_action("Save settings changes? y/N: "))

    def test_forecast_key_values(self) -> None:
        forecast = make_usage_forecast(
            dataset(),
            LimitConfig(five_hour_tokens=50, weekly_tokens=100),
            as_of=datetime.fromisoformat("2026-06-02T01:00:00+00:00"),
        )

        rows = forecast_key_values(forecast)

        self.assertEqual(rows[0][0], "5h forecast")
        self.assertIn("used 20 / 50", rows[0][1])
        self.assertEqual(rows[1][0], "Weekly forecast")
        self.assertIn("projected", rows[1][1])

        prediction_rows = prediction_key_values(forecast)
        self.assertEqual(prediction_rows[0][0], "Next 5h estimate")
        self.assertIn("tokens", prediction_rows[0][1])

    def test_current_usage_rate_rows_cover_5h_day_week_and_month(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sessions = (
                session(
                    "recent",
                    3600,
                    1800,
                    "/repo",
                    "2026-06-18T11:00:00+00:00",
                    root,
                    request_count=2,
                ),
                session(
                    "day",
                    3600,
                    1800,
                    "/repo",
                    "2026-06-18T01:00:00+00:00",
                    root,
                    request_count=1,
                ),
                session(
                    "week",
                    7200,
                    3600,
                    "/repo",
                    "2026-06-16T12:00:00+00:00",
                    root,
                    request_count=2,
                ),
                session(
                    "month",
                    14400,
                    7200,
                    "/repo",
                    "2026-06-03T12:00:00+00:00",
                    root,
                    request_count=4,
                ),
            )

        rows = current_usage_rate_rows(
            sessions,
            datetime.fromisoformat("2026-06-18T12:00:00+00:00"),
        )

        self.assertEqual(
            rows,
            [
                (
                    "Current 5h TPS/RPS",
                    "0.200 tok/s  0.000111 req/s  (3,600 tokens, 2 req)",
                ),
                (
                    "Current day TPS/RPS",
                    "0.167 tok/s  0.000069 req/s  (7,200 tokens, 3 req)",
                ),
                (
                    "Current week TPS/RPS",
                    "0.048 tok/s  0.000017 req/s  (14,400 tokens, 5 req)",
                ),
                (
                    "Current month TPS/RPS",
                    "0.019 tok/s  0.000006 req/s  (28,800 tokens, 9 req)",
                ),
            ],
        )

    def test_overview_renders_current_usage_rate_indicators(self) -> None:
        state = TuiState(
            dataset=dataset(
                loaded_at=datetime.fromisoformat("2026-06-02T01:00:00+00:00")
            ),
        )
        stdscr = FakeStdScr([], size=(60, 160))
        ui = CursesUi(stdscr, state, TuiOptions(codex_home=Path("/tmp")))

        ui.render_overview(40, 160)

        rendered = [text for _y, _x, text, _attr in stdscr.writes]
        labels = {text.strip() for text in rendered}
        self.assertIn("Current 5h TPS/RPS", labels)
        self.assertIn("Current day TPS/RPS", labels)
        self.assertIn("Current week TPS/RPS", labels)
        self.assertIn("Current month TPS/RPS", labels)
        self.assertTrue(any("tok/s" in text and "req/s" in text for text in rendered))

    def test_statistic_usage_rate_windows_use_rounded_complete_periods(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sessions = (
                session(
                    "stats",
                    0,
                    0,
                    "/repo",
                    "2026-06-18T12:34:00+00:00",
                    root,
                    usage_events=[
                        usage_event("2026-06-18T11:15:00+00:00", 3600),
                        usage_event("2026-06-18T11:45:00+00:00", 3600),
                        usage_event("2026-06-18T12:00:00+00:00", 9999),
                        usage_event("2026-06-18T08:00:00+00:00", 36000, requests=10),
                        usage_event("2026-06-17T06:00:00+00:00", 24000, requests=24),
                        usage_event("2026-06-10T12:00:00+00:00", 168000, requests=168),
                        usage_event("2026-05-20T12:00:00+00:00", 720000, requests=720),
                    ],
                ),
            )

        windows = statistic_usage_rate_windows(
            sessions,
            datetime.fromisoformat("2026-06-18T12:34:00+00:00"),
        )

        by_label = {window.label: window for window in windows}
        self.assertEqual(
            by_label["Last hour"].window_start.isoformat(),
            "2026-06-18T11:00:00+00:00",
        )
        self.assertEqual(
            by_label["Last hour"].window_end.isoformat(),
            "2026-06-18T12:00:00+00:00",
        )
        self.assertEqual(by_label["Last hour"].tokens, 7200)
        self.assertEqual(by_label["Last hour"].requests, 2)
        self.assertAlmostEqual(by_label["Last hour"].tps, 2.0)
        self.assertAlmostEqual(by_label["Last hour"].tpm, 120.0)
        self.assertAlmostEqual(by_label["Last hour"].tph, 7200.0)
        self.assertAlmostEqual(by_label["Last hour"].tpr, 3600.0)
        self.assertAlmostEqual(by_label["Last hour"].rph, 2.0)
        self.assertEqual(
            by_label["Last 5h"].window_start.isoformat(),
            "2026-06-18T07:00:00+00:00",
        )
        self.assertEqual(by_label["Last 5h"].tokens, 43200)
        self.assertAlmostEqual(by_label["Last 5h"].tph, 8640.0)
        self.assertAlmostEqual(by_label["Last 5h"].tpr, 3600.0)
        self.assertEqual(
            by_label["Last day"].window_start.isoformat(),
            "2026-06-17T00:00:00+00:00",
        )
        self.assertEqual(by_label["Last day"].tokens, 24000)
        self.assertAlmostEqual(by_label["Last day"].tph, 1000.0)
        self.assertEqual(
            by_label["Last week"].window_start.isoformat(),
            "2026-06-08T00:00:00+00:00",
        )
        self.assertEqual(by_label["Last week"].tokens, 168000)
        self.assertAlmostEqual(by_label["Last week"].tph, 1000.0)
        self.assertEqual(
            by_label["Last month"].window_start.isoformat(),
            "2026-05-01T00:00:00+00:00",
        )
        self.assertEqual(by_label["Last month"].tokens, 720000)
        self.assertAlmostEqual(by_label["Last month"].tph, 967.741935, places=6)

    def test_statistic_line_series_uses_ordered_tps_and_tpm_buckets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sessions = (
                session(
                    "series",
                    0,
                    0,
                    "/repo",
                    "2026-06-18T12:00:00+00:00",
                    root,
                    usage_events=[
                        usage_event("2026-06-18T11:00:00+00:00", 100),
                        usage_event("2026-06-18T11:59:00+00:00", 60),
                        usage_event("2026-06-18T11:59:30+00:00", 30),
                        usage_event("2026-06-18T11:59:58+00:00", 10),
                        usage_event("2026-06-18T11:59:58+00:00", 5),
                        usage_event("2026-06-18T11:59:59+00:00", 20),
                        usage_event("2026-06-18T12:00:00+00:00", 999),
                    ],
                ),
            )

        tps, tpm = statistic_line_series(
            sessions,
            datetime.fromisoformat("2026-06-18T12:00:00+00:00"),
        )

        self.assertEqual(tps.label, "TPS last 1m")
        self.assertEqual(tps.bucket_label, "1s")
        self.assertEqual(len(tps.values), 60)
        self.assertEqual(tps.values[-2:], (15.0, 20.0))
        self.assertEqual(tpm.label, "TPM last 1h")
        self.assertEqual(tpm.bucket_label, "1m")
        self.assertEqual(len(tpm.values), 60)
        self.assertEqual(tpm.values[0], 100.0)
        self.assertEqual(tpm.values[-1], 125.0)

    def test_statistic_tab_renders_rounded_rate_table(self) -> None:
        state = TuiState(
            dataset=dataset(
                loaded_at=datetime.fromisoformat("2026-06-18T12:00:00+00:00")
            )
        ).next_view()
        stdscr = FakeStdScr([], size=(60, 160))
        ui = CursesUi(stdscr, state, TuiOptions(codex_home=Path("/tmp")))

        ui.render()

        rendered = [text for _y, _x, text, _attr in stdscr.writes]
        self.assertIn(" Statistic ", rendered)
        self.assertTrue(any("rps" in text and "tpr" in text for text in rendered))
        self.assertTrue(any("Last hour" in text for text in rendered))

    def test_format_token_count_compacts_billion_and_trillion_values(self) -> None:
        self.assertEqual(format_token_count(1_000_000_000, 10), "1B")
        self.assertEqual(format_token_count(1_000_000_000_000, 10), "1T")
        self.assertEqual(format_token_count(10_500_000_000, 10), "10.5B")

    def test_sessions_view_uses_full_token_display_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            usage_dataset = UsageDataset(
                sessions=(
                    session(
                        "trillion",
                        1_000_000_000_000,
                        500_000_000_000,
                        "/repo",
                        "2026-06-01T00:00:00+00:00",
                        root,
                        model="gpt-5",
                    ),
                    session(
                        "billion",
                        1_000_000_000,
                        500_000_000,
                        "/repo",
                        "2026-06-02T00:00:00+00:00",
                        root,
                        model="gpt-4",
                    ),
                ),
                codex_home=root,
                loaded_at=datetime.now(timezone.utc),
                sqlite_available=False,
            )
        state = TuiState(dataset=usage_dataset)
        while state.view != "sessions":
            state = state.next_view()
        stdscr = FakeStdScr([], size=(24, 160))
        ui = CursesUi(
            stdscr,
            state,
            TuiOptions(
                codex_home=Path("/tmp"),
                display=DisplayConfig(show_context=False, show_model=False),
            ),
        )

        ui.render()

        row_parts: dict[int, list[tuple[int, str]]] = {}
        for y, x, text, _attr in stdscr.writes:
            if y < 5:
                continue
            row_parts.setdefault(y, []).append((x, text))

        session_lines = [
            "".join(chunk for _, chunk in sorted(chunks))
            for y, chunks in sorted(row_parts.items())
            if y >= 5
        ][:2]
        rendered_lines = " ".join(session_lines)
        self.assertIn("1,000,000,000,000", rendered_lines)
        self.assertIn("1,000,000,000", rendered_lines)
        self.assertNotIn(" 1T ", rendered_lines)
        self.assertNotIn(" 1B ", rendered_lines)

    def test_sessions_view_can_toggle_compact_token_display(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            usage_dataset = UsageDataset(
                sessions=(
                    session(
                        "trillion",
                        1_000_000_000_000,
                        500_000_000_000,
                        "/repo",
                        "2026-06-01T00:00:00+00:00",
                        root,
                        model="gpt-5",
                    ),
                    session(
                        "billion",
                        1_000_000_000,
                        500_000_000,
                        "/repo",
                        "2026-06-02T00:00:00+00:00",
                        root,
                        model="gpt-4",
                    ),
                ),
                codex_home=root,
                loaded_at=datetime.now(timezone.utc),
                sqlite_available=False,
            )
        state = TuiState(dataset=usage_dataset)
        while state.view != "sessions":
            state = state.next_view()
        stdscr = FakeStdScr([], size=(24, 160))
        ui = CursesUi(
            stdscr,
            state,
            TuiOptions(
                codex_home=Path("/tmp"),
                display=DisplayConfig(
                    show_context=False,
                    show_model=False,
                    compact_token_counts=True,
                ),
            ),
        )

        ui.render()

        row_parts: dict[int, list[tuple[int, str]]] = {}
        for y, x, text, _attr in stdscr.writes:
            if y < 5:
                continue
            row_parts.setdefault(y, []).append((x, text))

        session_lines = [
            "".join(chunk for _, chunk in sorted(chunks))
            for y, chunks in sorted(row_parts.items())
            if y >= 5
        ][:2]
        rendered_lines = " ".join(session_lines)
        self.assertIn("1T", rendered_lines)
        self.assertIn("1B", rendered_lines)
        self.assertNotIn("1,000,000,000,000", rendered_lines)
        self.assertNotIn("1,000,000,000", rendered_lines)

    def test_project_view_defaults_to_project_only_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            usage_dataset = UsageDataset(
                sessions=(
                    session(
                        "repo-gpt",
                        100,
                        80,
                        "/repo",
                        "2026-06-01T00:00:00+00:00",
                        root,
                        model="gpt-5",
                    ),
                    session(
                        "repo-o4",
                        40,
                        30,
                        "/repo",
                        "2026-06-02T00:00:00+00:00",
                        root,
                        model="o4-mini",
                    ),
                    session(
                        "other",
                        200,
                        100,
                        "/other",
                        "2026-06-03T00:00:00+00:00",
                        root,
                        model="gpt-5",
                    ),
                ),
                codex_home=root,
                loaded_at=datetime.now(timezone.utc),
                sqlite_available=False,
            )
        state = TuiState(dataset=usage_dataset)
        while state.view != "projects":
            state = state.next_view()
        stdscr = FakeStdScr([], size=(60, 160))
        ui = CursesUi(stdscr, state, TuiOptions(codex_home=Path("/tmp")))

        ui.render()

        rendered = [text for _y, _x, text, _attr in stdscr.writes]
        labels_by_y = {
            y: text
            for y, x, text, _attr in stdscr.writes
            if x == 0 and y >= 5
        }
        self.assertTrue(
            any(text.startswith(">/other") for text in labels_by_y.values())
        )
        self.assertTrue(
            any(text.startswith(" /repo") for text in labels_by_y.values())
        )
        self.assertFalse(any("gpt-5" in text for text in labels_by_y.values()))
        self.assertFalse(any("o4-mini" in text for text in labels_by_y.values()))
        self.assertTrue(any("mode=projects" in text for text in rendered))

    def test_model_view_renders_grouped_model_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            usage_dataset = UsageDataset(
                sessions=(
                    session(
                        "repo-gpt",
                        100,
                        80,
                        "/repo",
                        "2026-06-01T00:00:00+00:00",
                        root,
                        model="gpt-5",
                    ),
                    session(
                        "repo-o4",
                        40,
                        30,
                        "/repo",
                        "2026-06-02T00:00:00+00:00",
                        root,
                        model="o4-mini",
                    ),
                    session(
                        "other",
                        200,
                        100,
                        "/other",
                        "2026-06-03T00:00:00+00:00",
                        root,
                        model="gpt-5",
                    ),
                ),
                codex_home=root,
                loaded_at=datetime.now(timezone.utc),
                sqlite_available=False,
            )
        state = TuiState(dataset=usage_dataset)
        while state.view != "models":
            state = state.next_view()
        stdscr = FakeStdScr([], size=(60, 160))
        ui = CursesUi(stdscr, state, TuiOptions(codex_home=Path("/tmp")))

        ui.render()

        rendered = [text for _y, _x, text, _attr in stdscr.writes]
        labels_by_y = {
            y: text
            for y, x, text, _attr in stdscr.writes
            if x == 0 and y >= 5
        }
        self.assertIn(" By Model ", rendered)
        self.assertTrue(any(text.startswith("gpt-5") for text in labels_by_y.values()))
        self.assertTrue(
            any(text.startswith("o4-mini") for text in labels_by_y.values())
        )
        self.assertTrue(any("model" in text and "usage" in text for text in rendered))

    def test_project_view_can_render_indented_model_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            usage_dataset = UsageDataset(
                sessions=(
                    session(
                        "repo-gpt",
                        100,
                        80,
                        "/repo",
                        "2026-06-01T00:00:00+00:00",
                        root,
                        model="gpt-5",
                    ),
                    session(
                        "repo-o4",
                        40,
                        30,
                        "/repo",
                        "2026-06-02T00:00:00+00:00",
                        root,
                        model="o4-mini",
                    ),
                    session(
                        "other",
                        200,
                        100,
                        "/other",
                        "2026-06-03T00:00:00+00:00",
                        root,
                        model="gpt-5",
                    ),
                ),
                codex_home=root,
                loaded_at=datetime.now(timezone.utc),
                sqlite_available=False,
            )
        state = TuiState(dataset=usage_dataset)
        while state.view != "projects":
            state = state.next_view()
        state = state.cycle_display_mode()
        stdscr = FakeStdScr([], size=(60, 160))
        ui = CursesUi(stdscr, state, TuiOptions(codex_home=Path("/tmp")))

        ui.render()

        rendered = [text for _y, _x, text, _attr in stdscr.writes]
        labels_by_y = {
            y: text
            for y, x, text, _attr in stdscr.writes
            if x == 0 and y >= 5
        }
        repo_y = next(
            y for y, text in labels_by_y.items() if text.startswith(" /repo")
        )
        self.assertTrue(labels_by_y[repo_y + 1].startswith("   gpt-5"))
        self.assertTrue(labels_by_y[repo_y + 2].startswith("   o4-mini"))
        self.assertTrue(any("mode=models" in text for text in rendered))

    def test_project_details_renders_model_breakdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            usage_dataset = UsageDataset(
                sessions=(
                    session(
                        "repo-gpt",
                        100,
                        80,
                        "/repo",
                        "2026-06-01T00:00:00+00:00",
                        root,
                        model="gpt-5",
                    ),
                    session(
                        "repo-o4",
                        40,
                        30,
                        "/repo",
                        "2026-06-02T00:00:00+00:00",
                        root,
                        model="o4-mini",
                    ),
                    session(
                        "other",
                        200,
                        100,
                        "/other",
                        "2026-06-03T00:00:00+00:00",
                        root,
                        model="gpt-5",
                    ),
                ),
                codex_home=root,
                loaded_at=datetime.now(timezone.utc),
                sqlite_available=False,
            )
        state = TuiState(dataset=usage_dataset)
        while state.view != "projects":
            state = state.next_view()
        state = state.move_selection(1).open_details()
        stdscr = FakeStdScr([], size=(60, 160))
        ui = CursesUi(stdscr, state, TuiOptions(codex_home=Path("/tmp")))

        ui.render()

        rendered = [text for _y, _x, text, _attr in stdscr.writes]
        self.assertTrue(any(text.strip() == "Project" for text in rendered))
        self.assertTrue(any(text.strip() == "/repo" for text in rendered))
        self.assertTrue(any(text.startswith("model") for text in rendered))
        self.assertTrue(any(text.startswith("gpt-5") for text in rendered))
        self.assertTrue(any(text.startswith("o4-mini") for text in rendered))

    def test_statistic_tab_renders_line_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            usage_dataset = UsageDataset(
                sessions=(
                    session(
                        "stats",
                        0,
                        0,
                        "/repo",
                        "2026-06-18T12:00:00+00:00",
                        root,
                        usage_events=[
                            usage_event("2026-06-18T11:15:00+00:00", 3600),
                            usage_event("2026-06-18T11:45:00+00:00", 3600),
                        ],
                    ),
                ),
                codex_home=root,
                loaded_at=datetime.fromisoformat("2026-06-18T12:00:00+00:00"),
                sqlite_available=False,
            )
        state = TuiState(
            dataset=usage_dataset,
            statistic_display_mode="line",
        ).next_view()
        stdscr = FakeStdScr([], size=(60, 160))
        ui = CursesUi(stdscr, state, TuiOptions(codex_home=Path("/tmp")))

        ui.render()

        rendered = [text for _y, _x, text, _attr in stdscr.writes]
        chart_rows = [
            text
            for text in rendered
            if "│" in text or "┌" in text or "└" in text
        ]
        self.assertIn("Statistic line chart", rendered)
        self.assertTrue(any("TPS last 1m" in text for text in rendered))
        self.assertTrue(any("TPM last 1h" in text for text in rendered))
        self.assertTrue(any("│" in text for text in chart_rows))
        self.assertTrue(any("┌" in text and "─" in text for text in chart_rows))
        self.assertGreaterEqual(max(len(text) for text in chart_rows), 150)
        self.assertTrue(any("older" in text and "now" in text for text in rendered))
        self.assertTrue(
            any(
                any("\u2801" <= char <= "\u28ff" for char in text)
                for text in chart_rows
            )
        )
        self.assertFalse(any("/" in text or "\\" in text for text in chart_rows))

    def test_statistic_line_mode_handles_zero_data(self) -> None:
        state = TuiState(
            dataset=dataset(
                loaded_at=datetime.fromisoformat("2026-06-18T12:00:00+00:00")
            ),
            statistic_display_mode="line",
        ).next_view()
        stdscr = FakeStdScr([], size=(40, 160))
        ui = CursesUi(stdscr, state, TuiOptions(codex_home=Path("/tmp")))

        ui.render()

        rendered = [text for _y, _x, text, _attr in stdscr.writes]
        chart_rows = [
            text
            for text in rendered
            if "│" in text or "┌" in text or "└" in text
        ]
        self.assertIn("Statistic line chart", rendered)
        self.assertTrue(any("TPS last 1m" in text for text in rendered))
        self.assertTrue(any("│" in text for text in chart_rows))
        self.assertTrue(any("┌" in text and "─" in text for text in chart_rows))
        self.assertTrue(any("older" in text and "now" in text for text in rendered))
        self.assertTrue(
            any(
                any("\u2801" <= char <= "\u28ff" for char in text)
                for text in chart_rows
            )
        )

    def test_prediction_algorithm_cycles_from_misc_setting(self) -> None:
        prediction = cycle_prediction_algorithm(PredictionConfig())
        self.assertEqual(prediction.algorithm, "previous_period")

        ui = CursesUi(
            None,
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )
        (
            prediction,
            auto_refresh_seconds,
            shutdown_seconds,
            status,
        ) = ui.apply_misc_setting(
            PredictionConfig(),
            None,
            2.45,
            "prediction_algorithm",
        )

        self.assertEqual(prediction.algorithm, "previous_period")
        self.assertIsNone(auto_refresh_seconds)
        self.assertEqual(shutdown_seconds, 2.45)
        self.assertEqual(status, "prediction algorithm: previous period")

    def test_auto_refresh_timeout_calculation(self) -> None:
        ui = CursesUi(
            None,
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp"), auto_refresh_seconds=10),
        )

        ui.next_auto_refresh_at = 15.0
        self.assertEqual(ui.next_input_timeout_ms(10.0), 5000)
        self.assertEqual(ui.next_input_timeout_ms(15.0), 0)

        ui = CursesUi(
            None,
            TuiState(dataset=dataset()),
            TuiOptions(codex_home=Path("/tmp")),
        )
        self.assertEqual(ui.next_input_timeout_ms(10.0), -1)

    def test_settings_theme_helpers(self) -> None:
        theme = ThemeConfig(enabled=False, preset="rainbow", color_mode="8bit")

        self.assertEqual(theme_preset_label(theme), "plain")
        self.assertEqual(theme_current_preset(theme), "rainbow")
        self.assertEqual(theme_current_preset_label(theme), "rainbow (plain)")
        self.assertEqual(theme_current_preset(ThemeConfig(preset="")), "femboy")
        self.assertEqual(flag_display_name("trans"), "transgender")
        self.assertEqual(
            pride_community_message(ThemeConfig(enabled=True, preset="trans")),
            "Pride: transgender community, you belong here; be yourself and be proud to be there.",
        )
        about_lines = about_content_lines(ThemeConfig(enabled=True, preset="trans"), 34)
        joined_about = " ".join(about_lines)
        self.assertIn(ABOUT_DESCRIPTION, joined_about)
        self.assertIn("transgender community", joined_about)
        self.assertTrue(all(len(line) <= 34 for line in about_lines))
        farewell_lines = farewell_content_lines(
            ThemeConfig(enabled=True, preset="trans"),
            34,
        )
        joined_farewell = " ".join(farewell_lines)
        self.assertIn("Bye bye", joined_farewell)
        self.assertIn("transgender flag", joined_farewell)
        self.assertIn(OFFBOARD_MESSAGE, joined_farewell)
        self.assertTrue(all(len(line) <= 34 for line in farewell_lines))
        self.assertEqual(
            pride_message_for_preset("all"),
            "Pride: every community in this app belongs here; be yourself and be proud to be there.",
        )
        self.assertEqual(
            pride_messages_for_presets(("trans",)),
            (
                "Pride: transgender community, you belong here; be yourself and be proud to be there.",
            ),
        )
        for preset in PRESET_NAMES:
            message = pride_message_for_preset(preset)
            self.assertIn("Pride:", message)
            if preset != "all":
                self.assertIn(flag_display_name(preset), message)
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


def dataset(
    extra: bool = False,
    count: int | None = None,
    loaded_at: datetime | None = None,
) -> UsageDataset:
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
            loaded_at=loaded_at or datetime.now(timezone.utc),
            sqlite_available=False,
        )


def session(
    session_id: str,
    total: int,
    input_tokens: int,
    cwd: str,
    updated_at: str,
    root: Path,
    request_count: int = 0,
    usage_events: list[UsageEvent] | None = None,
    model: str = "gpt-5",
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
            model=model,
            cwd=cwd,
            created_at=updated,
            updated_at=updated,
        ),
        has_token_event=True,
        request_count=request_count,
        usage_events=tuple(usage_events or ()),
    )


def usage_event(
    occurred_at: str,
    total_tokens: int,
    requests: int = 1,
) -> UsageEvent:
    return UsageEvent(
        occurred_at=datetime.fromisoformat(occurred_at),
        tokens=TokenBreakdown(total_tokens=total_tokens),
        requests=requests,
    )


class FakeStdScr:
    def __init__(self, keys: list[int], size: tuple[int, int] = (24, 80)) -> None:
        self.keys = keys
        self.size = size
        self.writes: list[tuple[int, int, str, int]] = []
        self.timeouts: list[int] = []

    def getmaxyx(self) -> tuple[int, int]:
        return self.size

    def move(self, _y: int, _x: int) -> None:
        return None

    def clrtoeol(self) -> None:
        return None

    def addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        self.writes.append((y, x, text, attr))

    def erase(self) -> None:
        self.writes.clear()

    def timeout(self, value: int) -> None:
        self.timeouts.append(value)

    def refresh(self) -> None:
        return None

    def getch(self) -> int:
        return self.keys.pop(0) if self.keys else -1


if __name__ == "__main__":
    unittest.main()
