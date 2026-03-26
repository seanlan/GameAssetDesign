"""Project configuration loader."""

import os
import yaml


STYLE_PRESETS = {
    "pixel": "pixel art, 16-bit style, clean pixels, no anti-aliasing",
    "anime": "anime style, cel shading, vibrant colors, clean lines",
    "cel_shading": "cel shaded, flat colors, bold outlines, cartoon style",
    "watercolor": "watercolor painting, soft edges, muted colors",
    "flat": "flat design, minimal shading, solid colors, vector style",
    "realistic": "semi-realistic, detailed rendering, painterly style",
}

PRESET_TO_NANOBANANA = {
    "pixel": None,
    "anime": "anime",
    "cel_shading": None,
    "watercolor": "watercolor",
    "flat": None,
    "realistic": None,
}

PRESET_TO_GEMINI = {
    "pixel": "pixel art",
    "anime": "anime",
    "cel_shading": "cel shading",
    "watercolor": "watercolor",
    "flat": "flat design",
    "realistic": "semi-realistic",
}


def load_config(path: str) -> dict:
    """Load and validate a project YAML config file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    required = ["project", "style", "output"]
    missing = [k for k in required if k not in config]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")

    preset = config.get("style", {}).get("preset", "")
    if preset and preset not in STYLE_PRESETS:
        raise ValueError(
            f"Unknown preset '{preset}'. Valid presets: {', '.join(STYLE_PRESETS.keys())}"
        )

    return config


def get_asset_config(config: dict, asset_type: str) -> dict | None:
    """Get config for a specific asset type. Returns None if not defined."""
    assets = config.get("assets", {})
    if not assets:
        return None
    return assets.get(asset_type)


def get_style_keywords(config: dict) -> str:
    """Build the full style keyword string from config."""
    style = config.get("style", {})
    parts = []

    preset = style.get("preset", "")
    if preset and preset in STYLE_PRESETS:
        parts.append(STYLE_PRESETS[preset])

    keywords = style.get("keywords", "")
    if keywords:
        parts.append(keywords)

    palette = style.get("palette", [])
    if palette:
        parts.append("color palette: " + ", ".join(palette))

    return ", ".join(parts)
