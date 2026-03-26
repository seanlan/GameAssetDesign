# Game Asset Design Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code skill (`/game-asset`) with a Python post-processing toolkit that generates production-ready 2D game and card game assets.

**Architecture:** A single skill file orchestrates MCP AI image generation tools and delegates post-processing to a Python CLI toolkit (`game_asset_tools`). The toolkit handles background removal, resizing, sprite sheet assembly, card composition, video frame extraction, tileset assembly, and batch preview.

**Tech Stack:** Python 3.10+, Pillow, rembg, opencv-python-headless, numpy, PyYAML, Claude Code skill (Markdown)

**Spec:** `docs/superpowers/specs/2026-03-26-game-asset-skill-design.md`

---

## File Structure

```
GameAssetDesign/
├── game_asset_tools/
│   ├── __init__.py              # Package init, version
│   ├── __main__.py              # python3 -m game_asset_tools entry
│   ├── cli.py                   # CLI dispatcher (argparse)
│   ├── config.py                # Project config loader (YAML)
│   ├── naming.py                # Output naming template engine
│   ├── manifest.py              # Generation manifest (JSON read/write)
│   ├── remove_bg.py             # Background removal (rembg)
│   ├── resize.py                # Resize / crop / pad
│   ├── sprite_sheet.py          # Sprite sheet assembly + frame metadata
│   ├── card_composer.py         # Card layout composition + text rendering
│   ├── video_to_frames.py       # Video frame extraction + dedup
│   ├── tileset.py               # Tileset assembly + seamless blending
│   └── preview.py               # Batch HTML preview generator
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures (test images, temp dirs)
│   ├── test_config.py
│   ├── test_naming.py
│   ├── test_manifest.py
│   ├── test_remove_bg.py
│   ├── test_resize.py
│   ├── test_sprite_sheet.py
│   ├── test_card_composer.py
│   ├── test_video_to_frames.py
│   ├── test_tileset.py
│   ├── test_preview.py
│   └── test_cli.py
├── skills/
│   └── game-asset.md            # Claude Code skill file
├── templates/
│   ├── cards/
│   ├── ui/
│   └── fonts/
│       └── custom/
├── projects/
│   └── example_project.yaml
├── output/
│   ├── characters/
│   ├── backgrounds/
│   ├── ui/
│   ├── cards/
│   ├── icons/
│   ├── sprites/
│   └── tilesets/
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

---

## Task 1: Project Scaffolding & Dependencies

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `game_asset_tools/__init__.py`
- Create: `game_asset_tools/__main__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `projects/example_project.yaml`
- Create: directory structure for `templates/`, `output/`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "game-asset-tools"
version = "0.1.0"
description = "Python toolkit for game asset post-processing"
requires-python = ">=3.10"
dependencies = [
    "Pillow>=10.0",
    "rembg>=2.0",
    "opencv-python-headless>=4.8",
    "numpy>=1.24",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]
```

- [ ] **Step 2: Create requirements.txt**

```
Pillow>=10.0
rembg>=2.0
opencv-python-headless>=4.8
numpy>=1.24
pyyaml>=6.0
```

- [ ] **Step 3: Create requirements-dev.txt**

```
-r requirements.txt
pytest>=7.0
pytest-cov>=4.0
```

- [ ] **Step 4: Create game_asset_tools/__init__.py**

```python
"""Game Asset Tools - Python toolkit for game asset post-processing."""

__version__ = "0.1.0"
```

- [ ] **Step 5: Create game_asset_tools/__main__.py**

```python
"""Entry point for python3 -m game_asset_tools."""

from game_asset_tools.cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Create tests/__init__.py and tests/conftest.py**

```python
# tests/__init__.py
```

```python
# tests/conftest.py
import os
import tempfile
import pytest
from PIL import Image


@pytest.fixture
def tmp_dir():
    """Provide a temporary directory that is cleaned up after test."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sample_rgb_image(tmp_dir):
    """Create a 100x100 RGB test image and return its path."""
    path = os.path.join(tmp_dir, "test_rgb.png")
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    img.save(path)
    return path


@pytest.fixture
def sample_rgba_image(tmp_dir):
    """Create a 100x100 RGBA test image with a centered opaque circle on transparent bg."""
    path = os.path.join(tmp_dir, "test_rgba.png")
    img = Image.new("RGBA", (100, 100), color=(0, 0, 0, 0))
    # Draw a filled rectangle in the center as "subject"
    for x in range(25, 75):
        for y in range(25, 75):
            img.putpixel((x, y), (255, 0, 0, 255))
    img.save(path)
    return path


@pytest.fixture
def sample_frames(tmp_dir):
    """Create 4 numbered frame images in a subdirectory."""
    frames_dir = os.path.join(tmp_dir, "frames")
    os.makedirs(frames_dir)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    paths = []
    for i, color in enumerate(colors):
        path = os.path.join(frames_dir, f"frame_{i:03d}.png")
        img = Image.new("RGBA", (64, 64), color=(*color, 255))
        img.save(path)
        paths.append(path)
    return frames_dir, paths
```

- [ ] **Step 7: Create directory structure**

```bash
mkdir -p templates/cards templates/ui templates/fonts/custom
mkdir -p projects
mkdir -p output/{characters,backgrounds,ui,cards,icons,sprites,tilesets}
```

- [ ] **Step 8: Create projects/example_project.yaml**

```yaml
project:
  name: "Example RPG"
  engine: "unity"

style:
  preset: "anime"
  reference_image: null
  keywords: "vibrant colors, cel shading, fantasy theme"
  palette: ["#2C3E50", "#E74C3C", "#F39C12", "#27AE60"]

assets:
  character:
    sizes: [512, 1024]
    format: "png"
    transparent: true
  background:
    sizes: ["1920x1080", "1280x720"]
    format: "png"
    transparent: false
  icon:
    sizes: [64, 128, 256]
    format: "png"
    transparent: true
  card:
    size: "750x1050"
    template: "templates/cards/default.png"
    layout:
      artwork: [50, 50, 650, 600]
      title: [50, 660, 650, 60]
      description: [50, 740, 650, 200]
    text:
      font: "templates/fonts/NotoSansSC-Regular.ttf"
      title_size: 28
      title_color: "#FFFFFF"
      desc_size: 16
      desc_color: "#CCCCCC"
      align: "center"
      overflow: "shrink"
  sprite:
    frame_size: [128, 128]
    format: "png"
    transparent: true
  tileset:
    tile_size: [32, 32]
    format: "png"
  ui:
    sizes: [64, 128]
    format: "png"
    transparent: true
    states: ["normal", "hover", "pressed", "disabled"]

output:
  base_dir: "output/"
  naming: "{type}_{name}_{size}_{variant}"
```

- [ ] **Step 9: Install dependencies**

```bash
pip3 install -r requirements-dev.txt
```

- [ ] **Step 10: Verify setup**

```bash
python3 -c "import game_asset_tools; print(game_asset_tools.__version__)"
```

Expected: `0.1.0`

- [ ] **Step 11: Commit**

```bash
git init
git add pyproject.toml requirements.txt requirements-dev.txt
git add game_asset_tools/__init__.py game_asset_tools/__main__.py
git add tests/__init__.py tests/conftest.py
git add projects/example_project.yaml
git add templates/ output/
git commit -m "chore: scaffold project structure and dependencies"
```

---

## Task 2: Project Config Loader (`config.py`)

**Files:**
- Create: `game_asset_tools/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_config.py
import os
import pytest
from game_asset_tools.config import load_config, get_asset_config, get_style_keywords


def test_load_config_valid(tmp_dir):
    config_path = os.path.join(tmp_dir, "test.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test Game"
  engine: "unity"
style:
  preset: "anime"
  reference_image: null
  keywords: "fantasy theme"
  palette: ["#FF0000"]
assets:
  character:
    sizes: [512]
    format: "png"
    transparent: true
output:
  base_dir: "output/"
  naming: "{type}_{name}_{size}"
""")
    config = load_config(config_path)
    assert config["project"]["name"] == "Test Game"
    assert config["style"]["preset"] == "anime"


def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path.yaml")


def test_get_asset_config(tmp_dir):
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
assets:
  character:
    sizes: [512, 1024]
    format: "png"
    transparent: true
  icon:
    sizes: [64]
    format: "png"
    transparent: true
output:
  base_dir: "output/"
  naming: "{type}_{name}"
""")
    config = load_config(config_path)
    char_config = get_asset_config(config, "character")
    assert char_config["sizes"] == [512, 1024]
    assert char_config["transparent"] is True

    icon_config = get_asset_config(config, "icon")
    assert icon_config["sizes"] == [64]


def test_get_asset_config_unknown_type(tmp_dir):
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
    result = get_asset_config(config, "nonexistent")
    assert result is None


def test_get_style_keywords_with_preset(tmp_dir):
    config_path = os.path.join(tmp_dir, "test.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test"
  engine: "unity"
style:
  preset: "anime"
  keywords: "fantasy theme"
  palette: ["#FF0000", "#00FF00"]
assets: {}
output:
  base_dir: "output/"
  naming: "{type}_{name}"
""")
    config = load_config(config_path)
    keywords = get_style_keywords(config)
    assert "anime style" in keywords
    assert "fantasy theme" in keywords
    assert "#FF0000" in keywords


def test_load_config_validates_required_keys(tmp_dir):
    config_path = os.path.join(tmp_dir, "bad.yaml")
    with open(config_path, "w") as f:
        f.write("foo: bar\n")
    with pytest.raises(ValueError, match="Missing required"):
        load_config(config_path)


def test_load_config_validates_preset(tmp_dir):
    config_path = os.path.join(tmp_dir, "bad.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test"
  engine: "unity"
style:
  preset: "nonexistent_style"
  keywords: ""
  palette: []
assets: {}
output:
  base_dir: "output/"
  naming: "{type}_{name}"
""")
    with pytest.raises(ValueError, match="Unknown preset"):
        load_config(config_path)


def test_get_style_keywords_pixel_preset(tmp_dir):
    config_path = os.path.join(tmp_dir, "test.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test"
  engine: "unity"
style:
  preset: "pixel"
  keywords: ""
  palette: []
assets: {}
output:
  base_dir: "output/"
  naming: "{type}_{name}"
""")
    config = load_config(config_path)
    keywords = get_style_keywords(config)
    assert "pixel art" in keywords
    assert "16-bit style" in keywords
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_config.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'game_asset_tools.config'`

