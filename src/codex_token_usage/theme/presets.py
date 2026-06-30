from __future__ import annotations

import json
from importlib.resources import files

RGB = tuple[int, int, int]

def parse_hex_color(value: str) -> RGB:
    text = value.removeprefix("#")
    if len(text) != 6:
        raise ValueError(f"invalid color: {value}")
    return (
        int(text[0:2], 16),
        int(text[2:4], 16),
        int(text[4:6], 16),
    )


def load_flag_presets() -> dict[str, tuple[RGB, ...]]:
    try:
        raw = json.loads(
            files(__package__).joinpath("flag_presets.json").read_text("utf-8")
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return {}

    presets: dict[str, tuple[RGB, ...]] = {}
    for name, value in raw.items():
        colors = value.get("colors") if isinstance(value, dict) else value
        if not isinstance(colors, list):
            continue
        try:
            presets[str(name)] = tuple(parse_hex_color(str(color)) for color in colors)
        except ValueError:
            continue
    return presets

PRESETS: dict[str, tuple[RGB, ...]] = {
    "rainbow": (
        (228, 3, 3),
        (255, 140, 0),
        (255, 237, 0),
        (0, 128, 38),
        (0, 77, 255),
        (117, 7, 135),
    ),
    "progress": (
        (0, 0, 0),
        (120, 79, 23),
        (228, 3, 3),
        (255, 140, 0),
        (255, 237, 0),
        (0, 128, 38),
        (0, 77, 255),
        (117, 7, 135),
        (91, 206, 250),
        (245, 169, 184),
        (255, 255, 255),
    ),
    "trans": (
        (91, 206, 250),
        (245, 169, 184),
        (255, 255, 255),
        (245, 169, 184),
        (91, 206, 250),
    ),
    "bisexual": (
        (214, 2, 112),
        (155, 79, 150),
        (0, 56, 168),
    ),
    "pansexual": (
        (255, 33, 140),
        (255, 216, 0),
        (33, 177, 255),
    ),
    "polysexual": (
        (246, 28, 135),
        (7, 214, 105),
        (28, 146, 246),
    ),
    "omnisexual": (
        (254, 155, 203),
        (255, 83, 173),
        (32, 31, 66),
        (103, 79, 163),
        (139, 184, 232),
    ),
    "omniromantic": (
        (255, 156, 203),
        (255, 221, 238),
        (32, 31, 66),
        (190, 224, 255),
        (128, 179, 255),
    ),
    "genderfluid": (
        (255, 117, 162),
        (255, 255, 255),
        (190, 24, 214),
        (0, 0, 0),
        (51, 62, 189),
    ),
    "lesbian": (
        (213, 45, 0),
        (239, 118, 39),
        (255, 255, 255),
        (209, 98, 164),
        (163, 2, 98),
    ),
    "gay-men": (
        (7, 141, 112),
        (38, 206, 170),
        (152, 232, 193),
        (255, 255, 255),
        (123, 173, 226),
        (80, 73, 204),
        (61, 26, 120),
    ),
    "nonbinary": (
        (255, 244, 48),
        (255, 255, 255),
        (156, 89, 209),
        (0, 0, 0),
    ),
    "agender": (
        (0, 0, 0),
        (188, 188, 188),
        (255, 255, 255),
        (184, 244, 131),
        (255, 255, 255),
        (188, 188, 188),
        (0, 0, 0),
    ),
    "xenogender": (
        (255, 102, 153),
        (255, 153, 51),
        (255, 255, 255),
        (102, 204, 255),
        (153, 102, 204),
    ),
    "queer": (
        (0, 0, 0),
        (153, 51, 153),
        (255, 255, 255),
        (0, 153, 102),
        (0, 0, 0),
    ),
    "abrosexual": (
        (117, 222, 141),
        (176, 238, 188),
        (255, 255, 255),
        (240, 160, 198),
        (224, 33, 138),
    ),
    "asexual": (
        (0, 0, 0),
        (163, 163, 163),
        (255, 255, 255),
        (128, 0, 128),
    ),
}
_HYFETCH_PRESETS = load_flag_presets()
if _HYFETCH_PRESETS:
    for name, colors in PRESETS.items():
        _HYFETCH_PRESETS.setdefault(name, colors)
    PRESETS = _HYFETCH_PRESETS
for alias, target in {
    "trans": "transgender",
    "nonhuman-unit": "nonhuman-unity",
    "ynullflux": "nullflux",
}.items():
    if target in PRESETS:
        PRESETS[alias] = PRESETS[target]
PRESETS["all"] = tuple(color for colors in tuple(PRESETS.values()) for color in colors)

PRESET_NAMES = tuple(PRESETS)
DEFAULT_THEME_PRESET = "femboy" if "femboy" in PRESETS else "rainbow"
