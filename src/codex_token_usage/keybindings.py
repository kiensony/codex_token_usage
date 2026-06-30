from __future__ import annotations

import curses
from dataclasses import dataclass


KEYBINDING_ACTIONS = (
    "next_view",
    "previous_view",
    "move_down",
    "move_up",
    "page_down",
    "page_up",
    "select_first",
    "select_last",
    "open_details",
    "cycle_sort",
    "toggle_sort_direction",
    "cycle_date_preset",
    "show_all_time",
    "shift_date_backward",
    "shift_date_forward",
    "reload",
    "open_settings",
    "open_about",
    "filter",
    "help",
    "back",
    "back_or_quit",
    "quit",
)

KEYBINDING_ACTION_LABELS = {
    "next_view": "Next view",
    "previous_view": "Previous view",
    "move_down": "Move selection down",
    "move_up": "Move selection up",
    "page_down": "Page selection down",
    "page_up": "Page selection up",
    "select_first": "Select first session",
    "select_last": "Select last session",
    "open_details": "Open selected details",
    "cycle_sort": "Cycle sort field",
    "toggle_sort_direction": "Reverse sort direction",
    "cycle_date_preset": "Cycle date range",
    "show_all_time": "Show all time",
    "shift_date_backward": "Shift date range backward",
    "shift_date_forward": "Shift date range forward",
    "reload": "Reload data",
    "open_settings": "Open settings",
    "open_about": "Open about",
    "filter": "Filter sessions",
    "help": "Open help",
    "back": "Back from details",
    "back_or_quit": "Back from details or quit",
    "quit": "Quit",
}

DEFAULT_KEYBINDINGS: dict[str, tuple[str, ...]] = {
    "next_view": ("Tab",),
    "previous_view": ("Shift+Tab",),
    "move_down": ("Down", "j"),
    "move_up": ("Up", "k"),
    "page_down": ("PageDown",),
    "page_up": ("PageUp",),
    "select_first": ("Home",),
    "select_last": ("End",),
    "open_details": ("Enter",),
    "cycle_sort": ("s",),
    "toggle_sort_direction": ("S",),
    "cycle_date_preset": ("d",),
    "show_all_time": ("A",),
    "shift_date_backward": ("[",),
    "shift_date_forward": ("]",),
    "reload": ("r",),
    "open_settings": ("c",),
    "open_about": ("a",),
    "filter": ("/",),
    "help": ("?",),
    "back": ("Backspace",),
    "back_or_quit": ("Esc",),
    "quit": ("q", "Ctrl+C"),
}
DEFAULT_KEYBINDING_ITEMS = tuple(
    (action, DEFAULT_KEYBINDINGS[action]) for action in KEYBINDING_ACTIONS
)

NAMED_KEY_CODES: dict[str, tuple[str, tuple[int, ...]]] = {
    "tab": ("Tab", (9,)),
    "shift+tab": ("Shift+Tab", (curses.KEY_BTAB,)),
    "backtab": ("Shift+Tab", (curses.KEY_BTAB,)),
    "btab": ("Shift+Tab", (curses.KEY_BTAB,)),
    "enter": ("Enter", (10, 13, curses.KEY_ENTER)),
    "return": ("Enter", (10, 13, curses.KEY_ENTER)),
    "esc": ("Esc", (27,)),
    "escape": ("Esc", (27,)),
    "backspace": ("Backspace", (curses.KEY_BACKSPACE, 127, 8)),
    "bs": ("Backspace", (curses.KEY_BACKSPACE, 127, 8)),
    "up": ("Up", (curses.KEY_UP,)),
    "arrowup": ("Up", (curses.KEY_UP,)),
    "down": ("Down", (curses.KEY_DOWN,)),
    "arrowdown": ("Down", (curses.KEY_DOWN,)),
    "left": ("Left", (curses.KEY_LEFT,)),
    "arrowleft": ("Left", (curses.KEY_LEFT,)),
    "right": ("Right", (curses.KEY_RIGHT,)),
    "arrowright": ("Right", (curses.KEY_RIGHT,)),
    "pageup": ("PageUp", (curses.KEY_PPAGE,)),
    "pgup": ("PageUp", (curses.KEY_PPAGE,)),
    "pagedown": ("PageDown", (curses.KEY_NPAGE,)),
    "pgdn": ("PageDown", (curses.KEY_NPAGE,)),
    "home": ("Home", (curses.KEY_HOME,)),
    "end": ("End", (curses.KEY_END,)),
    "space": ("Space", (ord(" "),)),
    "comma": ("Comma", (ord(","),)),
}


@dataclass(frozen=True)
class KeybindingConfig:
    bindings: tuple[tuple[str, tuple[str, ...]], ...] = DEFAULT_KEYBINDING_ITEMS

    def as_dict(self) -> dict[str, tuple[str, ...]]:
        values = {action: labels for action, labels in DEFAULT_KEYBINDING_ITEMS}
        values.update(dict(self.bindings))
        return values

    def labels(self, action: str) -> tuple[str, ...]:
        return self.as_dict()[action]