- [ ] **Step 3: Implement config.py**

```python
# game_asset_tools/config.py
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

# Mapping from preset name to NanoBanana style enum (None if not available)
PRESET_TO_NANOBANANA = {
    "pixel": None,
    "anime": "anime",
    "cel_shading": None,
    "watercolor": "watercolor",
    "flat": None,
    "realistic": None,
}

# Mapping from preset name to Gemini style string
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

    # Validate required top-level keys
    required = ["project", "style", "output"]
    missing = [k for k in required if k not in config]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")

    # Validate preset if specified
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
    """Build the full style keyword string from config (preset + keywords + palette)."""
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_config.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/config.py tests/test_config.py
git commit -m "feat: add project config loader with style presets"
```

---

## Task 3: Output Naming Engine (`naming.py`)

**Files:**
- Create: `game_asset_tools/naming.py`
- Create: `tests/test_naming.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_naming.py
from game_asset_tools.naming import generate_filename, find_next_variant


def test_generate_filename_basic():
    result = generate_filename(
        template="{type}_{name}_{size}_{variant}",
        asset_type="character",
        name="fire_mage",
        size="512",
        variant="v1",
    )
    assert result == "char_fire_mage_512_v1.png"


def test_generate_filename_with_action():
    result = generate_filename(
        template="{type}_{name}_{action}_{size}",
        asset_type="sprite",
        name="warrior",
        size="128x128",
        action="walk",
    )
    assert result == "sprite_warrior_walk_128x128.png"


def test_generate_filename_with_timestamp():
    result = generate_filename(
        template="{type}_{name}_{timestamp}",
        asset_type="icon",
        name="potion",
        timestamp="20260326_143022",
    )
    assert result == "icon_potion_20260326_143022.png"


def test_type_abbreviation():
    result = generate_filename(
        template="{type}_{name}",
        asset_type="character",
        name="test",
    )
    assert result.startswith("char_")


def test_type_abbreviation_background():
    result = generate_filename(
        template="{type}_{name}",
        asset_type="background",
        name="forest",
    )
    assert result.startswith("bg_")


def test_find_next_variant(tmp_dir):
    import os
    # Create existing files
    open(os.path.join(tmp_dir, "char_mage_512_v1.png"), "w").close()
    open(os.path.join(tmp_dir, "char_mage_512_v2.png"), "w").close()
    variant = find_next_variant(tmp_dir, "char_mage_512")
    assert variant == "v3"


def test_find_next_variant_no_existing(tmp_dir):
    variant = find_next_variant(tmp_dir, "char_mage_512")
    assert variant == "v1"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_naming.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement naming.py**

```python
# game_asset_tools/naming.py
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

    # Clean up double underscores from empty fields
    while "__" in result:
        result = result.replace("__", "_")
    result = result.strip("_")

    return f"{result}.{ext}"


def find_next_variant(directory: str, base_name: str) -> str:
    """Find the next available variant number (v1, v2, ...) in a directory."""
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_naming.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/naming.py tests/test_naming.py
git commit -m "feat: add output naming template engine"
```

---

## Task 4: Generation Manifest (`manifest.py`)

**Files:**
- Create: `game_asset_tools/manifest.py`
- Create: `tests/test_manifest.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_manifest.py
import os
import json
from game_asset_tools.manifest import Manifest


def test_create_new_manifest(tmp_dir):
    m = Manifest(tmp_dir, "test_project")
    m.add_entry(
        file="characters/char_mage_v1.png",
        asset_type="character",
        prompt="A fire mage",
        model="gemini",
        style="anime",
        aspect_ratio="1:1",
        raw_file=".tmp/raw/mage.png",
        post_processing=["remove_bg", "resize:512x512"],
        preset="anime",
    )
    m.save()

    manifest_path = os.path.join(tmp_dir, "manifest.json")
    assert os.path.exists(manifest_path)

    with open(manifest_path) as f:
        data = json.load(f)
    assert data["project"] == "test_project"
    assert len(data["assets"]) == 1
    assert data["assets"][0]["file"] == "characters/char_mage_v1.png"


def test_append_to_existing_manifest(tmp_dir):
    m = Manifest(tmp_dir, "test_project")
    m.add_entry(file="a.png", asset_type="icon", prompt="icon1", model="gemini")
    m.save()

    m2 = Manifest(tmp_dir, "test_project")
    m2.add_entry(file="b.png", asset_type="icon", prompt="icon2", model="gemini")
    m2.save()

    with open(os.path.join(tmp_dir, "manifest.json")) as f:
        data = json.load(f)
    assert len(data["assets"]) == 2


def test_manifest_entry_has_timestamp(tmp_dir):
    m = Manifest(tmp_dir, "test_project")
    m.add_entry(file="a.png", asset_type="icon", prompt="test", model="gemini")
    m.save()

    with open(os.path.join(tmp_dir, "manifest.json")) as f:
        data = json.load(f)
    assert "generated_at" in data["assets"][0]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_manifest.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement manifest.py**

```python
# game_asset_tools/manifest.py
"""Generation manifest for asset traceability."""

import json
import os
from datetime import datetime, timezone


class Manifest:
    """Manages a manifest.json file tracking generated assets."""

    def __init__(self, output_dir: str, project_name: str):
        self.path = os.path.join(output_dir, "manifest.json")
        self.project_name = project_name
        self.entries: list[dict] = []

        # Load existing manifest if present
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.entries = data.get("assets", [])

    def add_entry(
        self,
        file: str,
        asset_type: str,
        prompt: str,
        model: str,
        style: str = "",
        aspect_ratio: str = "",
        raw_file: str = "",
        post_processing: list[str] | None = None,
        preset: str = "",
        reference_image: str | None = None,
        project_config: str = "",
    ) -> None:
        """Add a generation record."""
        entry = {
            "file": file,
            "type": asset_type,
            "prompt": prompt,
            "model": model,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        if style:
            entry["style"] = style
        if aspect_ratio:
            entry["aspect_ratio"] = aspect_ratio
        if raw_file:
            entry["raw_file"] = raw_file
        if post_processing:
            entry["post_processing"] = post_processing
        if preset:
            entry["preset"] = preset
        if reference_image:
            entry["reference_image"] = reference_image
        if project_config:
            entry["project_config"] = project_config

        self.entries.append(entry)

    def save(self) -> None:
        """Write manifest to disk."""
        data = {
            "project": self.project_name,
            "assets": self.entries,
        }
        os.makedirs(os.path.dirname(self.path) if os.path.dirname(self.path) else ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_manifest.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/manifest.py tests/test_manifest.py
git commit -m "feat: add generation manifest for asset traceability"
```

---

## Task 5: Resize Module (`resize.py`)

**Files:**
- Create: `game_asset_tools/resize.py`
- Create: `tests/test_resize.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_resize.py
import os
from PIL import Image
from game_asset_tools.resize import resize_image


def test_resize_contain(sample_rgb_image, tmp_dir):
    output = os.path.join(tmp_dir, "out.png")
    resize_image(sample_rgb_image, output, size=(64, 64), mode="contain")
    img = Image.open(output)
    assert img.size == (64, 64)
    assert img.mode == "RGBA"  # contain adds transparency for padding


def test_resize_cover(sample_rgb_image, tmp_dir):
    output = os.path.join(tmp_dir, "out.png")
    resize_image(sample_rgb_image, output, size=(50, 80), mode="cover")
    img = Image.open(output)
    assert img.size == (50, 80)


def test_resize_stretch(sample_rgb_image, tmp_dir):
    output = os.path.join(tmp_dir, "out.png")
    resize_image(sample_rgb_image, output, size=(200, 50), mode="stretch")
    img = Image.open(output)
    assert img.size == (200, 50)


def test_resize_contain_preserves_transparency(sample_rgba_image, tmp_dir):
    output = os.path.join(tmp_dir, "out.png")
    resize_image(sample_rgba_image, output, size=(64, 64), mode="contain")
    img = Image.open(output)
    assert img.mode == "RGBA"
    # Corner pixel should be transparent (padding)
    corner = img.getpixel((0, 0))
    assert corner[3] == 0


def test_resize_batch(sample_rgb_image, tmp_dir):
    from game_asset_tools.resize import resize_batch
    # Create input dir with images
    in_dir = os.path.join(tmp_dir, "in")
    out_dir = os.path.join(tmp_dir, "out")
    os.makedirs(in_dir)
    os.makedirs(out_dir)
    # Copy sample to input dir
    img = Image.open(sample_rgb_image)
    img.save(os.path.join(in_dir, "a.png"))
    img.save(os.path.join(in_dir, "b.png"))

    resize_batch(in_dir, out_dir, size=(32, 32), mode="contain")
    assert len(os.listdir(out_dir)) == 2
    for f in os.listdir(out_dir):
        result = Image.open(os.path.join(out_dir, f))
        assert result.size == (32, 32)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_resize.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement resize.py**

```python
# game_asset_tools/resize.py
"""Image resize, crop, and pad utilities."""

