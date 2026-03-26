# game_asset_tools/export.py
"""Engine-specific asset export."""

import json
import os
import shutil


SUPPORTED_ENGINES = ["unity", "godot", "cocos", "web"]

# Mapping from our asset subdirs to engine-specific paths
ENGINE_LAYOUTS = {
    "unity": {
        "characters": "Assets/Sprites/Characters",
        "icons": "Assets/Sprites/Icons",
        "sprites": "Assets/Sprites/Animations",
        "ui": "Assets/UI",
        "cards": "Assets/UI/Cards",
        "backgrounds": "Assets/Backgrounds",
        "tilesets": "Assets/Tilesets",
    },
    "godot": {
        "characters": "assets/characters",
        "icons": "assets/icons",
        "sprites": "assets/sprites",
        "ui": "assets/ui",
        "cards": "assets/cards",
        "backgrounds": "assets/backgrounds",
        "tilesets": "assets/tilesets",
    },
    "cocos": {
        "characters": "assets/sprites/characters",
        "icons": "assets/sprites/icons",
        "sprites": "assets/sprites/animations",
        "ui": "assets/ui",
        "cards": "assets/ui/cards",
        "backgrounds": "assets/backgrounds",
        "tilesets": "assets/tilesets",
    },
    "web": {
        "characters": "images/characters",
        "icons": "images/icons",
        "sprites": "images/sprites",
        "ui": "images/ui",
        "cards": "images/cards",
        "backgrounds": "images/backgrounds",
        "tilesets": "images/tilesets",
    },
}


def export_for_engine(
    engine: str,
    input_dir: str,
    export_dir: str,
) -> dict:
    """Export assets restructured for a specific game engine.

    Args:
        engine: target engine ("unity", "godot", "cocos", "web")
        input_dir: source output/ directory
        export_dir: destination export directory

    Returns:
        dict with "total" count and "files" list
    """
    if engine not in SUPPORTED_ENGINES:
        raise ValueError(f"Unsupported engine '{engine}'. Supported: {', '.join(SUPPORTED_ENGINES)}")

    layout = ENGINE_LAYOUTS[engine]
    total = 0
    files = []

    for src_subdir, dest_subdir in layout.items():
        src_path = os.path.join(input_dir, src_subdir)
        if not os.path.isdir(src_path):
            continue

        dest_path = os.path.join(export_dir, dest_subdir)
        os.makedirs(dest_path, exist_ok=True)

        for root, dirs, fnames in os.walk(src_path):
            # Skip .versions
            dirs[:] = [d for d in dirs if d != ".versions"]
            rel = os.path.relpath(root, src_path)
            target_root = os.path.join(dest_path, rel) if rel != "." else dest_path
            os.makedirs(target_root, exist_ok=True)

            for fname in fnames:
                if fname.lower().endswith((".png", ".jpg", ".jpeg", ".json")) and not fname.startswith("."):
                    src_file = os.path.join(root, fname)
                    dst_file = os.path.join(target_root, fname)
                    shutil.copy2(src_file, dst_file)
                    files.append(dst_file)
                    total += 1

    # Web engine: generate a manifest
    if engine == "web":
        web_manifest = {
            "engine": "web",
            "total_assets": total,
            "files": [os.path.relpath(f, export_dir) for f in files],
        }
        manifest_path = os.path.join(export_dir, "manifest.json")
        os.makedirs(os.path.dirname(manifest_path) or ".", exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(web_manifest, f, indent=2)

    return {"total": total, "files": files}
