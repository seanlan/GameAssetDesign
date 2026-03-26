# Phase 2C: Export + Atlas + Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add engine-specific export, texture atlas packing, and project progress dashboard to the game asset toolkit.

**Architecture:** Three new modules: `export.py` (restructure assets for Unity/Godot/Cocos/Web), `atlas.py` (bin-pack sprites into optimized atlases), and `config.py` + `manager.py` extensions (requirements tracking and dashboard display). Each module is independent and testable.

**Tech Stack:** Python 3.10+, Pillow, existing game_asset_tools modules

**Spec:** `docs/superpowers/specs/2026-03-26-game-asset-skill-design.md` → "Engine Export", "Texture Atlas Packing", "Project Progress Dashboard" sections

---

## File Structure

```
game_asset_tools/
├── export.py            # NEW: Engine-specific export
├── atlas.py             # NEW: Texture atlas packing
├── config.py            # MODIFY: Add requirements parsing
├── manager.py           # MODIFY: Add progress dashboard to HTML
├── cli.py               # MODIFY: Add export, atlas commands

tests/
├── test_export.py       # NEW
├── test_atlas.py        # NEW
├── test_config.py       # MODIFY: Add requirements tests

skills/
└── game-asset.md        # MODIFY: Add export/atlas/dashboard sections
```

---

## Task 1: Texture Atlas Module (`atlas.py`)

**Files:**
- Create: `game_asset_tools/atlas.py`
- Create: `tests/test_atlas.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_atlas.py
import os
import json
from PIL import Image
from game_asset_tools.atlas import pack_atlas


def _create_sprites(tmp_dir, count=6, size=(64, 64)):
    sprites_dir = os.path.join(tmp_dir, "sprites")
    os.makedirs(sprites_dir)
    for i in range(count):
        color = ((i * 40) % 256, (i * 60 + 100) % 256, (i * 80 + 50) % 256, 255)
        img = Image.new("RGBA", size, color)
        img.save(os.path.join(sprites_dir, f"sprite_{i:02d}.png"))
    return sprites_dir


def test_pack_atlas_basic(tmp_dir):
    sprites_dir = _create_sprites(tmp_dir, count=4, size=(64, 64))
    output = os.path.join(tmp_dir, "atlas.png")
    meta = os.path.join(tmp_dir, "atlas.json")
    pack_atlas(sprites_dir, output, meta, max_size=(512, 512))
    assert os.path.exists(output)
    assert os.path.exists(meta)
    atlas = Image.open(output)
    assert atlas.width <= 512
    assert atlas.height <= 512
    with open(meta) as f:
        data = json.load(f)
    assert len(data["atlases"]) == 1
    assert len(data["atlases"][0]["sprites"]) == 4


def test_pack_atlas_with_padding(tmp_dir):
    sprites_dir = _create_sprites(tmp_dir, count=4, size=(64, 64))
    output = os.path.join(tmp_dir, "atlas.png")
    meta = os.path.join(tmp_dir, "atlas.json")
    pack_atlas(sprites_dir, output, meta, max_size=(512, 512), padding=4)
    with open(meta) as f:
        data = json.load(f)
    sprites = data["atlases"][0]["sprites"]
    # With padding=4, sprites should not overlap
    for i in range(len(sprites)):
        for j in range(i + 1, len(sprites)):
            s1, s2 = sprites[i], sprites[j]
            # Check no overlap (at least padding apart)
            x_overlap = s1["x"] < s2["x"] + s2["w"] and s2["x"] < s1["x"] + s1["w"]
            y_overlap = s1["y"] < s2["y"] + s2["h"] and s2["y"] < s1["y"] + s1["h"]
            assert not (x_overlap and y_overlap)


def test_pack_atlas_multiple_pages(tmp_dir):
    # Many sprites that won't fit in a tiny atlas
    sprites_dir = _create_sprites(tmp_dir, count=20, size=(64, 64))
    output = os.path.join(tmp_dir, "atlas.png")
    meta = os.path.join(tmp_dir, "atlas.json")
    pack_atlas(sprites_dir, output, meta, max_size=(128, 128), padding=2)
    with open(meta) as f:
        data = json.load(f)
    assert len(data["atlases"]) > 1
    total_sprites = sum(len(a["sprites"]) for a in data["atlases"])
    assert total_sprites == 20


def test_pack_atlas_mixed_sizes(tmp_dir):
    sprites_dir = os.path.join(tmp_dir, "sprites")
    os.makedirs(sprites_dir)
    Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(os.path.join(sprites_dir, "small.png"))
    Image.new("RGBA", (128, 64), (0, 255, 0, 255)).save(os.path.join(sprites_dir, "wide.png"))
    Image.new("RGBA", (64, 128), (0, 0, 255, 255)).save(os.path.join(sprites_dir, "tall.png"))
    output = os.path.join(tmp_dir, "atlas.png")
    meta = os.path.join(tmp_dir, "atlas.json")
    pack_atlas(sprites_dir, output, meta, max_size=(512, 512))
    with open(meta) as f:
        data = json.load(f)
    assert len(data["atlases"][0]["sprites"]) == 3


def test_pack_atlas_phaser_format(tmp_dir):
    sprites_dir = _create_sprites(tmp_dir, count=2, size=(64, 64))
    output = os.path.join(tmp_dir, "atlas.png")
    meta = os.path.join(tmp_dir, "atlas.json")
    pack_atlas(sprites_dir, output, meta, max_size=(512, 512), meta_format="phaser")
    with open(meta) as f:
        data = json.load(f)
    assert "frames" in data
    assert "meta" in data


def test_pack_atlas_generic_format(tmp_dir):
    sprites_dir = _create_sprites(tmp_dir, count=2, size=(64, 64))
    output = os.path.join(tmp_dir, "atlas.png")
    meta = os.path.join(tmp_dir, "atlas.json")
    pack_atlas(sprites_dir, output, meta, max_size=(512, 512), meta_format="generic")
    with open(meta) as f:
        data = json.load(f)
    assert "atlases" in data
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_atlas.py -v
```

