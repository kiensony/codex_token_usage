from __future__ import annotations

import unittest

from codex_token_usage.keybindings import (
    KeybindingConfig,
    key_codes_for_label,
    key_label_for_code,
    normalize_key_label,
    parse_keybinding_text,
    reset_keybinding,
    update_keybinding,
)


class KeybindingTests(unittest.TestCase):
    def test_parse_named_printable_and_control_keys(self) -> None:
        self.assertEqual(normalize_key_label("PgUp"), "PageUp")
        self.assertEqual(normalize_key_label("ctrl+x"), "Ctrl+X")
        self.assertEqual(normalize_key_label("S"), "S")
        self.assertEqual(key_codes_for_label("Ctrl+A"), (1,))
        self.assertEqual(key_label_for_code(1), "Ctrl+A")
        self.assertEqual(key_label_for_code(ord(",")), "Comma")
        self.assertEqual(parse_keybinding_text("n, Ctrl+X"), ("n", "Ctrl+X"))

    def test_empty_and_unknown_key_labels_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_keybinding_text("")
        with self.assertRaises(ValueError):
            parse_keybinding_text("NotAKey")

    def test_conflicting_bindings_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            update_keybinding(KeybindingConfig(), "next_view", ("j",))

    def test_update_keybinding_returns_normalized_config(self) -> None:
        config = update_keybinding(KeybindingConfig(), "next_view", ("n", "Ctrl+X"))

        self.assertEqual(config.labels("next_view"), ("n", "Ctrl+X"))
        self.assertEqual(config.labels("move_down"), ("Down", "j"))

    def test_reset_keybinding_returns_action_to_default(self) -> None:
        config = update_keybinding(KeybindingConfig(), "next_view", ("n",))
        config = reset_keybinding(config, "next_view")

        self.assertEqual(config.labels("next_view"), ("Tab",))


if __name__ == "__main__":
    unittest.main()
