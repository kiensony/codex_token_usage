from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from codex_token_usage.pricing import ModelPrice, PricingConfig
from codex_token_usage.theme import (
    DEFAULT_THEME_PRESET,
    DisplayConfig,
    PRESETS,
    ThemeConfig,
    apply_theme_overrides,
    load_theme_config,
    save_theme_config,
    themed_bar_segments,
)


class ThemeConfigTests(unittest.TestCase):
    def test_missing_config_uses_plain_theme_without_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = load_theme_config(Path(tmp) / "missing.json")

        self.assertFalse(result.config.enabled)
        self.assertEqual(result.config.preset, "femboy")
        self.assertEqual(DEFAULT_THEME_PRESET, "femboy")
        self.assertEqual(result.status, "")

    def test_save_and_load_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            saved = ThemeConfig(
                enabled=True,
                preset="trans",
                color_mode="rgb",
                lightness=0.75,
            )

            save_theme_config(saved, path)
            result = load_theme_config(path)

        self.assertEqual(result.config, saved)
        self.assertEqual(result.status, "")
        self.assertEqual(result.display, DisplayConfig())

    def test_save_and_load_display_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            display = DisplayConfig(
                show_cached_tokens=False,
                show_cached_percent=False,
                show_estimated_cost=True,
                show_reasoning_level=False,
                show_cache_miss=False,
                show_reasoning_tokens=False,
                show_model=False,
                show_context=False,
                model_column_width=16,
            )

            save_theme_config(ThemeConfig(), path, display=display)
            result = load_theme_config(path)

        self.assertEqual(result.display, display)
        self.assertEqual(result.status, "")

    def test_save_and_load_pricing_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            pricing = PricingConfig(
                model_prices=(
                    ("custom-model", ModelPrice(1.0, 0.1, 2.0)),
                    ("no-cache-model", ModelPrice(3.0, None, 4.0)),
                )
            )

            save_theme_config(ThemeConfig(), path, pricing=pricing)
            result = load_theme_config(path)

        self.assertEqual(result.pricing, pricing)
        self.assertEqual(result.status, "")

    def test_invalid_json_falls_back_to_plain_with_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text("{not-json", encoding="utf-8")

            result = load_theme_config(path)

        self.assertFalse(result.config.enabled)
        self.assertIn("theme config ignored", result.status)

    def test_unknown_preset_falls_back_to_plain_with_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "theme": {
                            "enabled": True,
                            "preset": "unknown",
                            "color_mode": "8bit",
                            "lightness": 1,
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = load_theme_config(path)

        self.assertFalse(result.config.enabled)
        self.assertEqual(result.config.preset, "femboy")
        self.assertIn("unknown theme preset", result.status)

    def test_empty_preset_falls_back_to_femboy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "theme": {
                            "enabled": True,
                            "preset": "",
                            "color_mode": "8bit",
                            "lightness": 1,
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = load_theme_config(path)

        self.assertTrue(result.config.enabled)
        self.assertEqual(result.config.preset, "femboy")
        self.assertEqual(result.status, "")

    def test_disabled_theme_loads_as_plain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            save_theme_config(ThemeConfig(enabled=False, preset="rainbow"), path)

            result = load_theme_config(path)

        self.assertFalse(result.config.enabled)
        self.assertEqual(result.config.preset, "rainbow")

    def test_one_run_overrides(self) -> None:
        config = ThemeConfig(enabled=False, preset="rainbow")

        themed = apply_theme_overrides(config, preset="pansexual", lightness=0.5)
        plain = apply_theme_overrides(themed, preset="plain")

        self.assertTrue(themed.enabled)
        self.assertEqual(themed.preset, "pansexual")
        self.assertEqual(themed.lightness, 0.5)
        self.assertFalse(plain.enabled)

    def test_all_preset_combines_existing_flags(self) -> None:
        expected_length = sum(
            len(colors) for name, colors in PRESETS.items() if name != "all"
        )

        self.assertIn("all", PRESETS)
        self.assertEqual(len(PRESETS["all"]), expected_length)

    def test_hyfetch_style_presets_are_available(self) -> None:
        requested = {
            "abrosexual",
            "adipophilia",
            "agender",
            "akiosexual",
            "androgyne",
            "androsexual",
            "aroace1",
            "aroace2",
            "aroace3",
            "aromantic",
            "asexual",
            "autism",
            "autoromantic",
            "autosexual",
            "baker",
            "band",
            "bear",
            "beiyang",
            "bigender",
            "biromantic1",
            "biromantic2",
            "bisexual",
            "boyflux2",
            "burger",
            "butch",
            "caninekin",
            "cenelian",
            "cisgender",
            "cupioromantic",
            "cupiorose",
            "cupiosexual",
            "demiboy",
            "demifae",
            "demifaun",
            "demigender",
            "demigirl",
            "demisexual",
            "drag",
            "enbian",
            "equal-rights",
            "exipronoun",
            "femboy",
            "femme",
            "fictosexual",
            "finsexual",
            "fluidflux1",
            "fluidflux2",
            "fraysexual",
            "gay-men",
            "genderfae",
            "genderfaun",
            "genderfluid",
            "genderflux",
            "gendernonconforming1",
            "gendernonconforming2",
            "genderqueer",
            "gendervoid",
            "girlflux",
            "greygender",
            "gynesexual",
            "haruhi",
            "hyperandrogyne",
            "hyperboy",
            "hypergender",
            "hypergirl",
            "hyperneutrois",
            "intergender",
            "interprogress",
            "intersex",
            "kenochoric",
            "leather",
            "lesbian",
            "libraandrogyne",
            "librafeminine",
            "libragender",
            "libramasculine",
            "libranonbinary",
            "lunian",
            "neofluid",
            "neopronoun",
            "neutrois",
            "nonbinary",
            "nonhuman-unit",
            "ynullflux",
            "old-polyam",
            "omniromantic",
            "omnisexual",
            "otter",
            "pangender",
            "pangender.contrast",
            "pansexual",
            "paraboy",
            "paraboyalt",
            "paragender",
            "paragenderalt",
            "paragirl",
            "paragirlalt",
            "paranonbinary",
            "paranonbinaryalt",
            "petergriffin",
            "plural",
            "polyam",
            "polysexual",
            "progress",
            "pronounfluid",
            "pronounflux",
            "queer",
            "queervillain",
            "rainbow",
            "rubber",
            "sapphic",
            "solian",
            "throatlozenges",
            "tomboy",
            "transbian",
            "transfeminine",
            "transgender",
            "transmasculine",
            "transneutral",
            "twink",
            "unlabeled1",
            "unlabeled2",
            "veldian",
            "voidboy",
            "voidgirl",
            "xenogender",
        }

        self.assertFalse(requested - set(PRESETS))

    def test_themed_bar_segments_and_plain_fallback(self) -> None:
        config = ThemeConfig(enabled=True, preset="trans")

        segments = themed_bar_segments(100, 100, 10, config)
        color_indexes = {
            segment.color_index
            for segment in segments
            if segment.color_index is not None
        }
        plain = themed_bar_segments(50, 100, 5, ThemeConfig(enabled=False))

        self.assertGreater(len(color_indexes), 1)
        self.assertEqual("".join(segment.text for segment in segments), "#" * 10)
        self.assertEqual(len(plain), 1)
        self.assertEqual(plain[0].text, "##...")
        self.assertIsNone(plain[0].color_index)


if __name__ == "__main__":
    unittest.main()