- [ ] **Step 3: Implement atlas.py**

```python
# game_asset_tools/atlas.py
"""Texture atlas packing using shelf-first-fit algorithm."""

import json
import os
from PIL import Image


def _shelf_pack(sprites: list[dict], max_w: int, max_h: int, padding: int) -> list[list[dict]]:
    """Pack sprites into pages using shelf-first-fit algorithm.

    Returns list of pages, each page is a list of placed sprites with x, y positions.
    """
    # Sort by height descending for better shelf packing
    sprites_sorted = sorted(sprites, key=lambda s: s["h"], reverse=True)

    pages = []
    remaining = list(sprites_sorted)

    while remaining:
        page = []
        shelf_y = 0
        shelf_h = 0
        cursor_x = 0

        to_place = list(remaining)
        remaining = []

        for sprite in to_place:
            sw = sprite["w"] + padding
            sh = sprite["h"] + padding

            # Try to fit on current shelf
            if cursor_x + sw <= max_w and shelf_y + sh <= max_h:
                page.append({**sprite, "x": cursor_x, "y": shelf_y})
                cursor_x += sw
                shelf_h = max(shelf_h, sh)
            # Try new shelf
            elif sw <= max_w and shelf_y + shelf_h + sh <= max_h:
                shelf_y += shelf_h
                shelf_h = sh
                cursor_x = sw
                page.append({**sprite, "x": 0, "y": shelf_y})
            else:
                # Doesn't fit on this page
                remaining.append(sprite)

        if page:
            pages.append(page)
        elif remaining:
            # Single sprite too large — force it on its own page
            s = remaining.pop(0)
            pages.append([{**s, "x": 0, "y": 0}])

    return pages


def _format_generic(pages: list[list[dict]], atlas_images: list[str], atlas_sizes: list[tuple]) -> dict:
    atlases = []
    for i, (page, img_name, size) in enumerate(zip(pages, atlas_images, atlas_sizes)):
        atlases.append({
            "image": img_name,
            "size": {"w": size[0], "h": size[1]},
            "sprites": [{"name": s["name"], "x": s["x"], "y": s["y"], "w": s["w"], "h": s["h"]} for s in page],
        })
    return {"atlases": atlases}


def _format_phaser(pages: list[list[dict]], atlas_images: list[str], atlas_sizes: list[tuple]) -> dict:
    """Phaser/TexturePacker format (single atlas only, first page)."""
    frames = {}
    page = pages[0] if pages else []
    for s in page:
        frames[s["name"]] = {
            "frame": {"x": s["x"], "y": s["y"], "w": s["w"], "h": s["h"]},
            "sourceSize": {"w": s["w"], "h": s["h"]},
            "spriteSourceSize": {"x": 0, "y": 0, "w": s["w"], "h": s["h"]},
        }
    return {
        "frames": frames,
        "meta": {
            "image": atlas_images[0] if atlas_images else "atlas.png",
            "size": {"w": atlas_sizes[0][0], "h": atlas_sizes[0][1]} if atlas_sizes else {"w": 0, "h": 0},
            "format": "RGBA8888",
            "scale": 1,
        },
    }


def pack_atlas(
    input_dir: str,
    output_path: str,
    meta_path: str,
    max_size: tuple[int, int] = (2048, 2048),
    padding: int = 2,
    meta_format: str = "generic",
) -> None:
    """Pack sprites from input_dir into texture atlas(es).

    Args:
        input_dir: directory with sprite images
        output_path: base output path for atlas images (e.g., atlas.png → atlas_0.png, atlas_1.png)
        meta_path: output metadata JSON path
        max_size: maximum atlas size (width, height)
        padding: pixel spacing between sprites
        meta_format: "generic" or "phaser"
    """
    max_w, max_h = max_size

    # Collect sprites
    sprite_files = sorted(
        f for f in os.listdir(input_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    )
    if not sprite_files:
        raise ValueError(f"No sprite images found in {input_dir}")

    sprites = []
    for fname in sprite_files:
        path = os.path.join(input_dir, fname)
        img = Image.open(path)
        name = os.path.splitext(fname)[0]
        sprites.append({"name": name, "w": img.width, "h": img.height, "path": path, "fname": fname})

    # Pack
    pages = _shelf_pack(sprites, max_w, max_h, padding)

    # Render atlas images
    base, ext = os.path.splitext(output_path)
    if not ext:
        ext = ".png"

    atlas_images = []
    atlas_sizes = []
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    for i, page in enumerate(pages):
        # Calculate actual atlas size (tight fit)
        actual_w = max((s["x"] + s["w"] for s in page), default=0)
        actual_h = max((s["y"] + s["h"] for s in page), default=0)
        actual_w = min(actual_w, max_w)
        actual_h = min(actual_h, max_h)

        atlas = Image.new("RGBA", (actual_w, actual_h), (0, 0, 0, 0))
        for s in page:
            sprite_img = Image.open(s["path"]).convert("RGBA")
            atlas.paste(sprite_img, (s["x"], s["y"]), sprite_img)

        if len(pages) == 1:
            img_path = output_path
            img_name = os.path.basename(output_path)
        else:
            img_path = f"{base}_{i}{ext}"
            img_name = os.path.basename(img_path)

        atlas.save(img_path, "PNG")
        atlas_images.append(img_name)
        atlas_sizes.append((actual_w, actual_h))

    # Write metadata
    if meta_format == "phaser":
        meta_data = _format_phaser(pages, atlas_images, atlas_sizes)
    else:
        meta_data = _format_generic(pages, atlas_images, atlas_sizes)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=2)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_atlas.py -v
```

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/atlas.py tests/test_atlas.py
git commit -m "feat: add texture atlas packing module"
```

---

## Task 2: Engine Export Module (`export.py`)

**Files:**
- Create: `game_asset_tools/export.py`
- Create: `tests/test_export.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_export.py
import os
import json
from PIL import Image
from game_asset_tools.export import export_for_engine, SUPPORTED_ENGINES


