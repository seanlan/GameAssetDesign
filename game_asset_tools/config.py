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


CONFIG_FILENAME = "game-assets.yaml"


def find_config(start_dir: str | None = None) -> str | None:
    """Find game-assets.yaml in the given directory or CWD.

    Also checks for legacy projects/*.yaml location.
    """
    base = start_dir or os.getcwd()

    # Primary: game-assets.yaml in project root
    primary = os.path.join(base, CONFIG_FILENAME)
    if os.path.exists(primary):
        return primary

    # Legacy: projects/*.yaml
    projects_dir = os.path.join(base, "projects")
    if os.path.isdir(projects_dir):
        for f in sorted(os.listdir(projects_dir)):
            if f.endswith((".yaml", ".yml")):
                return os.path.join(projects_dir, f)

    return None


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


def get_requirements(config: dict) -> dict:
    """Get project asset requirements from config."""
    return config.get("requirements", {})


def check_progress(requirements: dict, output_dir: str) -> dict:
    """Check which required assets exist in the output directory.

    Returns dict mapping category → {total, done, completed, missing}.
    """
    # Map category names to output subdirectories
    category_to_subdir = {
        "characters": "characters",
        "icons": "icons",
        "ui": "ui",
        "cards": "cards",
        "backgrounds": "backgrounds",
        "sprites": "sprites",
        "tilesets": "tilesets",
    }

    progress = {}

    for category, items in requirements.items():
        subdir = category_to_subdir.get(category, category)
        asset_dir = os.path.join(output_dir, subdir)

        # List existing files
        existing_files = []
        if os.path.isdir(asset_dir):
            for root, dirs, files in os.walk(asset_dir):
                dirs[:] = [d for d in dirs if d != ".versions"]
                for f in files:
                    if f.lower().endswith((".png", ".jpg", ".jpeg")):
                        existing_files.append(f.lower())

        completed = []
        missing = []
        for item in items:
            name = item["name"].lower()
            # Match by substring in any existing filename
            found = any(name in ef for ef in existing_files)
            if found:
                completed.append(item["name"])
            else:
                missing.append(item["name"])

        progress[category] = {
            "total": len(items),
            "done": len(completed),
            "completed": completed,
            "missing": missing,
        }

    return progress


def get_templates(config: dict) -> list[dict]:
    """Get asset generation templates from config."""
    return config.get("templates", [])


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