import os
from PIL import Image


def resize_image(
    input_path: str,
    output_path: str,
    size: tuple[int, int],
    mode: str = "contain",
) -> None:
    """Resize an image to target size.

    Modes:
        contain: fit inside size, pad with transparency to fill
        cover: fill size, crop excess
        stretch: distort to exact size
    """
    img = Image.open(input_path).convert("RGBA")
    target_w, target_h = size

    if mode == "stretch":
        result = img.resize((target_w, target_h), Image.LANCZOS)

    elif mode == "contain":
        # Scale to fit within target, then pad
        ratio = min(target_w / img.width, target_h / img.height)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        resized = img.resize((new_w, new_h), Image.LANCZOS)
        result = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        offset_x = (target_w - new_w) // 2
        offset_y = (target_h - new_h) // 2
        result.paste(resized, (offset_x, offset_y), resized)

    elif mode == "cover":
        # Scale to fill target, then center crop
        ratio = max(target_w / img.width, target_h / img.height)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        resized = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        result = resized.crop((left, top, left + target_w, top + target_h))

    else:
        raise ValueError(f"Unknown resize mode: {mode}")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    result.save(output_path, "PNG")


def resize_batch(
    input_dir: str,
    output_dir: str,
    size: tuple[int, int],
    mode: str = "contain",
) -> list[str]:
    """Resize all PNG images in input_dir, save to output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    results = []
    for fname in sorted(os.listdir(input_dir)):
        if fname.lower().endswith((".png", ".jpg", ".jpeg")):
            in_path = os.path.join(input_dir, fname)
            out_path = os.path.join(output_dir, fname)
            resize_image(in_path, out_path, size, mode)
            results.append(out_path)
    return results
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_resize.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/resize.py tests/test_resize.py
git commit -m "feat: add image resize module with contain/cover/stretch modes"
```

---

## Task 6: Background Removal Module (`remove_bg.py`)

**Files:**
- Create: `game_asset_tools/remove_bg.py`
- Create: `tests/test_remove_bg.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_remove_bg.py
import os
import pytest
from PIL import Image
from game_asset_tools.remove_bg import remove_background, is_rembg_available


def test_is_rembg_available():
    # Should return True or False without error
    result = is_rembg_available()
    assert isinstance(result, bool)


def test_remove_background_outputs_rgba(sample_rgb_image, tmp_dir):
    if not is_rembg_available():
        pytest.skip("rembg not installed")
    output = os.path.join(tmp_dir, "no_bg.png")
    remove_background(sample_rgb_image, output)
    img = Image.open(output)
    assert img.mode == "RGBA"


def test_remove_background_file_not_found(tmp_dir):
    output = os.path.join(tmp_dir, "out.png")
    with pytest.raises(FileNotFoundError):
        remove_background("/nonexistent/image.png", output)


def test_remove_background_batch(sample_rgb_image, tmp_dir):
    if not is_rembg_available():
        pytest.skip("rembg not installed")
    from game_asset_tools.remove_bg import remove_background_batch
    in_dir = os.path.join(tmp_dir, "in")
    out_dir = os.path.join(tmp_dir, "out")
    os.makedirs(in_dir)
    img = Image.open(sample_rgb_image)
    img.save(os.path.join(in_dir, "a.png"))
    img.save(os.path.join(in_dir, "b.png"))

    remove_background_batch(in_dir, out_dir)
    assert len(os.listdir(out_dir)) == 2
    for f in os.listdir(out_dir):
        result = Image.open(os.path.join(out_dir, f))
        assert result.mode == "RGBA"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_remove_bg.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement remove_bg.py**

```python
# game_asset_tools/remove_bg.py
"""Background removal using rembg."""

import os
from PIL import Image


def is_rembg_available() -> bool:
    """Check if rembg is installed."""
    try:
        import rembg  # noqa: F401
        return True
    except ImportError:
        return False


def remove_background(input_path: str, output_path: str) -> None:
    """Remove background from an image, output RGBA PNG."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Image not found: {input_path}")

    if not is_rembg_available():
        raise RuntimeError(
            "rembg is not installed. Install with: pip install rembg"
        )

    from rembg import remove

    img = Image.open(input_path)
    result = remove(img)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    result.save(output_path, "PNG")


def remove_background_batch(input_dir: str, output_dir: str) -> list[str]:
    """Remove background from all images in a directory."""
    os.makedirs(output_dir, exist_ok=True)
    results = []
    for fname in sorted(os.listdir(input_dir)):
        if fname.lower().endswith((".png", ".jpg", ".jpeg")):
            in_path = os.path.join(input_dir, fname)
            out_path = os.path.join(output_dir, fname)
            remove_background(in_path, out_path)
            results.append(out_path)
    return results
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_remove_bg.py -v
```

Expected: All PASS (some skipped if rembg not installed)

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/remove_bg.py tests/test_remove_bg.py
git commit -m "feat: add background removal module with rembg"
```

---

## Task 7: Sprite Sheet Module (`sprite_sheet.py`)

**Files:**
- Create: `game_asset_tools/sprite_sheet.py`
- Create: `tests/test_sprite_sheet.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_sprite_sheet.py
import os
import json
from PIL import Image
from game_asset_tools.sprite_sheet import assemble_sprite_sheet


def test_assemble_basic(sample_frames, tmp_dir):
    frames_dir, _ = sample_frames
    output = os.path.join(tmp_dir, "sheet.png")
    meta_output = os.path.join(tmp_dir, "sheet.json")

    assemble_sprite_sheet(
        input_dir=frames_dir,
        output_path=output,
        meta_path=meta_output,
        cols=2,
        frame_size=(64, 64),
    )

    sheet = Image.open(output)
    # 4 frames, 2 cols → 2 rows → 128x128
    assert sheet.size == (128, 128)

    with open(meta_output) as f:
        meta = json.load(f)
    assert len(meta["frames"]) == 4
    assert meta["frames"][0]["frame"]["x"] == 0
    assert meta["frames"][0]["frame"]["y"] == 0
    assert meta["frames"][0]["frame"]["w"] == 64
    assert meta["frames"][0]["frame"]["h"] == 64


def test_assemble_auto_cols(sample_frames, tmp_dir):
    frames_dir, _ = sample_frames
    output = os.path.join(tmp_dir, "sheet.png")
    meta_output = os.path.join(tmp_dir, "sheet.json")

    assemble_sprite_sheet(
        input_dir=frames_dir,
        output_path=output,
        meta_path=meta_output,
        frame_size=(64, 64),
    )

    sheet = Image.open(output)
    assert sheet.size[0] > 0
    assert sheet.size[1] > 0


def test_assemble_resizes_frames(tmp_dir):
    """Frames of different sizes should be normalized to frame_size."""
    frames_dir = os.path.join(tmp_dir, "mixed")
    os.makedirs(frames_dir)
    Image.new("RGBA", (100, 100), (255, 0, 0, 255)).save(
        os.path.join(frames_dir, "frame_000.png")
    )
    Image.new("RGBA", (50, 80), (0, 255, 0, 255)).save(
        os.path.join(frames_dir, "frame_001.png")
    )

    output = os.path.join(tmp_dir, "sheet.png")
    meta_output = os.path.join(tmp_dir, "sheet.json")
    assemble_sprite_sheet(
        input_dir=frames_dir,
        output_path=output,
        meta_path=meta_output,
        cols=2,
        frame_size=(64, 64),
    )
    sheet = Image.open(output)
    assert sheet.size == (128, 64)


def test_meta_format_phaser_compatible(sample_frames, tmp_dir):
    frames_dir, _ = sample_frames
    output = os.path.join(tmp_dir, "sheet.png")
    meta_output = os.path.join(tmp_dir, "sheet.json")

    assemble_sprite_sheet(
        input_dir=frames_dir,
        output_path=output,
        meta_path=meta_output,
        cols=2,
        frame_size=(64, 64),
    )

    with open(meta_output) as f:
        meta = json.load(f)
    # Phaser-compatible structure
    assert "frames" in meta
    assert "meta" in meta
    assert meta["meta"]["image"] == "sheet.png"
    frame = meta["frames"][0]
    assert "frame" in frame
    assert "sourceSize" in frame
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_sprite_sheet.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement sprite_sheet.py**

```python
# game_asset_tools/sprite_sheet.py
"""Sprite sheet assembly and frame metadata export."""

import json
import math
import os
from PIL import Image

from game_asset_tools.resize import resize_image