def _setup_assets(tmp_dir):
    out_dir = os.path.join(tmp_dir, "output")
    for subdir in ["characters", "icons", "ui", "backgrounds"]:
        d = os.path.join(out_dir, subdir)
        os.makedirs(d)
        Image.new("RGBA", (64, 64), (100, 100, 100, 255)).save(os.path.join(d, f"test_{subdir}.png"))
    return out_dir


def test_supported_engines():
    assert "unity" in SUPPORTED_ENGINES
    assert "godot" in SUPPORTED_ENGINES
    assert "cocos" in SUPPORTED_ENGINES
    assert "web" in SUPPORTED_ENGINES


def test_export_unity(tmp_dir):
    input_dir = _setup_assets(tmp_dir)
    export_dir = os.path.join(tmp_dir, "unity_export")
    result = export_for_engine("unity", input_dir, export_dir)
    assert os.path.isdir(os.path.join(export_dir, "Assets", "Sprites", "Characters"))
    assert os.path.isdir(os.path.join(export_dir, "Assets", "Sprites", "Icons"))
    assert os.path.isdir(os.path.join(export_dir, "Assets", "UI"))
    assert os.path.isdir(os.path.join(export_dir, "Assets", "Backgrounds"))
    # Check files were copied
    chars = os.listdir(os.path.join(export_dir, "Assets", "Sprites", "Characters"))
    assert any(f.endswith(".png") for f in chars)
    assert result["total"] > 0


