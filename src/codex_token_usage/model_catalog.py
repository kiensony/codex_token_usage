"""OpenAI USD prices, checked 2026-11-25.

Sources: https://developers.openai.com/api/docs/pricing and the individual model
pages linked from https://developers.openai.com/api/docs/models/all (including
retired models, for historical Codex sessions).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPrice:
    input_per_million: float
    cached_input_per_million: float | None
    output_per_million: float


# Per million tokens. Unqualified names use standard speed and short context.
MODEL_PRICES: dict[str, ModelPrice] = {
    "babbage-002": ModelPrice(0.40, None, 0.40),
    "chat-latest": ModelPrice(5.00, 0.50, 30.00),
    "chatgpt-4o-latest": ModelPrice(5.00, None, 15.00),
    "codex-mini-latest": ModelPrice(1.50, 0.375, 6.00),
    "computer-use-preview": ModelPrice(3.00, None, 12.00),
    "davinci-002": ModelPrice(2.00, None, 2.00),
    "gpt-3.5-turbo": ModelPrice(0.50, None, 1.50),
    "gpt-4": ModelPrice(30.00, None, 60.00),
    "gpt-4-turbo": ModelPrice(10.00, None, 30.00),
    "gpt-4-turbo-preview": ModelPrice(10.00, None, 30.00),
    "gpt-4.1": ModelPrice(2.00, 0.50, 8.00),
    "gpt-4.1 (long context)": ModelPrice(2.00, 0.50, 8.00),
    "gpt-4.1-mini": ModelPrice(0.40, 0.10, 1.60),
    "gpt-4.1-mini (long context)": ModelPrice(0.40, 0.10, 1.60),
    "gpt-4.1-nano": ModelPrice(0.10, 0.025, 0.40),
    "gpt-4.5-preview": ModelPrice(75.00, 37.50, 150.00),
    "gpt-4o": ModelPrice(2.50, 1.25, 10.00),
    "gpt-4o-mini": ModelPrice(0.15, 0.075, 0.60),
    "gpt-4o-mini-search-preview": ModelPrice(0.15, None, 0.60),
    "gpt-4o-mini-tts": ModelPrice(0.60, None, 12.00),
    "gpt-4o-search-preview": ModelPrice(2.50, None, 10.00),
    "gpt-5": ModelPrice(1.25, 0.125, 10.00),
    "gpt-5-chat-latest": ModelPrice(1.25, 0.125, 10.00),
    "gpt-5-codex": ModelPrice(1.25, 0.125, 10.00),
    "gpt-5-mini": ModelPrice(0.25, 0.025, 2.00),
    "gpt-5-nano": ModelPrice(0.05, 0.005, 0.40),
    "gpt-5-pro": ModelPrice(15.00, None, 120.00),
    "gpt-5-search-api": ModelPrice(1.25, 0.125, 10.00),
    "gpt-5.1": ModelPrice(1.25, 0.125, 10.00),
    "gpt-5.1-chat-latest": ModelPrice(1.25, 0.125, 10.00),
    "gpt-5.1-codex": ModelPrice(1.25, 0.125, 10.00),
    "gpt-5.1-codex-max": ModelPrice(1.25, 0.125, 10.00),
    "gpt-5.1-codex-mini": ModelPrice(0.25, 0.025, 2.00),
    "gpt-5.2": ModelPrice(1.75, 0.175, 14.00),
    "gpt-5.2-chat-latest": ModelPrice(1.75, 0.175, 14.00),
    "gpt-5.2-codex": ModelPrice(1.75, 0.175, 14.00),
    "gpt-5.2-pro": ModelPrice(21.00, None, 168.00),
    "gpt-5.3-chat-latest": ModelPrice(1.75, 0.175, 14.00),
    "gpt-5.3-codex": ModelPrice(1.75, 0.175, 14.00),
    "gpt-5.4": ModelPrice(2.50, 0.25, 15.00),
    "gpt-5.4 (long context)": ModelPrice(5.00, 0.50, 22.50),
    "gpt-5.4-mini": ModelPrice(0.75, 0.075, 4.50),
    "gpt-5.4-nano": ModelPrice(0.20, 0.02, 1.25),
    "gpt-5.4-pro": ModelPrice(30.00, None, 180.00),
    "gpt-5.4-pro (long context)": ModelPrice(60.00, None, 270.00),
    "gpt-5.5": ModelPrice(5.00, 0.50, 30.00),
    "gpt-5.5 (long context)": ModelPrice(10.00, 1.00, 45.00),
    "gpt-5.5-cyber-preview": ModelPrice(12.50, 1.25, 75.00),
    "gpt-5.5-pro": ModelPrice(30.00, None, 180.00),
    "gpt-5.5-pro (long context)": ModelPrice(60.00, None, 270.00),
    "gpt-5.6": ModelPrice(4.00, 0.40, 20.00),
    "gpt-5.6-cyber": ModelPrice(12.50, 1.25, 75.00),
    "gpt-5.6-luna": ModelPrice(0.20, 0.02, 1.20),
    "gpt-5.6-sol": ModelPrice(4.00, 0.40, 20.00),
    "gpt-5.6-terra": ModelPrice(2.00, 0.20, 12.00),
    "gpt-6-astra": ModelPrice(10.00, 1.00, 50.00),
    "gpt-6-astra-law": ModelPrice(10.00, 1.00, 50.00),
    "gpt-6-cyber": ModelPrice(20.00, 2.00, 100.00),
    "gpt-6-luna": ModelPrice(0.10, 0.01, 0.50),
    "gpt-6-rosalind": ModelPrice(10.00, 1.00, 50.00),
    "gpt-6-sol": ModelPrice(2.00, 0.20, 10.00),
    "gpt-6.1-sol": ModelPrice(2.00, 0.10, 10.00),
    "gpt-6.1-sol-ultrafast": ModelPrice(12.00, 0.60, 60.00),
    "gpt-6.1-terra": ModelPrice(1.00, 0.05, 5.00),
    "gpt-6.2-astra": ModelPrice(8.00, 0.40, 40.00),
    "gpt-6.2-astra-law": ModelPrice(8.00, 0.40, 40.00),
    "gpt-6.2-sol": ModelPrice(2.00, 0.10, 10.00),
    "gpt-daybreak-blue-latest": ModelPrice(4.00, 0.40, 20.00),
    "gpt-daybreak-red-latest": ModelPrice(12.50, 1.25, 75.00),
    "gpt-rosalind-discovery": ModelPrice(5.00, 0.50, 25.00),
    "gpt-rosalind-research": ModelPrice(5.00, 0.50, 25.00),
    "o1": ModelPrice(15.00, 7.50, 60.00),
    "o1-mini": ModelPrice(1.10, 0.55, 4.40),
    "o1-preview": ModelPrice(15.00, 7.50, 60.00),
    "o1-pro": ModelPrice(150.00, None, 600.00),
    "o3": ModelPrice(2.00, 0.50, 8.00),
    "o3-deep-research": ModelPrice(10.00, 2.50, 40.00),
    "o3-mini": ModelPrice(1.10, 0.55, 4.40),
    "o3-pro": ModelPrice(20.00, None, 80.00),
    "o4-mini": ModelPrice(1.10, 0.275, 4.40),
    "o4-mini-deep-research": ModelPrice(2.00, 0.50, 8.00),
    "omni-moderation-latest": ModelPrice(0.00, None, 0.00),
    "text-embedding-3-large": ModelPrice(0.13, None, 0.00),
    "text-embedding-3-small": ModelPrice(0.02, None, 0.00),
    "text-embedding-ada-002": ModelPrice(0.10, None, 0.00),
    "text-moderation-latest": ModelPrice(0.00, None, 0.00),
    "text-moderation-stable": ModelPrice(0.00, None, 0.00),
}


# These rates need units or billing details absent from Codex token totals.
REFERENCE_PRICING: dict[str, str] = {
    model: description
    for models, description in (
        (
            (
                "gpt-image-2.6-sunburst",
                "gpt-image-2.6-flare",
                "gpt-image-2.5-sunburst",
                "gpt-image-2.5-flare",
                "gpt-image-2",
            ),
            "Per 1M tokens. Text $5 input, $1.25 cached. Image $8 input, $2 cached, "
            "$30 output.",
        ),
        (
            ("gpt-image-1.5", "chatgpt-image-latest"),
            "Per 1M tokens. Text $5 input, $1.25 cached, $10 output. Image $8 input, "
            "$2 cached, $32 output.",
        ),
        (
            ("gpt-image-1",),
            "Per 1M tokens. Text $5 input, $1.25 cached. Image $10 input, $2.50 "
            "cached, $40 output.",
        ),
        (
            ("gpt-image-1-mini",),
            "Per 1M tokens. Text $2 input, $0.20 cached. Image $2.50 input, $0.25 "
            "cached, $8 output.",
        ),
        (("gpt-live-1.1", "gpt-live-1"), "$0.05 per active minute, $0.02 per standby minute."),
        (
            ("gpt-realtime-2.1", "gpt-realtime-2"),
            "Per 1M tokens. Text $4 input, $0.40 cached, $24 output. Audio $32 input, "
            "$0.40 cached, $64 output. Image $5 input, $0.50 cached.",
        ),
        (
            ("gpt-realtime-1.5", "gpt-realtime"),
            "Per 1M tokens. Text $4 input, $0.40 cached, $16 output. Audio $32 input, "
            "$0.40 cached, $64 output. Image $5 input, $0.50 cached.",
        ),
        (
            ("gpt-realtime-2.1-mini", "gpt-realtime-mini"),
            "Per 1M tokens. Text $0.60 input, $0.06 cached, $2.40 output. Audio $10 "
            "input, $0.30 cached, $20 output. Image $0.80 input, $0.08 cached.",
        ),
        (
            ("gpt-audio-1.5", "gpt-audio"),
            "Per 1M tokens. Text $2.50 input, $10 output. Audio $32 input, $64 "
            "output.",
        ),
        (
            ("gpt-audio-mini",),
            "Per 1M tokens. Text $0.60 input, $2.40 output. Audio $10 input, $20 "
            "output.",
        ),
        (
            ("gpt-4o-audio-preview",),
            "Per 1M tokens. Text $2.50 input, $10 output. Audio $40 input, $80 "
            "output.",
        ),
        (
            ("gpt-4o-mini-audio-preview",),
            "Per 1M tokens. Text $0.15 input, $0.60 output. Audio $10 input, $20 "
            "output.",
        ),
        (
            ("gpt-4o-realtime-preview",),
            "Per 1M tokens. Text $5 input, $2.50 cached, $20 output. Audio $40 input, "
            "$2.50 cached, $80 output.",
        ),
        (
            ("gpt-4o-mini-realtime-preview",),
            "Per 1M tokens. Text $0.60 input, $0.30 cached, $2.40 output. Audio $10 "
            "input, $0.30 cached, $20 output.",
        ),
        (
            ("gpt-4o-transcribe", "gpt-4o-transcribe-diarize"),
            "Published estimate for transcription is $0.006 per minute.",
        ),
        (
            ("gpt-4o-mini-transcribe",),
            "Published estimate for transcription is $0.003 per minute.",
        ),
        (("whisper-1",), "$0.006 per minute."),
        (("gpt-live-transcribe", "gpt-realtime-whisper"), "$0.017 per minute."),
        (("gpt-realtime-translate",), "$0.034 per minute."),
        (("gpt-transcribe",), "$0.0045 per minute."),
        (("tts-1",), "$15 per million characters."),
        (("tts-1-hd",), "$30 per million characters."),
        (
            ("gpt-oss-120b", "gpt-oss-20b"),
            "Open-weight model. Set the rate charged by your hosting provider.",
        ),
        (
            ("gpt-reserve", "gpt-5.3-codex-spark", "gpt-5-codex-mini", "webrun"),
            "A public standard API token rate could not be verified.",
        ),
        (
            ("codex-auto-review",),
            "Auto-review is free with ChatGPT sign-in. A standard API token rate "
            "could not be verified.",
        ),
    )
    for model in models
}
