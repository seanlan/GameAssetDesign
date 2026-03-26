"""Output naming template engine."""

import os
import re

TYPE_ABBREVIATIONS = {
    "character": "char",
    "background": "bg",
    "icon": "icon",
    "card": "card",
    "sprite": "sprite",
    "tileset": "tile",
    "ui": "ui",
}


def generate_filename(
    template: str,
    asset_type: str,
    name: str = "",
    size: str = "",
    variant: str = "",
    timestamp: str = "",
    action: str = "",
    ext: str = "png",
) -> str:
    """Generate a filename from a naming template and parameters."""
    type_abbr = TYPE_ABBREVIATIONS.get(asset_type, asset_type)

    result = template
    result = result.replace("{type}", type_abbr)
    result = result.replace("{name}", name)
    result = result.replace("{size}", size)
    result = result.replace("{variant}", variant)
    result = result.replace("{timestamp}", timestamp)
    result = result.replace("{action}", action)

    while "__" in result:
        result = result.replace("__", "_")
    result = result.strip("_")

    return f"{result}.{ext}"


def find_next_variant(directory: str, base_name: str) -> str:
    """Find the next available variant number in a directory."""
    if not os.path.exists(directory):
        return "v1"

    existing = os.listdir(directory)
    max_variant = 0
    pattern = re.compile(rf"^{re.escape(base_name)}_v(\d+)\.")
    for f in existing:
        match = pattern.match(f)
        if match:
            max_variant = max(max_variant, int(match.group(1)))

    return f"v{max_variant + 1}"