def test_export_godot(tmp_dir):
    input_dir = _setup_assets(tmp_dir)
    export_dir = os.path.join(tmp_dir, "godot_export")
    result = export_for_engine("godot", input_dir, export_dir)
    assert os.path.isdir(os.path.join(export_dir, "assets", "characters"))
    assert os.path.isdir(os.path.join(export_dir, "assets", "icons"))
    assert result["total"] > 0


def test_export_web(tmp_dir):
    input_dir = _setup_assets(tmp_dir)
    export_dir = os.path.join(tmp_dir, "web_export")
    result = export_for_engine("web", input_dir, export_dir)
    assert os.path.isdir(os.path.join(export_dir, "images", "characters"))
    # Should have a manifest
    assert os.path.exists(os.path.join(export_dir, "manifest.json"))
    assert result["total"] > 0


def test_export_cocos(tmp_dir):
    input_dir = _setup_assets(tmp_dir)
    export_dir = os.path.join(tmp_dir, "cocos_export")
    result = export_for_engine("cocos", input_dir, export_dir)
    assert os.path.isdir(os.path.join(export_dir, "assets"))
    assert result["total"] > 0


def test_export_invalid_engine(tmp_dir):
    import pytest
    input_dir = _setup_assets(tmp_dir)
    with pytest.raises(ValueError, match="Unsupported engine"):
        export_for_engine("unreal", input_dir, os.path.join(tmp_dir, "out"))


def test_export_empty_input(tmp_dir):
    input_dir = os.path.join(tmp_dir, "empty_output")
    os.makedirs(input_dir)
    export_dir = os.path.join(tmp_dir, "export")
    result = export_for_engine("web", input_dir, export_dir)
    assert result["total"] == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_export.py -v
```

- [ ] **Step 3: Implement export.py**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_export.py -v
```

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/export.py tests/test_export.py
git commit -m "feat: add engine-specific asset export module"
```

---

## Task 3: Project Progress Dashboard

**Files:**
- Modify: `game_asset_tools/config.py`
- Modify: `tests/test_config.py`

- [ ] **Step 1: Add failing tests**

Add to `tests/test_config.py`:

```python
def test_get_requirements(tmp_dir):
    from game_asset_tools.config import get_requirements
    config_path = os.path.join(tmp_dir, "test.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test"
  engine: "unity"
style:
  preset: "anime"
  keywords: ""
  palette: []
assets: {}
output:
  base_dir: "output/"
  naming: "{type}_{name}"
requirements:
  characters:
    - name: "fire_mage"
      sizes: [512, 1024]
    - name: "ice_archer"
  icons:
    - name: "fireball"
    - name: "ice_arrow"
    - name: "healing"
""")
    config = load_config(config_path)
    reqs = get_requirements(config)
    assert "characters" in reqs
    assert len(reqs["characters"]) == 2
    assert reqs["characters"][0]["name"] == "fire_mage"
    assert len(reqs["icons"]) == 3


def test_get_requirements_empty(tmp_dir):
    from game_asset_tools.config import get_requirements
    config_path = os.path.join(tmp_dir, "test.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test"
  engine: "unity"
style:
  preset: "anime"
  keywords: ""
  palette: []
assets: {}
output:
  base_dir: "output/"
  naming: "{type}_{name}"
""")
    config = load_config(config_path)
    reqs = get_requirements(config)
    assert reqs == {}