def parse_keybindings_config(raw: object) -> KeybindingConfig:
    if not isinstance(raw, dict):
        raise ValueError("config must be a JSON object")

    raw_keybindings = raw.get("keybindings", {})
    if raw_keybindings in (None, ""):
        raw_keybindings = {}
    if not isinstance(raw_keybindings, dict):
        raise ValueError("keybindings must be a JSON object")

    bindings = {action: labels for action, labels in DEFAULT_KEYBINDING_ITEMS}
    for action, raw_labels in raw_keybindings.items():
        if action not in DEFAULT_KEYBINDINGS:
            raise ValueError(f"unknown keybinding action: {action}")
        parsed_labels = parse_keybinding_value(raw_labels, action)
        if (
            action == "show_all_time"
            and parsed_labels == ("a",)
            and "open_about" not in raw_keybindings
        ):
            parsed_labels = DEFAULT_KEYBINDINGS["show_all_time"]
        bindings[str(action)] = parsed_labels
    return make_keybinding_config(bindings)


def parse_keybinding_value(value: object, action: str = "keybinding") -> tuple[str, ...]:
    if isinstance(value, str):
        labels = split_keybinding_text(value)
    elif isinstance(value, list):
        labels = tuple(str(item) for item in value)
    else:
        raise ValueError(f"{action} must be a string or list of strings")
    return normalize_key_labels(labels, action)


def parse_keybinding_text(value: str, action: str = "keybinding") -> tuple[str, ...]:
    return normalize_key_labels(split_keybinding_text(value), action)


def split_keybinding_text(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def normalize_key_labels(labels: tuple[str, ...], action: str) -> tuple[str, ...]:
    if not labels:
        raise ValueError(f"{action} must have at least one key")
    normalized = tuple(normalize_key_label(label) for label in labels)
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{action} has duplicate keys")
    return normalized


def make_keybinding_config(bindings: dict[str, tuple[str, ...]]) -> KeybindingConfig:
    complete = {action: labels for action, labels in DEFAULT_KEYBINDING_ITEMS}
    complete.update(bindings)
    validate_keybindings(complete)
    return KeybindingConfig(
        bindings=tuple((action, complete[action]) for action in KEYBINDING_ACTIONS)
    )


def update_keybinding(
    config: KeybindingConfig,
    action: str,
    labels: tuple[str, ...],
) -> KeybindingConfig:
    if action not in DEFAULT_KEYBINDINGS:
        raise ValueError(f"unknown keybinding action: {action}")
    bindings = config.as_dict()
    bindings[action] = normalize_key_labels(labels, action)
    return make_keybinding_config(bindings)


def reset_keybinding(config: KeybindingConfig, action: str) -> KeybindingConfig:
    if action not in DEFAULT_KEYBINDINGS:
        raise ValueError(f"unknown keybinding action: {action}")
    bindings = config.as_dict()
    bindings[action] = DEFAULT_KEYBINDINGS[action]
    return make_keybinding_config(bindings)


def validate_keybindings(bindings: dict[str, tuple[str, ...]]) -> None:
    seen_codes: dict[int, str] = {}
    for action in KEYBINDING_ACTIONS:
        labels = bindings.get(action)
        if labels is None:
            raise ValueError(f"missing keybinding action: {action}")
        if not labels:
            raise ValueError(f"{action} must have at least one key")
        for label in labels:
            for code in key_codes_for_label(label):
                existing = seen_codes.get(code)
                if existing is not None and existing != action:
                    raise ValueError(
                        f"{label} is assigned to both {existing} and {action}"
                    )
                seen_codes[code] = action


def keymap_for_config(config: KeybindingConfig) -> dict[int, str]:
    keymap: dict[int, str] = {}
    bindings = config.as_dict()
    validate_keybindings(bindings)
    for action in KEYBINDING_ACTIONS:
        for label in bindings[action]:
            for code in key_codes_for_label(label):
                keymap[code] = action
    return keymap


def normalize_key_label(label: str) -> str:
    text = label.strip()
    if not text:
        raise ValueError("key label must not be empty")
    named = NAMED_KEY_CODES.get(text.lower().replace(" ", ""))
    if named is not None:
        return named[0]
    if text.lower().startswith("ctrl+"):
        letter = text[5:].strip()
        if len(letter) == 1 and "a" <= letter.lower() <= "z":
            return f"Ctrl+{letter.upper()}"
        raise ValueError(f"unknown key label: {label}")
    if len(text) == 1 and 32 <= ord(text) <= 126:
        return text
    raise ValueError(f"unknown key label: {label}")


def key_codes_for_label(label: str) -> tuple[int, ...]:
    normalized = normalize_key_label(label)
    named = NAMED_KEY_CODES.get(normalized.lower().replace(" ", ""))
    if named is not None:
        return named[1]
    if normalized.startswith("Ctrl+"):
        letter = normalized[-1]
        return (ord(letter) - ord("@"),)
    if len(normalized) == 1:
        return (ord(normalized),)
    raise ValueError(f"unknown key label: {label}")


def key_label_for_code(code: int) -> str | None:
    for _name, (label, codes) in NAMED_KEY_CODES.items():
        if code in codes:
            return label
    if 1 <= code <= 26:
        return f"Ctrl+{chr(code + ord('@'))}"
    if 32 <= code <= 126:
        return chr(code)
    return None


def format_keybinding_labels(labels: tuple[str, ...]) -> str:
    return ", ".join(labels)


def format_keybinding_config(config: KeybindingConfig, action: str) -> str:
    return format_keybinding_labels(config.labels(action))