def assemble_sprite_sheet(
    input_dir: str,
    output_path: str,
    meta_path: str,
    frame_size: tuple[int, int],
    cols: int | None = None,
) -> None:
    """Assemble individual frame images into a sprite sheet.

    Args:
        input_dir: directory containing frame images (sorted by filename)
        output_path: path for the output sprite sheet PNG
        meta_path: path for the output JSON metadata
        frame_size: (width, height) for each frame in the sheet
        cols: number of columns (auto-calculated if None)
    """
    # Collect and sort frame files
    frame_files = sorted(
        f for f in os.listdir(input_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    )

    if not frame_files:
        raise ValueError(f"No image files found in {input_dir}")

    num_frames = len(frame_files)
    fw, fh = frame_size

    if cols is None:
        cols = math.ceil(math.sqrt(num_frames))
    rows = math.ceil(num_frames / cols)

    # Create the sheet
    sheet = Image.new("RGBA", (cols * fw, rows * fh), (0, 0, 0, 0))
    frames_meta = []

    for idx, fname in enumerate(frame_files):
        src_path = os.path.join(input_dir, fname)
        img = Image.open(src_path).convert("RGBA")

        # Resize frame if needed (contain mode to preserve aspect ratio)
        if img.size != frame_size:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            resize_image(src_path, tmp_path, frame_size, mode="contain")
            img = Image.open(tmp_path).convert("RGBA")
            os.unlink(tmp_path)

        col = idx % cols
        row = idx // cols
        x = col * fw
        y = row * fh
        sheet.paste(img, (x, y), img)

        frames_meta.append({
            "filename": fname,
            "frame": {"x": x, "y": y, "w": fw, "h": fh},
            "sourceSize": {"w": fw, "h": fh},
            "spriteSourceSize": {"x": 0, "y": 0, "w": fw, "h": fh},
        })

    # Save sheet
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    sheet.save(output_path, "PNG")

    # Save metadata (Phaser/TexturePacker compatible)
    meta = {
        "frames": frames_meta,
        "meta": {
            "image": os.path.basename(output_path),
            "size": {"w": cols * fw, "h": rows * fh},
            "format": "RGBA8888",
            "scale": 1,
        },
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_sprite_sheet.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/sprite_sheet.py tests/test_sprite_sheet.py
git commit -m "feat: add sprite sheet assembly with Phaser-compatible metadata"
```

---

## Task 8: Card Composer Module (`card_composer.py`)

**Files:**
- Create: `game_asset_tools/card_composer.py`
- Create: `tests/test_card_composer.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_card_composer.py
import os
from PIL import Image
from game_asset_tools.card_composer import compose_card


def test_compose_card_basic(sample_rgb_image, tmp_dir):
    """Compose a card with artwork only (no template)."""
    output = os.path.join(tmp_dir, "card.png")
    compose_card(
        artwork_path=sample_rgb_image,
        output_path=output,
        card_size=(750, 1050),
        artwork_region=(50, 50, 650, 600),
    )
    card = Image.open(output)
    assert card.size == (750, 1050)


def test_compose_card_with_template(tmp_dir):
    """Compose a card using a border template."""
    # Create a template (border frame)
    template_path = os.path.join(tmp_dir, "border.png")
    template = Image.new("RGBA", (750, 1050), (50, 50, 50, 255))
    # Cut out artwork area (transparent center)
    for x in range(50, 700):
        for y in range(50, 650):
            template.putpixel((x, y), (0, 0, 0, 0))
    template.save(template_path)

    # Create artwork
    artwork_path = os.path.join(tmp_dir, "art.png")
    Image.new("RGB", (300, 300), (255, 0, 0)).save(artwork_path)

    output = os.path.join(tmp_dir, "card.png")
    compose_card(
        artwork_path=artwork_path,
        output_path=output,
        card_size=(750, 1050),
        artwork_region=(50, 50, 650, 600),
        template_path=template_path,
    )
    card = Image.open(output)
    assert card.size == (750, 1050)


def test_compose_card_with_text(sample_rgb_image, tmp_dir):
    """Compose a card with title text."""
    output = os.path.join(tmp_dir, "card.png")
    compose_card(
        artwork_path=sample_rgb_image,
        output_path=output,
        card_size=(750, 1050),
        artwork_region=(50, 50, 650, 600),
        title="Fire Mage",
        title_region=(50, 660, 650, 60),
        title_color="#FFFFFF",
        title_size=28,
    )
    card = Image.open(output)
    assert card.size == (750, 1050)


def test_compose_card_with_description(sample_rgb_image, tmp_dir):
    """Compose a card with both title and description."""
    output = os.path.join(tmp_dir, "card.png")
    compose_card(
        artwork_path=sample_rgb_image,
        output_path=output,
        card_size=(750, 1050),
        artwork_region=(50, 50, 650, 600),
        title="Fire Mage",
        title_region=(50, 660, 650, 60),
        description="A powerful mage who controls fire magic",
        desc_region=(50, 740, 650, 200),
        desc_color="#CCCCCC",
        desc_size=16,
        overflow="wrap",
    )
    card = Image.open(output)
    assert card.size == (750, 1050)


def test_compose_card_truncate_long_title(sample_rgb_image, tmp_dir):
    """A very long title should be truncated with ellipsis."""
    output = os.path.join(tmp_dir, "card.png")
    compose_card(
        artwork_path=sample_rgb_image,
        output_path=output,
        card_size=(750, 1050),
        artwork_region=(50, 50, 650, 600),
        title="This Is An Extremely Long Card Title That Should Be Truncated",
        title_region=(50, 660, 200, 60),  # narrow region to force truncation
        title_size=28,
        overflow="truncate",
    )
    card = Image.open(output)
    assert card.size == (750, 1050)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_card_composer.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement card_composer.py**

```python
# game_asset_tools/card_composer.py
"""Card layout composition with artwork placement and text rendering."""

import os
from PIL import Image, ImageDraw, ImageFont


def _find_project_root() -> str:
    """Find the project root by looking for pyproject.toml or templates/ dir."""
    # Start from this file's location, walk up
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        if os.path.exists(os.path.join(current, "pyproject.toml")) or \
           os.path.exists(os.path.join(current, "templates")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.abspath(__file__))


def _load_font(font_path: str | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a font file, falling back to default."""
    if font_path and os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)

    # Try bundled default (resolve from project root)
    root = _find_project_root()
    default_paths = [
        os.path.join(root, "templates", "fonts", "NotoSansSC-Regular.ttf"),
        os.path.join(root, "templates", "fonts", "NotoSansSC-Bold.ttf"),
    ]
    for p in default_paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)

    return ImageFont.load_default()


def _draw_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    region: tuple[int, int, int, int],
    color: str = "#FFFFFF",
    font_size: int = 24,
    font_path: str | None = None,
    align: str = "center",
    overflow: str = "truncate",
) -> None:
    """Draw text within a region."""
    rx, ry, rw, rh = region
    font = _load_font(font_path, font_size)

    if overflow == "shrink":
        # Reduce font size until text fits
        while font_size > 8:
            bbox = font.getbbox(text)
            text_w = bbox[2] - bbox[0]
            if text_w <= rw:
                break
            font_size -= 1
            font = _load_font(font_path, font_size)

    elif overflow == "truncate":
        # Truncate text if too wide
        original_len = len(text)
        bbox = font.getbbox(text)
        text_w = bbox[2] - bbox[0]
        while text_w > rw and len(text) > 1:
            text = text[:-1]
            bbox = font.getbbox(text + "...")
            text_w = bbox[2] - bbox[0]
        if len(text) < original_len:
            text = text + "..."

    elif overflow == "wrap":
        # Wrap text to multiple lines within the region
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = font.getbbox(test_line)
            test_w = bbox[2] - bbox[0]
            if test_w <= rw:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        # Draw each line
        line_height = font.getbbox("Ag")[3] - font.getbbox("Ag")[1] + 4
        for i, line in enumerate(lines):
            ly = ry + i * line_height
            if ly + line_height > ry + rh:
                break  # Don't draw beyond region
            bbox = font.getbbox(line)
            lw = bbox[2] - bbox[0]
            if align == "center":
                lx = rx + (rw - lw) // 2
            elif align == "right":
                lx = rx + rw - lw
            else:
                lx = rx
            draw.text((lx, ly), line, fill=color, font=font)
        return  # wrap handles its own drawing

    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    if align == "center":
        tx = rx + (rw - text_w) // 2
    elif align == "right":
        tx = rx + rw - text_w
    else:
        tx = rx

    ty = ry + (rh - text_h) // 2
    draw.text((tx, ty), text, fill=color, font=font)


def compose_card(
    artwork_path: str,
    output_path: str,
    card_size: tuple[int, int],
    artwork_region: tuple[int, int, int, int],
    template_path: str | None = None,
    title: str = "",
    title_region: tuple[int, int, int, int] | None = None,
    title_color: str = "#FFFFFF",
    title_size: int = 28,
    description: str = "",
    desc_region: tuple[int, int, int, int] | None = None,
    desc_color: str = "#CCCCCC",
    desc_size: int = 16,
    font_path: str | None = None,
    align: str = "center",
    overflow: str = "truncate",
) -> None:
    """Compose a card by placing artwork into a template with text."""
    card_w, card_h = card_size
    ax, ay, aw, ah = artwork_region

    # Start with blank card or template
    if template_path and os.path.exists(template_path):
        card = Image.open(template_path).convert("RGBA")
        card = card.resize(card_size, Image.LANCZOS)
    else:
        card = Image.new("RGBA", card_size, (30, 30, 30, 255))

    # Place artwork
    artwork = Image.open(artwork_path).convert("RGBA")
    # Resize artwork to fit the artwork region (cover mode)
    ratio = max(aw / artwork.width, ah / artwork.height)
    new_w = int(artwork.width * ratio)
    new_h = int(artwork.height * ratio)
    artwork = artwork.resize((new_w, new_h), Image.LANCZOS)
    # Center crop
    left = (new_w - aw) // 2
    top = (new_h - ah) // 2
    artwork = artwork.crop((left, top, left + aw, top + ah))

    # Paste artwork under the template
    base = Image.new("RGBA", card_size, (0, 0, 0, 0))
    base.paste(artwork, (ax, ay), artwork)
    base = Image.alpha_composite(base, card)
    card = base

    # Draw text
    draw = ImageDraw.Draw(card)
    if title and title_region:
        _draw_text(draw, title, title_region, title_color, title_size, font_path, align, overflow)
    if description and desc_region:
        _draw_text(draw, description, desc_region, desc_color, desc_size, font_path, align, overflow)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    card.save(output_path, "PNG")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_card_composer.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/card_composer.py tests/test_card_composer.py
git commit -m "feat: add card composer with artwork placement and text rendering"
```

---

## Task 9: Video Frame Extraction (`video_to_frames.py`)

**Files:**
- Create: `game_asset_tools/video_to_frames.py`
- Create: `tests/test_video_to_frames.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_video_to_frames.py
import os
import pytest
from game_asset_tools.video_to_frames import extract_frames, is_opencv_available


def test_is_opencv_available():
    result = is_opencv_available()
    assert isinstance(result, bool)


@pytest.fixture
def sample_video(tmp_dir):
    """Create a minimal test video using OpenCV if available."""
    if not is_opencv_available():
        pytest.skip("opencv not installed")
    import cv2
    import numpy as np

    path = os.path.join(tmp_dir, "test.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, 10, (64, 64))
    for i in range(30):  # 3 seconds at 10fps
        frame = np.full((64, 64, 3), fill_value=(i * 8) % 256, dtype=np.uint8)
        writer.write(frame)
    writer.release()
    return path


def test_extract_frames_basic(sample_video, tmp_dir):
    out_dir = os.path.join(tmp_dir, "frames")
    count = extract_frames(sample_video, out_dir, fps=5)
    assert count > 0
    files = os.listdir(out_dir)
    assert len(files) == count
    assert all(f.endswith(".png") for f in files)


def test_extract_frames_with_dedup(sample_video, tmp_dir):
    out_dir = os.path.join(tmp_dir, "frames")
    count = extract_frames(sample_video, out_dir, fps=10, dedup=True, dedup_threshold=0.99)
    # With dedup, similar frames should be removed
    assert count > 0


def test_extract_frames_missing_file(tmp_dir):
    with pytest.raises(FileNotFoundError):
        extract_frames("/nonexistent/video.mp4", tmp_dir)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_video_to_frames.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement video_to_frames.py**

```python
# game_asset_tools/video_to_frames.py
"""Video frame extraction with optional deduplication."""

import os


def is_opencv_available() -> bool:
    """Check if OpenCV is installed."""
    try:
        import cv2  # noqa: F401
        return True
    except ImportError:
        return False


def extract_frames(
    video_path: str,
    output_dir: str,
    fps: int = 8,
    dedup: bool = False,
    dedup_threshold: float = 0.95,
) -> int:
    """Extract frames from a video at specified FPS.

    Args:
        video_path: path to input video
        output_dir: directory to save extracted frames
        fps: target frames per second to extract
        dedup: if True, skip frames that are too similar to the previous
        dedup_threshold: similarity threshold for dedup (0-1, higher = more similar)

    Returns:
        Number of frames extracted
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    if not is_opencv_available():
        raise RuntimeError(
            "opencv-python-headless is not installed. Install with: pip install opencv-python-headless"
        )

    import cv2
    import numpy as np

    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if video_fps <= 0:
        video_fps = 30  # fallback

    frame_interval = max(1, int(video_fps / fps))
    frame_idx = 0
    saved_count = 0
    prev_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_interval == 0:
            save = True

            if dedup and prev_frame is not None:
                # Compare with previous saved frame using normalized correlation
                similarity = _frame_similarity(prev_frame, frame)
                if similarity >= dedup_threshold:
                    save = False

            if save:
                out_path = os.path.join(output_dir, f"frame_{saved_count:04d}.png")
                cv2.imwrite(out_path, frame)
                prev_frame = frame.copy()
                saved_count += 1

        frame_idx += 1

    cap.release()
    return saved_count


def _frame_similarity(frame1, frame2) -> float:
    """Calculate similarity between two frames (0-1)."""
    import cv2
    import numpy as np

    # Convert to grayscale for comparison
    g1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY).astype(np.float32)
    g2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # Normalized cross-correlation
    result = cv2.matchTemplate(g1, g2, cv2.TM_CCORR_NORMED)
    return float(result[0][0])
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_video_to_frames.py -v
```

Expected: All PASS (some skipped if opencv not installed)

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/video_to_frames.py tests/test_video_to_frames.py
git commit -m "feat: add video frame extraction with deduplication"
```

---

## Task 10: Tileset Module (`tileset.py`)

**Files:**
- Create: `game_asset_tools/tileset.py`
- Create: `tests/test_tileset.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_tileset.py
import os
import json
from PIL import Image
from game_asset_tools.tileset import assemble_tileset, make_seamless


def test_assemble_tileset(tmp_dir):
    tiles_dir = os.path.join(tmp_dir, "tiles")
    os.makedirs(tiles_dir)
    for i in range(6):
        img = Image.new("RGBA", (32, 32), color=(i * 40, 100, 100, 255))
        img.save(os.path.join(tiles_dir, f"tile_{i:02d}.png"))

    output = os.path.join(tmp_dir, "tileset.png")
    meta = os.path.join(tmp_dir, "tileset.json")
    assemble_tileset(tiles_dir, output, meta, tile_size=(32, 32), cols=3)

    sheet = Image.open(output)
    assert sheet.size == (96, 64)  # 3 cols x 2 rows

    with open(meta) as f:
        data = json.load(f)
    assert len(data["tiles"]) == 6


def test_make_seamless(tmp_dir):
    # Create a tile with distinct edges
    tile_path = os.path.join(tmp_dir, "tile.png")
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 255))
    # Left edge bright, right edge dark → should be blended
    for y in range(32):
        for x in range(32):
            img.putpixel((x, y), (x * 8, 100, 100, 255))
    img.save(tile_path)

    output = os.path.join(tmp_dir, "seamless.png")
    make_seamless(tile_path, output, blend_width=4)
    result = Image.open(output)
    assert result.size == (32, 32)


def test_assemble_tileset_with_seamless(tmp_dir):
    tiles_dir = os.path.join(tmp_dir, "tiles")
    os.makedirs(tiles_dir)
    for i in range(4):
        img = Image.new("RGBA", (32, 32), color=(i * 60, 100, 100, 255))
        img.save(os.path.join(tiles_dir, f"tile_{i:02d}.png"))

    output = os.path.join(tmp_dir, "tileset.png")
    meta = os.path.join(tmp_dir, "tileset.json")
    assemble_tileset(tiles_dir, output, meta, tile_size=(32, 32), cols=2, seamless=True)

    sheet = Image.open(output)
    assert sheet.size == (64, 64)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_tileset.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement tileset.py**

```python
# game_asset_tools/tileset.py
"""Tileset assembly with optional seamless edge blending."""

import json
import math
import os
from PIL import Image
import numpy as np

from game_asset_tools.resize import resize_image


def make_seamless(
    input_path: str,
    output_path: str,
    blend_width: int = 8,
) -> None:
    """Make a tile seamless by blending opposite edges with mirrored strips."""
    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape[:2]
    bw = min(blend_width, w // 4, h // 4)

    if bw < 1:
        img.save(output_path)
        return

    result = arr.copy()

    # Horizontal seamless: blend left/right edges
    for i in range(bw):
        alpha = i / bw
        # Blend left edge with mirrored right edge
        result[:, i] = arr[:, i] * alpha + arr[:, w - bw + i] * (1 - alpha)
        result[:, w - bw + i] = arr[:, w - bw + i] * alpha + arr[:, i] * (1 - alpha)

    # Vertical seamless: blend top/bottom edges
    for i in range(bw):
        alpha = i / bw
        result[i, :] = result[i, :] * alpha + arr[h - bw + i, :] * (1 - alpha)
        result[h - bw + i, :] = result[h - bw + i, :] * alpha + arr[i, :] * (1 - alpha)

    result_img = Image.fromarray(result.astype(np.uint8))
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    result_img.save(output_path, "PNG")


def assemble_tileset(
    input_dir: str,
    output_path: str,
    meta_path: str,
    tile_size: tuple[int, int],
    cols: int | None = None,
    seamless: bool = False,
    blend_width: int = 8,
) -> None:
    """Assemble individual tiles into a tileset image.

    Args:
        input_dir: directory with individual tile images
        output_path: output tileset PNG path
        meta_path: output metadata JSON path
        tile_size: (width, height) per tile
        cols: columns in the tileset (auto if None)
        seamless: apply seamless edge blending to each tile
        blend_width: pixel width for seamless blending
    """
    tile_files = sorted(
        f for f in os.listdir(input_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    )

    if not tile_files:
        raise ValueError(f"No tile images found in {input_dir}")

    num_tiles = len(tile_files)
    tw, th = tile_size
    if cols is None:
        cols = math.ceil(math.sqrt(num_tiles))
    rows = math.ceil(num_tiles / cols)

    sheet = Image.new("RGBA", (cols * tw, rows * th), (0, 0, 0, 0))
    tiles_meta = []

    for idx, fname in enumerate(tile_files):
        src_path = os.path.join(input_dir, fname)
        img = Image.open(src_path).convert("RGBA")

        # Resize if needed
        if img.size != tile_size:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            resize_image(src_path, tmp_path, tile_size, mode="cover")
            img = Image.open(tmp_path).convert("RGBA")
            os.unlink(tmp_path)

        # Apply seamless blending
        if seamless:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_in = tmp.name
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_out = tmp.name
            img.save(tmp_in)
            make_seamless(tmp_in, tmp_out, blend_width)
            img = Image.open(tmp_out).convert("RGBA")
            os.unlink(tmp_in)
            os.unlink(tmp_out)

        col = idx % cols
        row = idx // cols
        x = col * tw
        y = row * th
        sheet.paste(img, (x, y), img)

        tiles_meta.append({
            "filename": fname,
            "index": idx,
            "x": x,
            "y": y,
            "w": tw,
            "h": th,
        })

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    sheet.save(output_path, "PNG")

    meta = {
        "tiles": tiles_meta,
        "meta": {
            "image": os.path.basename(output_path),
            "tile_size": {"w": tw, "h": th},
            "columns": cols,
            "rows": rows,
            "total": num_tiles,
        },
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_tileset.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/tileset.py tests/test_tileset.py
git commit -m "feat: add tileset assembly with seamless edge blending"
```

---

## Task 11: Preview Module (`preview.py`)

**Files:**
- Create: `game_asset_tools/preview.py`
- Create: `tests/test_preview.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_preview.py
import os
from PIL import Image
from game_asset_tools.preview import generate_preview_html


def test_generate_preview_html(tmp_dir):
    # Create some fake assets
    assets_dir = os.path.join(tmp_dir, "assets")
    os.makedirs(assets_dir)
    for i in range(3):
        img = Image.new("RGB", (64, 64), (i * 80, 100, 100))
        img.save(os.path.join(assets_dir, f"icon_{i}.png"))

    output = os.path.join(tmp_dir, "preview.html")
    generate_preview_html(assets_dir, output)
    assert os.path.exists(output)

    with open(output) as f:
        html = f.read()
    assert "icon_0.png" in html
    assert "icon_1.png" in html
    assert "icon_2.png" in html
    assert "<img" in html
    assert "64 x 64" in html


def test_generate_preview_html_empty_dir(tmp_dir):
    assets_dir = os.path.join(tmp_dir, "empty")
    os.makedirs(assets_dir)
    output = os.path.join(tmp_dir, "preview.html")
    generate_preview_html(assets_dir, output)
    assert os.path.exists(output)

    with open(output) as f:
        html = f.read()
    assert "No assets found" in html


def test_preview_uses_base64_embedding(tmp_dir):
    """Preview HTML should embed images as base64 for self-contained viewing."""
    assets_dir = os.path.join(tmp_dir, "assets")
    os.makedirs(assets_dir)
    Image.new("RGB", (32, 32), (255, 0, 0)).save(os.path.join(assets_dir, "test.png"))

    output = os.path.join(tmp_dir, "preview.html")
    generate_preview_html(assets_dir, output)

    with open(output) as f:
        html = f.read()
    assert "data:image/png;base64," in html
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_preview.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement preview.py**

```python
# game_asset_tools/preview.py
"""Batch asset preview HTML generator."""

import base64
import os
from PIL import Image


def generate_preview_html(
    input_dir: str,
    output_path: str,
    title: str = "Game Asset Preview",
) -> None:
    """Generate a self-contained HTML preview page for assets in a directory.

    Images are embedded as base64 data URIs so the HTML is fully self-contained.
    """
    image_files = sorted(
        f for f in os.listdir(input_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
    )

    cards_html = ""
    if not image_files:
        cards_html = '<p style="color:#888; text-align:center;">No assets found</p>'
    else:
        for fname in image_files:
            fpath = os.path.join(input_dir, fname)
            img = Image.open(fpath)
            w, h = img.size
            file_size = os.path.getsize(fpath)
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} B"

            # Embed as base64
            with open(fpath, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            ext = fname.rsplit(".", 1)[-1].lower()
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif"}.get(ext, "image/png")

            cards_html += f"""
        <div class="card">
            <img src="data:{mime};base64,{b64}" alt="{fname}">
            <div class="info">
                <div class="filename">{fname}</div>
                <div class="meta">{w} x {h} &middot; {size_str}</div>
            </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
h1 {{ text-align: center; color: #e94560; margin-bottom: 30px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; max-width: 1200px; margin: 0 auto; }}
.card {{ background: #16213e; border-radius: 8px; overflow: hidden; border: 1px solid #0f3460; }}
.card img {{ width: 100%; height: 180px; object-fit: contain; background: repeating-conic-gradient(#333 0% 25%, #444 0% 50%) 50% / 16px 16px; }}
.info {{ padding: 8px 12px; }}
.filename {{ font-size: 12px; font-weight: 600; word-break: break-all; }}
.meta {{ font-size: 11px; color: #888; margin-top: 4px; }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="grid">{cards_html}
</div>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_preview.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/preview.py tests/test_preview.py
git commit -m "feat: add batch asset preview HTML generator"
```

---

## Task 12: CLI Dispatcher (`cli.py`)

**Files:**
- Create: `game_asset_tools/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_cli.py
import os
import subprocess
import sys
from PIL import Image


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "game_asset_tools" in result.stdout.lower() or "usage" in result.stdout.lower()


def test_cli_resize(tmp_dir):
    # Create test image
    in_path = os.path.join(tmp_dir, "in.png")
    out_path = os.path.join(tmp_dir, "out.png")
    Image.new("RGB", (100, 100), (255, 0, 0)).save(in_path)

    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "resize",
         "--input", in_path, "--output", out_path,
         "--size", "64x64", "--mode", "contain"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert os.path.exists(out_path)
    img = Image.open(out_path)
    assert img.size == (64, 64)


def test_cli_sprite_sheet(sample_frames, tmp_dir):
    frames_dir, _ = sample_frames
    output = os.path.join(tmp_dir, "sheet.png")
    meta = os.path.join(tmp_dir, "sheet.json")

    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "sprite_sheet",
         "--input-dir", frames_dir, "--output", output,
         "--meta", meta, "--cols", "2", "--frame-size", "64x64"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert os.path.exists(output)
    assert os.path.exists(meta)


def test_cli_preview(tmp_dir):
    assets_dir = os.path.join(tmp_dir, "assets")
    os.makedirs(assets_dir)
    Image.new("RGB", (32, 32), (255, 0, 0)).save(os.path.join(assets_dir, "test.png"))

    output = os.path.join(tmp_dir, "preview.html")
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "preview",
         "--input-dir", assets_dir, "--output", output],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert os.path.exists(output)


def test_cli_unknown_command():
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "nonexistent"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_cli.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement cli.py**

```python
# game_asset_tools/cli.py
"""CLI dispatcher for game_asset_tools commands."""

import argparse
import sys


def _parse_size(size_str: str) -> tuple[int, int]:
    """Parse a size string like '64x64' or '512' into (width, height)."""
    if "x" in size_str:
        parts = size_str.split("x")
        return int(parts[0]), int(parts[1])
    s = int(size_str)
    return s, s


def cmd_resize(args):
    from game_asset_tools.resize import resize_image, resize_batch
    size = _parse_size(args.size)
    if args.input_dir:
        resize_batch(args.input_dir, args.output_dir, size, args.mode)
    else:
        resize_image(args.input, args.output, size, args.mode)


def cmd_remove_bg(args):
    from game_asset_tools.remove_bg import remove_background, remove_background_batch
    if args.input_dir:
        remove_background_batch(args.input_dir, args.output_dir)
    else:
        remove_background(args.input, args.output)


def cmd_sprite_sheet(args):
    from game_asset_tools.sprite_sheet import assemble_sprite_sheet
    frame_size = _parse_size(args.frame_size)
    cols = int(args.cols) if args.cols else None
    assemble_sprite_sheet(args.input_dir, args.output, args.meta, frame_size, cols)


def cmd_card_composer(args):
    from game_asset_tools.card_composer import compose_card
    card_size = _parse_size(args.card_size) if args.card_size else (750, 1050)
    artwork_region = tuple(map(int, args.artwork_region.split(","))) if args.artwork_region else (50, 50, 650, 600)
    title_region = tuple(map(int, args.title_region.split(","))) if args.title_region else None
    desc_region = tuple(map(int, args.desc_region.split(","))) if args.desc_region else None

    compose_card(
        artwork_path=args.artwork,
        output_path=args.output,
        card_size=card_size,
        artwork_region=artwork_region,
        template_path=args.template,
        title=args.title or "",
        title_region=title_region,
        description=args.description or "",
        desc_region=desc_region,
        font_path=args.font,
    )


def cmd_video_to_frames(args):
    from game_asset_tools.video_to_frames import extract_frames
    count = extract_frames(
        args.input, args.output_dir,
        fps=args.fps,
        dedup=args.dedup,
        dedup_threshold=args.dedup_threshold,
    )
    print(f"Extracted {count} frames")


def cmd_tileset(args):
    from game_asset_tools.tileset import assemble_tileset
    tile_size = _parse_size(args.tile_size)
    cols = int(args.cols) if args.cols else None
    assemble_tileset(
        args.input_dir, args.output, args.meta,
        tile_size, cols,
        seamless=args.seamless,
    )


def cmd_preview(args):
    from game_asset_tools.preview import generate_preview_html
    generate_preview_html(args.input_dir, args.output, title=args.title or "Game Asset Preview")


def main():
    parser = argparse.ArgumentParser(
        prog="game_asset_tools",
        description="Python toolkit for game asset post-processing",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # resize
    p = subparsers.add_parser("resize", help="Resize/crop images")
    p.add_argument("--input", help="Input image path")
    p.add_argument("--output", help="Output image path")
    p.add_argument("--input-dir", help="Input directory for batch")
    p.add_argument("--output-dir", help="Output directory for batch")
    p.add_argument("--size", required=True, help="Target size (e.g., 64x64 or 512)")
    p.add_argument("--mode", default="contain", choices=["contain", "cover", "stretch"])
    p.set_defaults(func=cmd_resize)

    # remove_bg
    p = subparsers.add_parser("remove_bg", help="Remove image background")
    p.add_argument("--input", help="Input image path")
    p.add_argument("--output", help="Output image path")
    p.add_argument("--input-dir", help="Input directory for batch")
    p.add_argument("--output-dir", help="Output directory for batch")
    p.set_defaults(func=cmd_remove_bg)

    # sprite_sheet
    p = subparsers.add_parser("sprite_sheet", help="Assemble sprite sheet")
    p.add_argument("--input-dir", required=True, help="Directory with frame images")
    p.add_argument("--output", required=True, help="Output sprite sheet path")
    p.add_argument("--meta", required=True, help="Output metadata JSON path")
    p.add_argument("--cols", help="Number of columns")
    p.add_argument("--frame-size", required=True, help="Frame size (e.g., 128x128)")
    p.set_defaults(func=cmd_sprite_sheet)

    # card_composer
    p = subparsers.add_parser("card_composer", help="Compose a card")
    p.add_argument("--artwork", required=True, help="Artwork image path")
    p.add_argument("--output", required=True, help="Output card path")
    p.add_argument("--template", help="Card border template path")
    p.add_argument("--card-size", help="Card size (e.g., 750x1050)")
    p.add_argument("--artwork-region", help="Artwork region x,y,w,h")
    p.add_argument("--title", help="Card title text")
    p.add_argument("--title-region", help="Title region x,y,w,h")
    p.add_argument("--description", help="Card description text")
    p.add_argument("--desc-region", help="Description region x,y,w,h")
    p.add_argument("--font", help="Font file path")
    p.set_defaults(func=cmd_card_composer)

    # video_to_frames
    p = subparsers.add_parser("video_to_frames", help="Extract frames from video")
    p.add_argument("--input", required=True, help="Input video path")
    p.add_argument("--output-dir", required=True, help="Output directory for frames")
    p.add_argument("--fps", type=int, default=8, help="Target FPS")
    p.add_argument("--dedup", action="store_true", help="Remove duplicate frames")
    p.add_argument("--dedup-threshold", type=float, default=0.95, help="Dedup similarity threshold")
    p.set_defaults(func=cmd_video_to_frames)

    # tileset
    p = subparsers.add_parser("tileset", help="Assemble tileset")
    p.add_argument("--input-dir", required=True, help="Directory with tile images")
    p.add_argument("--output", required=True, help="Output tileset path")
    p.add_argument("--meta", required=True, help="Output metadata JSON path")
    p.add_argument("--tile-size", required=True, help="Tile size (e.g., 32x32)")
    p.add_argument("--cols", help="Number of columns")
    p.add_argument("--seamless", action="store_true", help="Apply seamless edge blending")
    p.set_defaults(func=cmd_tileset)

    # preview
    p = subparsers.add_parser("preview", help="Generate HTML preview")
    p.add_argument("--input-dir", required=True, help="Directory with asset images")
    p.add_argument("--output", required=True, help="Output HTML path")
    p.add_argument("--title", help="Preview page title")
    p.set_defaults(func=cmd_preview)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_cli.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/cli.py tests/test_cli.py
git commit -m "feat: add CLI dispatcher for all tool commands"
```

---

## Task 13: Download Default Font

**Files:**
- Create: `templates/fonts/NotoSansSC-Regular.ttf`
- Create: `templates/fonts/NotoSansSC-Bold.ttf`

- [ ] **Step 1: Download Noto Sans SC fonts**

```bash
curl -L -o templates/fonts/NotoSansSC-Regular.ttf \
  "https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
```

Note: If the variable font URL doesn't work, use:
```bash
pip install fonttools
python3 -c "
from fontTools.ttLib import TTFont
# If variable font, we keep it as-is since Pillow supports variable fonts
"
```

Alternatively, download from Google Fonts manually and place in `templates/fonts/`.

- [ ] **Step 2: Verify font loads in Pillow**

```bash
python3 -c "
from PIL import ImageFont
font = ImageFont.truetype('templates/fonts/NotoSansSC-Regular.ttf', 24)
print('Font loaded:', font.getname())
"
```

Expected: prints font name without error

- [ ] **Step 3: Commit**

```bash
git add templates/fonts/
git commit -m "chore: add default Noto Sans SC font for card text rendering"
```

---

## Task 14: Claude Code Skill File (`game-asset.md`)

**Files:**
- Create: `skills/game-asset.md`

- [ ] **Step 1: Create the skill file**

```markdown
---
name: game-asset
description: Generate production-ready game assets (characters, backgrounds, UI, cards, icons, sprite sheets, tilesets) for 2D and card games. Combines AI image generation with post-processing.
---

# Game Asset Design Skill

You are a game asset designer. You help users generate production-ready assets for 2D games and card games by combining AI image generation (MCP tools) with Python post-processing.

## Startup: Dependency Check

Before doing anything, check Python toolkit availability:

```bash
python3 -m game_asset_tools --help
```

If it fails, inform the user:
> Python toolkit not set up. Run `pip install -r requirements.txt` in the GameAssetDesign directory first.

Check for optional dependencies:
```bash
python3 -c "import rembg; print('rembg: OK')" 2>/dev/null || echo "rembg: NOT INSTALLED (background removal unavailable)"
python3 -c "import cv2; print('opencv: OK')" 2>/dev/null || echo "opencv: NOT INSTALLED (video frame extraction unavailable)"
```

## Startup: Project Config

Check if a project config exists:

1. Look for YAML files in `projects/` directory
2. If none exist, ask the user:
   > No project config found. Want me to create one? I'll need:
   > - Project name
   > - Game engine (unity/godot/cocos/web/custom)
   > - Art style (pixel/anime/cel_shading/watercolor/flat/realistic)
   > - Any additional style keywords?

3. If multiple configs exist, ask which project to use
4. Load the selected config with `game_asset_tools.config`

## Intent Parsing

When the user describes what they want, determine:

1. **Asset type**: character / background / ui / card / icon / sprite / tileset
2. **Complexity**: simple (single asset) → Quick Mode, complex (multi-step) → Guided Mode
3. **Description**: what the asset should look like

### Quick Mode triggers
- Single asset generation (one character, one icon, one background)
- No multi-step composition needed

### Guided Mode triggers
- Card creation (needs artwork + template + text)
- Sprite sheet (multiple frames + assembly)
- Icon set (batch + consistency)
- UI element set (multiple states)
- Tileset (multiple tiles + seamless)

## Prompt Construction

Build the MCP prompt by combining:

```
[User description in English] + [Preset keywords] + [Project keywords] + [Palette]
```

### Style Presets → Prompt Keywords

| Preset | Keywords |
|--------|----------|
| pixel | pixel art, 16-bit style, clean pixels, no anti-aliasing |
| anime | anime style, cel shading, vibrant colors, clean lines |
| cel_shading | cel shaded, flat colors, bold outlines, cartoon style |
| watercolor | watercolor painting, soft edges, muted colors |
| flat | flat design, minimal shading, solid colors, vector style |
| realistic | semi-realistic, detailed rendering, painterly style |

### Model Selection

| Condition | Use |
|-----------|-----|
| Preset matches NanoBanana enum (anime, ghibli, pixar, cyberpunk, fantasy, watercolor, sketch, oil_painting) | `mcp__grsai-nanobanana__generate_image` with `style` param |
| Need 2K/4K resolution | `mcp__grsai-nanobanana__generate_image` with `image_size` |
| Free-form style or pixel/cel_shading/flat/realistic | `mcp__gemini-image__generate_image` with `style` string |
| Uncommon aspect ratio (21:9, 5:4, etc.) | NanoBanana (11 ratios) |
| User wants to try different result | Switch to the other model |

### Aspect Ratio

Map target size to nearest supported ratio:
- Square (NxN) → 1:1
- 1920x1080, 1280x720 → 16:9
- 1080x1920 → 9:16
- 750x1050 (card) → 3:4
- Other → calculate and find nearest

## Quick Mode Flow

1. Parse intent → determine asset type
2. Read project config for that asset type
3. Construct prompt (translate to English if user spoke Chinese)
4. Select model and parameters
5. Call MCP image generation tool
6. Show result to user via Read tool
7. Ask: "满意吗？可以选择：A) 满意，继续后处理 B) 重新生成 C) 微调描述 D) AI 编辑局部 E) 换模型"
8. On approval, run post-processing pipeline:

```bash
# If transparent asset:
python3 -m game_asset_tools remove_bg --input raw.png --output nobg.png

# Resize to target:
python3 -m game_asset_tools resize --input nobg.png --output final.png --size {size} --mode contain
```

9. Show final result, output file path
10. Update manifest

## Guided Mode: Card

1. Ask for card content (character/scene description, title, description text)
2. Generate artwork using Quick Mode flow
3. On artwork approval:

```bash
python3 -m game_asset_tools remove_bg --input raw_artwork.png --output artwork_nobg.png
python3 -m game_asset_tools card_composer \
  --artwork artwork_nobg.png \
  --output output/cards/card_name.png \
  --template templates/cards/default.png \
  --card-size 750x1050 \
  --artwork-region 50,50,650,600 \
  --title "Card Title" \
  --title-region 50,660,650,60 \
  --description "Card description text" \
  --desc-region 50,740,650,200
```

4. Show result, allow iteration

## Guided Mode: Sprite Sheet

1. Ask: character description, action list, frames per action
2. Ask: generation method
   - A) Per-frame AI generation (use blend_images with maintain_character for consistency)
   - B) AI video → frame extraction (use image_to_video from hero image)
3. Generate hero/reference image first, confirm
4. For each action:
   - If video method: generate video via `mcp__grsai-sora2__image_to_video`, then:
     ```bash
     python3 -m game_asset_tools video_to_frames --input action.mp4 --output-dir frames/ --fps 8 --dedup
     ```
   - If per-frame: generate each frame using blend_images with hero image
5. Post-process all frames:
   ```bash
   python3 -m game_asset_tools remove_bg --input-dir frames/ --output-dir frames_nobg/
   python3 -m game_asset_tools sprite_sheet \
     --input-dir frames_nobg/ --output sprite_sheet.png \
     --meta sprite_data.json --frame-size 128x128 --cols 4
   ```
6. Show preview, output files

## Guided Mode: UI Multi-State

1. Ask: element type (button/toggle/checkbox/tab) and description
2. Generate base state (normal) using Quick Mode flow
3. Derive other states via AI edit:
   - hover: "Make the colors slightly brighter and add a subtle glow effect"
   - pressed: "Make the colors darker and add an inset shadow effect"
   - disabled: "Desaturate the colors and reduce opacity to look disabled"
4. Post-process each state (remove bg → resize)
5. Generate preview of all states:
   ```bash
   python3 -m game_asset_tools preview --input-dir output/ui/ --output preview.html
   ```

## Guided Mode: Tileset

1. Ask: tile description, number of tile variants
2. Generate each tile with prompt including "seamless tileable texture, repeating pattern"
3. Post-process:
   ```bash
   python3 -m game_asset_tools tileset \
     --input-dir tiles/ --output output/tilesets/tileset.png \
     --meta tileset.json --tile-size 32x32 --cols 8 --seamless
   ```
4. Show 3x3 tiled preview for seamlessness check

## Guided Mode: Icon Set

1. Ask: list of icons needed, style confirmation
2. Generate first icon, confirm style
3. For subsequent icons, use style_transfer from first icon:
   - Generate raw icon → apply `mcp__gemini-image__style_transfer` or `mcp__grsai-nanobanana__style_transfer` with first icon as reference
4. Batch post-process (remove bg → resize to all target sizes)
5. Generate batch preview:
   ```bash
   python3 -m game_asset_tools preview --input-dir output/icons/ --output preview.html
   ```

## Character Consistency

When generating multiple assets of the same character:
1. Always generate a "hero" reference image first
2. For sprite frames: prefer video-based extraction (image_to_video preserves character)
3. For pose variants: use `mcp__gemini-image__blend_images` with `maintain_character: true`
4. For video-based: use `mcp__grsai-sora2__image_to_video` with hero image

## Output Management

All outputs go to the project's configured `output.base_dir`, organized by type:
- `characters/`, `backgrounds/`, `ui/`, `cards/`, `icons/`, `sprites/`, `tilesets/`

Naming follows the project config template (e.g., `{type}_{name}_{size}_{variant}`).

After each generation, update the manifest:
- Record: file path, prompt, model, style, post-processing steps
- Manifest location: `output/manifest.json`

## Important Notes

- Always translate user's Chinese descriptions to English for MCP prompts
- Always show generated images to user for confirmation before post-processing
- For batch operations, generate HTML preview for efficient review
- Check and report missing dependencies gracefully — never crash
- Intermediate files go to `output/.tmp/`; ask user about cleanup after completion
```

- [ ] **Step 2: Verify skill file syntax**

Read the file back to ensure proper YAML frontmatter and Markdown formatting.

- [ ] **Step 3: Commit**

```bash
git add skills/game-asset.md
git commit -m "feat: add game-asset Claude Code skill file"
```

---

## Task 15: Integration Test & Full Pipeline Verification

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write integration test**

```python
# tests/test_integration.py
"""Integration tests for the full pipeline (without AI generation)."""
import os
import json
from PIL import Image

from game_asset_tools.config import load_config, get_asset_config, get_style_keywords
from game_asset_tools.naming import generate_filename, find_next_variant
from game_asset_tools.manifest import Manifest
from game_asset_tools.resize import resize_image
from game_asset_tools.sprite_sheet import assemble_sprite_sheet
from game_asset_tools.preview import generate_preview_html


def test_full_character_pipeline(tmp_dir):
    """Simulate: AI generates image → remove_bg → resize → name → manifest."""
    # Simulate AI output (we skip actual AI call)
    raw = Image.new("RGB", (1024, 1024), (200, 50, 50))
    raw_path = os.path.join(tmp_dir, "raw_mage.png")
    raw.save(raw_path)

    # Post-process: resize (skip remove_bg as it needs rembg)
    output_dir = os.path.join(tmp_dir, "output", "characters")
    os.makedirs(output_dir)
    filename = generate_filename(
        template="{type}_{name}_{size}_{variant}",
        asset_type="character",
        name="fire_mage",
        size="512",
        variant="v1",
    )
    output_path = os.path.join(output_dir, filename)
    resize_image(raw_path, output_path, (512, 512), mode="contain")

    assert os.path.exists(output_path)
    img = Image.open(output_path)
    assert img.size == (512, 512)

    # Update manifest
    manifest = Manifest(os.path.join(tmp_dir, "output"), "test_game")
    manifest.add_entry(
        file=f"characters/{filename}",
        asset_type="character",
        prompt="A fire mage with red robes",
        model="gemini",
        style="anime",
        post_processing=["resize:512x512"],
    )
    manifest.save()

    with open(os.path.join(tmp_dir, "output", "manifest.json")) as f:
        data = json.load(f)
    assert len(data["assets"]) == 1


def test_full_sprite_pipeline(tmp_dir):
    """Simulate: multiple frames → sprite sheet + metadata."""
    frames_dir = os.path.join(tmp_dir, "frames")
    os.makedirs(frames_dir)
    for i in range(6):
        img = Image.new("RGBA", (128, 128), (i * 40, 100, 50, 255))
        img.save(os.path.join(frames_dir, f"frame_{i:03d}.png"))

    output_dir = os.path.join(tmp_dir, "output", "sprites")
    os.makedirs(output_dir)
    sheet_path = os.path.join(output_dir, "sprite_warrior_walk_128x128.png")
    meta_path = os.path.join(output_dir, "sprite_warrior_walk_128x128.json")

    assemble_sprite_sheet(frames_dir, sheet_path, meta_path, (128, 128), cols=3)

    sheet = Image.open(sheet_path)
    assert sheet.size == (384, 256)  # 3 cols x 2 rows
    with open(meta_path) as f:
        meta = json.load(f)
    assert len(meta["frames"]) == 6


def test_config_and_style_integration():
    """Test loading the example config and generating style keywords."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config = load_config(os.path.join(project_root, "projects", "example_project.yaml"))
    assert config["project"]["name"] == "Example RPG"

    keywords = get_style_keywords(config)
    assert "anime style" in keywords
    assert "fantasy theme" in keywords

    char_config = get_asset_config(config, "character")
    assert char_config["transparent"] is True
    assert 512 in char_config["sizes"]


def test_batch_preview_pipeline(tmp_dir):
    """Simulate: generate multiple icons → preview HTML."""
    icons_dir = os.path.join(tmp_dir, "icons")
    os.makedirs(icons_dir)
    for i in range(5):
        img = Image.new("RGBA", (64, 64), (i * 50, 100, 200, 255))
        img.save(os.path.join(icons_dir, f"icon_item_{i}_64_v1.png"))

    preview_path = os.path.join(tmp_dir, "preview.html")
    generate_preview_html(icons_dir, preview_path, title="Icon Set Preview")

    assert os.path.exists(preview_path)
    with open(preview_path) as f:
        html = f.read()
    assert "icon_item_0_64_v1.png" in html
    assert "Icon Set Preview" in html
```

- [ ] **Step 2: Run integration tests**

```bash
python3 -m pytest tests/test_integration.py -v
```

Expected: All PASS

- [ ] **Step 3: Run full test suite**

```bash
python3 -m pytest tests/ -v --tb=short
```

Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests for full asset pipelines"
```

---

## Task 16: Final Cleanup & Documentation

- [ ] **Step 1: Add .gitignore**

```
# Python
__pycache__/
*.pyc
*.egg-info/
dist/
build/

# Output
output/.tmp/

# OS
.DS_Store
```

- [ ] **Step 2: Verify all output directories have .gitkeep**

```bash
for dir in output/characters output/backgrounds output/ui output/cards output/icons output/sprites output/tilesets; do
  touch "$dir/.gitkeep"
done
touch templates/cards/.gitkeep
touch templates/ui/.gitkeep
touch templates/fonts/custom/.gitkeep
```

- [ ] **Step 3: Final commit**

```bash
git add .gitignore output/ templates/
git commit -m "chore: add gitignore and gitkeep files for directory structure"
```

- [ ] **Step 4: Run full test suite one final time**

```bash
python3 -m pytest tests/ -v
```

Expected: All PASS