def test_check_progress(tmp_dir):
    from game_asset_tools.config import get_requirements, check_progress
    config_path = os.path.join(tmp_dir, "test.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test"
  engine: "unity"
style:
  preset: "anime"
  keywords: ""
  palette: []
assets: {}
output:
  base_dir: "output/"
  naming: "{type}_{name}"
requirements:
  characters:
    - name: "fire_mage"
    - name: "ice_archer"
  icons:
    - name: "fireball"
    - name: "healing"
""")
    config = load_config(config_path)
    reqs = get_requirements(config)

    # Create some matching assets
    out_dir = os.path.join(tmp_dir, "output")
    chars_dir = os.path.join(out_dir, "characters")
    icons_dir = os.path.join(out_dir, "icons")
    os.makedirs(chars_dir)
    os.makedirs(icons_dir)
    Image.new("RGBA", (64, 64), (255, 0, 0, 255)).save(os.path.join(chars_dir, "char_fire_mage_512_v1.png"))
    Image.new("RGBA", (64, 64), (255, 0, 0, 255)).save(os.path.join(icons_dir, "icon_fireball_64_v1.png"))

    progress = check_progress(reqs, out_dir)
    assert progress["characters"]["total"] == 2
    assert progress["characters"]["done"] == 1
    assert "fire_mage" in progress["characters"]["completed"]
    assert "ice_archer" in progress["characters"]["missing"]
    assert progress["icons"]["done"] == 1
    assert "healing" in progress["icons"]["missing"]
```

- [ ] **Step 2: Run new tests to verify they fail**

```bash
python3 -m pytest tests/test_config.py -v
```

- [ ] **Step 3: Add requirements and progress functions to config.py**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_config.py -v
```

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/config.py tests/test_config.py
git commit -m "feat: add project requirements and progress tracking"
```

---

## Task 4: Dashboard in Asset Manager

**Files:**
- Modify: `game_asset_tools/manager.py`
- Modify: `tests/test_manager.py`

- [ ] **Step 1: Add failing test**

Add to `tests/test_manager.py`:

```python
def test_manager_with_progress_dashboard(tmp_dir):
    """Manager should show progress dashboard when project config has requirements."""
    out_dir = os.path.join(tmp_dir, "output")
    icons_dir = os.path.join(out_dir, "icons")
    os.makedirs(icons_dir)
    Image.new("RGBA", (64, 64), (200, 100, 100, 255)).save(os.path.join(icons_dir, "icon_fireball_64.png"))

    # Create project config with requirements
    config_path = os.path.join(tmp_dir, "project.yaml")
    import yaml
    config = {
        "project": {"name": "Test RPG", "engine": "unity"},
        "style": {"preset": "anime", "keywords": "", "palette": []},
        "assets": {},
        "output": {"base_dir": "output/", "naming": "{type}_{name}"},
        "requirements": {
            "icons": [
                {"name": "fireball"},
                {"name": "ice_arrow"},
                {"name": "healing"},
            ]
        },
    }
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, None, html_path, project_config=config_path)

    with open(html_path) as f:
        html = f.read()
    assert "1/3" in html or "33%" in html  # 1 of 3 icons complete
    assert "ice_arrow" in html or "healing" in html  # missing items listed
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_manager.py::test_manager_with_progress_dashboard -v
```

- [ ] **Step 3: Add project_config parameter and dashboard to manager.py**

Modify `generate_manager_html()` signature to accept `project_config=None`:

```python
def generate_manager_html(
    output_dir: str,
    manifest_path: str | None,
    html_path: str,
    project_name: str = "",
    project_config: str | None = None,
) -> None:
```

Add dashboard HTML generation before the grid:

```python
    # Generate progress dashboard if project config has requirements
    dashboard_html = ""
    if project_config and os.path.exists(project_config):
        from game_asset_tools.config import load_config, get_requirements, check_progress
        config = load_config(project_config)
        if not project_name:
            project_name = config.get("project", {}).get("name", "Game Assets")
        reqs = get_requirements(config)
        if reqs:
            progress = check_progress(reqs, output_dir)
            bars = ""
            missing_list = ""
            for cat, p in progress.items():
                pct = int(p["done"] / p["total"] * 100) if p["total"] > 0 else 0
                bars += f'<div class="pbar"><span class="plabel">{cat}: {p["done"]}/{p["total"]}</span><div class="ptrack"><div class="pfill" style="width:{pct}%"></div></div><span class="ppct">{pct}%</span></div>'
                if p["missing"]:
                    missing_list += f'<div class="pmissing">{cat}: {", ".join(p["missing"])}</div>'

            dashboard_html = f'''
<div class="dashboard">
  <h3>Project Progress</h3>
  <div class="pbars">{bars}</div>
  {f'<div class="missing-section"><h4>Missing:</h4>{missing_list}</div>' if missing_list else ''}
</div>'''
```

Add dashboard CSS and insert `{dashboard_html}` before the grid in the HTML template.

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_manager.py -v
```

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/manager.py tests/test_manager.py
git commit -m "feat: add progress dashboard to asset manager"
```

---

## Task 5: CLI Integration — export + atlas commands

**Files:**
- Modify: `game_asset_tools/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add failing CLI tests**

Add to `tests/test_cli.py`:

```python
def test_cli_export(tmp_dir):
    input_dir = os.path.join(tmp_dir, "output")
    icons_dir = os.path.join(input_dir, "icons")
    os.makedirs(icons_dir)
    Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(os.path.join(icons_dir, "test.png"))
    export_dir = os.path.join(tmp_dir, "web_export")
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "export",
         "--engine", "web", "--input-dir", input_dir, "--export-dir", export_dir],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert os.path.isdir(export_dir)


def test_cli_atlas(tmp_dir):
    sprites_dir = os.path.join(tmp_dir, "sprites")
    os.makedirs(sprites_dir)
    for i in range(4):
        Image.new("RGBA", (32, 32), (i * 60, 100, 100, 255)).save(os.path.join(sprites_dir, f"s{i}.png"))
    output = os.path.join(tmp_dir, "atlas.png")
    meta = os.path.join(tmp_dir, "atlas.json")
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "atlas",
         "--input-dir", sprites_dir, "--output", output, "--meta", meta,
         "--max-size", "512x512"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert os.path.exists(output)
    assert os.path.exists(meta)
```

- [ ] **Step 2: Run new tests to verify they fail**

- [ ] **Step 3: Add CLI commands**

```python
def _cmd_export(args):
    from game_asset_tools.export import export_for_engine
    result = export_for_engine(args.engine, args.input_dir, args.export_dir)
    print(f"Exported {result['total']} files for {args.engine} → {args.export_dir}")


def _cmd_atlas(args):
    from game_asset_tools.atlas import pack_atlas
    max_size = _parse_size(args.max_size)
    pack_atlas(
        args.input_dir, args.output, args.meta,
        max_size=max_size, padding=args.padding,
        meta_format=args.format,
    )
    print(f"Atlas packed: {args.output}, meta: {args.meta}")
```

Add to `_build_parser()`:

```python
    # --- export ---
    p_exp = subparsers.add_parser("export", help="Export assets for game engine")
    p_exp.add_argument("--engine", required=True, choices=["unity", "godot", "cocos", "web"])
    p_exp.add_argument("--input-dir", dest="input_dir", required=True)
    p_exp.add_argument("--export-dir", dest="export_dir", required=True)

    # --- atlas ---
    p_atl = subparsers.add_parser("atlas", help="Pack sprites into texture atlas")
    p_atl.add_argument("--input-dir", dest="input_dir", required=True)
    p_atl.add_argument("--output", required=True)
    p_atl.add_argument("--meta", required=True)
    p_atl.add_argument("--max-size", dest="max_size", default="2048x2048")
    p_atl.add_argument("--padding", type=int, default=2)
    p_atl.add_argument("--format", default="generic", choices=["generic", "phaser"])
```

Add to `_COMMAND_HANDLERS`:
```python
    "export": _cmd_export,
    "atlas": _cmd_atlas,
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_cli.py -v
```

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/cli.py tests/test_cli.py
git commit -m "feat: add export and atlas CLI commands"
```

---

## Task 6: Skill File Update + Integration Tests

**Files:**
- Modify: `skills/game-asset.md`
- Modify: `tests/test_integration.py`

- [ ] **Step 1: Add export/atlas/dashboard sections to skill file**

Add before "## Critical: Background Removal" in `skills/game-asset.md`:

```markdown
## Engine Export

Export all assets restructured for a target game engine:

```bash
python3 -m game_asset_tools export --engine unity --input-dir output/ --export-dir ./unity_export/
python3 -m game_asset_tools export --engine godot --input-dir output/ --export-dir ./godot_export/
python3 -m game_asset_tools export --engine web --input-dir output/ --export-dir ./web_export/
```

Supported engines: unity, godot, cocos, web

## Texture Atlas

Pack multiple small sprites into optimized texture atlases:

```bash
python3 -m game_asset_tools atlas --input-dir output/icons/ --output atlas.png --meta atlas.json --max-size 2048x2048 --padding 2 --format generic
```

Formats: generic (simple JSON), phaser (TexturePacker compatible)

## Project Progress

When project config has a `requirements` section, the asset manager page shows a progress dashboard. Generate manager with project config:

```bash
python3 -m game_asset_tools manager --output-dir output/ --manifest output/manifest.json --output asset_manager.html
```

Proactively suggest missing assets to the user based on requirements.
```

- [ ] **Step 2: Add integration tests**

Add to `tests/test_integration.py`:

```python
def test_atlas_pipeline(tmp_dir):
    """Pack icons into atlas and verify metadata."""
    from game_asset_tools.atlas import pack_atlas

    icons_dir = os.path.join(tmp_dir, "icons")
    os.makedirs(icons_dir)
    for i in range(8):
        Image.new("RGBA", (64, 64), (i * 30, 100, 200, 255)).save(
            os.path.join(icons_dir, f"icon_{i}.png")
        )

    atlas_path = os.path.join(tmp_dir, "atlas.png")
    meta_path = os.path.join(tmp_dir, "atlas.json")
    pack_atlas(icons_dir, atlas_path, meta_path, max_size=(256, 256), padding=2)

    assert os.path.exists(atlas_path)
    atlas = Image.open(atlas_path)
    assert atlas.width <= 256
    assert atlas.height <= 256

    with open(meta_path) as f:
        meta = json.load(f)
    total = sum(len(a["sprites"]) for a in meta["atlases"])
    assert total == 8


def test_export_pipeline(tmp_dir):
    """Export assets for web engine and verify structure."""
    from game_asset_tools.export import export_for_engine

    input_dir = os.path.join(tmp_dir, "output")
    for subdir in ["characters", "icons"]:
        d = os.path.join(input_dir, subdir)
        os.makedirs(d)
        Image.new("RGBA", (64, 64), (100, 100, 100, 255)).save(os.path.join(d, f"test.png"))

    export_dir = os.path.join(tmp_dir, "web_export")
    result = export_for_engine("web", input_dir, export_dir)
    assert result["total"] == 2
    assert os.path.exists(os.path.join(export_dir, "manifest.json"))
    assert os.path.isdir(os.path.join(export_dir, "images", "characters"))
```

- [ ] **Step 3: Run full test suite**

```bash
python3 -m pytest tests/ -v --tb=short
```

Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add skills/game-asset.md tests/test_integration.py
git commit -m "feat: add export/atlas/dashboard to skill, integration tests"
```
