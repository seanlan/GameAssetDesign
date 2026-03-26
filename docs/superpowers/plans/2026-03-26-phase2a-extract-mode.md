# Phase 2A: Extract Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Extract Mode to the game-asset skill — analyze a design image, identify elements by layer, generate annotated preview, and batch-extract individual game-ready assets.

**Architecture:** Three new Python modules (`trim.py`, `annotate.py`, `extract.py`) plus CLI commands and skill file updates. Claude's multimodal vision handles element detection; Python handles deterministic image operations (crop, trim, remove-bg). The `extract` module orchestrates the pipeline, calling `remove_bg`, `trim`, and `resize` internally.

**Tech Stack:** Python 3.10+, Pillow, rembg, numpy, existing game_asset_tools modules

**Spec:** `docs/superpowers/specs/2026-03-26-game-asset-skill-design.md` → "Extract Mode" section

---

## File Structure

```
game_asset_tools/
├── trim.py              # NEW: Transparent area trimming
├── annotate.py          # NEW: Annotated preview generation
├── extract.py           # NEW: Batch element extraction
├── cli.py               # MODIFY: Add trim, annotate, extract commands
├── manifest.py          # MODIFY: Add relationships support

tests/
├── test_trim.py         # NEW
├── test_annotate.py     # NEW
├── test_extract.py      # NEW

skills/
└── game-asset.md        # MODIFY: Add Extract Mode section
```

---

## Task 1: Trim Module (`trim.py`)

**Files:**
- Create: `game_asset_tools/trim.py`
- Create: `tests/test_trim.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_trim.py
import os
from PIL import Image
from game_asset_tools.trim import trim_transparent, get_content_bbox


def test_get_content_bbox_centered_square(tmp_dir):
    """A centered opaque square on transparent background."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    for x in range(25, 75):
        for y in range(25, 75):
            img.putpixel((x, y), (255, 0, 0, 255))
    path = os.path.join(tmp_dir, "test.png")
    img.save(path)
    bbox = get_content_bbox(path)
    assert bbox == (25, 25, 75, 75)


def test_get_content_bbox_fully_transparent(tmp_dir):
    """A fully transparent image should return None."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    path = os.path.join(tmp_dir, "empty.png")
    img.save(path)
    bbox = get_content_bbox(path)
    assert bbox is None


def test_trim_transparent_basic(tmp_dir):
    """Trim should crop to content bounds."""
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    for x in range(50, 150):
        for y in range(60, 140):
            img.putpixel((x, y), (255, 0, 0, 255))
    in_path = os.path.join(tmp_dir, "input.png")
    out_path = os.path.join(tmp_dir, "output.png")
    img.save(in_path)

    trim_transparent(in_path, out_path, padding=0)
    result = Image.open(out_path)
    assert result.size == (100, 80)


def test_trim_transparent_with_padding(tmp_dir):
    """Trim with padding should keep extra margin."""
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    for x in range(50, 150):
        for y in range(50, 150):
            img.putpixel((x, y), (255, 0, 0, 255))
    in_path = os.path.join(tmp_dir, "input.png")
    out_path = os.path.join(tmp_dir, "output.png")
    img.save(in_path)

    trim_transparent(in_path, out_path, padding=5)
    result = Image.open(out_path)
    assert result.size == (110, 110)


def test_trim_transparent_padding_clamp(tmp_dir):
    """Padding should not extend beyond original image bounds."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    for x in range(0, 50):
        for y in range(0, 50):
            img.putpixel((x, y), (255, 0, 0, 255))
    in_path = os.path.join(tmp_dir, "input.png")
    out_path = os.path.join(tmp_dir, "output.png")
    img.save(in_path)

    trim_transparent(in_path, out_path, padding=20)
    result = Image.open(out_path)
    # Content at (0,0)-(50,50), padding 20 → clamp to (0,0)-(70,70)
    assert result.size == (70, 70)


def test_trim_fully_transparent_returns_none(tmp_dir):
    """Trimming a fully transparent image should not create output."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    in_path = os.path.join(tmp_dir, "empty.png")
    out_path = os.path.join(tmp_dir, "output.png")
    img.save(in_path)

    result = trim_transparent(in_path, out_path, padding=0)
    assert result is None
    assert not os.path.exists(out_path)


def test_trim_rgb_input_converts(tmp_dir):
    """RGB input (no alpha) should be returned as-is since there's nothing to trim."""
    img = Image.new("RGB", (100, 100), (255, 0, 0))
    in_path = os.path.join(tmp_dir, "rgb.png")
    out_path = os.path.join(tmp_dir, "output.png")
    img.save(in_path)

    trim_transparent(in_path, out_path, padding=0)
    result = Image.open(out_path)
    assert result.size == (100, 100)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_trim.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'game_asset_tools.trim'`

- [ ] **Step 3: Implement trim.py**

```python
# game_asset_tools/trim.py
"""Transparent area trimming for game assets."""

import os
from PIL import Image


def get_content_bbox(image_path: str) -> tuple[int, int, int, int] | None:
    """Find the bounding box of non-transparent content in an image.

    Returns (left, top, right, bottom) or None if fully transparent.
    """
    img = Image.open(image_path).convert("RGBA")
    # getbbox() returns the bounding box of non-zero regions in the alpha channel
    alpha = img.split()[3]
    bbox = alpha.getbbox()
    return bbox


def trim_transparent(
    input_path: str,
    output_path: str,
    padding: int = 0,
) -> str | None:
    """Trim transparent edges from an image.

    Args:
        input_path: path to input image
        output_path: path for trimmed output
        padding: extra pixels to keep around content

    Returns:
        output_path if successful, None if image is fully transparent
    """
    img = Image.open(input_path)

    # If no alpha channel, nothing to trim
    if img.mode != "RGBA":
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        img.save(output_path, "PNG")
        return output_path

    alpha = img.split()[3]
    bbox = alpha.getbbox()

    if bbox is None:
        return None

    left, top, right, bottom = bbox

    # Apply padding, clamped to image bounds
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(img.width, right + padding)
    bottom = min(img.height, bottom + padding)

    trimmed = img.crop((left, top, right, bottom))
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    trimmed.save(output_path, "PNG")
    return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_trim.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/trim.py tests/test_trim.py
git commit -m "feat: add transparent area trim module"
```

---

## Task 2: Annotate Module (`annotate.py`)

**Files:**
- Create: `game_asset_tools/annotate.py`
- Create: `tests/test_annotate.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_annotate.py
import os
import json
from PIL import Image
from game_asset_tools.annotate import annotate_image, TYPE_COLORS


def _make_elements(layers=None, shared=None):
    """Helper to build an elements dict."""
    return {
        "source": "test.png",
        "source_size": [400, 300],
        "layers": layers or {},
        "shared_assets": shared or [],
    }


def test_annotate_basic(tmp_dir):
    """Draw boxes on an image for detected elements."""
    # Create source image
    src = Image.new("RGB", (400, 300), (200, 200, 200))
    src_path = os.path.join(tmp_dir, "source.png")
    src.save(src_path)

    elements = _make_elements(
        layers={
            "top": [
                {"name": "btn_attack", "type": "ui", "bbox": [50, 200, 200, 250]},
            ],
            "middle": [
                {"name": "hero", "type": "character", "bbox": [100, 50, 300, 280]},
            ],
        }
    )
    elements_path = os.path.join(tmp_dir, "elements.json")
    with open(elements_path, "w") as f:
        json.dump(elements, f)

    out_path = os.path.join(tmp_dir, "annotated.png")
    annotate_image(src_path, elements_path, out_path)

    assert os.path.exists(out_path)
    result = Image.open(out_path)
    assert result.size == (400, 300)


def test_annotate_with_shared_assets(tmp_dir):
    """Shared assets should be drawn with dashed style indicator."""
    src = Image.new("RGB", (400, 300), (200, 200, 200))
    src_path = os.path.join(tmp_dir, "source.png")
    src.save(src_path)

    elements = _make_elements(
        layers={
            "top": [
                {"name": "icon_fire", "type": "icon", "bbox": [10, 10, 74, 74], "uses_shared": ["frame"]},
                {"name": "icon_ice", "type": "icon", "bbox": [80, 10, 144, 74], "uses_shared": ["frame"]},
            ],
        },
        shared=[
            {"name": "frame", "type": "ui", "bbox": [10, 10, 74, 74], "reuse_count": 2},
        ],
    )
    elements_path = os.path.join(tmp_dir, "elements.json")
    with open(elements_path, "w") as f:
        json.dump(elements, f)

    out_path = os.path.join(tmp_dir, "annotated.png")
    annotate_image(src_path, elements_path, out_path)
    assert os.path.exists(out_path)


def test_annotate_empty_elements(tmp_dir):
    """No elements should still produce an output (copy of source)."""
    src = Image.new("RGB", (200, 200), (100, 100, 100))
    src_path = os.path.join(tmp_dir, "source.png")
    src.save(src_path)

    elements = _make_elements()
    elements_path = os.path.join(tmp_dir, "elements.json")
    with open(elements_path, "w") as f:
        json.dump(elements, f)

    out_path = os.path.join(tmp_dir, "annotated.png")
    annotate_image(src_path, elements_path, out_path)
    assert os.path.exists(out_path)


def test_type_colors_defined():
    """All expected types should have colors defined."""
    for t in ["character", "icon", "ui", "background", "shared"]:
        assert t in TYPE_COLORS


def test_annotate_from_dict(tmp_dir):
    """annotate_image should also accept elements as a dict directly."""
    src = Image.new("RGB", (200, 200), (150, 150, 150))
    src_path = os.path.join(tmp_dir, "source.png")
    src.save(src_path)

    elements = _make_elements(
        layers={"middle": [{"name": "item", "type": "icon", "bbox": [10, 10, 60, 60]}]}
    )

    out_path = os.path.join(tmp_dir, "annotated.png")
    annotate_image(src_path, elements, out_path)
    assert os.path.exists(out_path)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_annotate.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement annotate.py**

```python
# game_asset_tools/annotate.py
"""Annotated preview generation for element detection results."""

import json
import os
from PIL import Image, ImageDraw, ImageFont


TYPE_COLORS = {
    "character": (220, 50, 50),      # red
    "icon": (240, 200, 40),          # yellow
    "ui": (50, 120, 220),            # blue
    "background": (50, 180, 80),     # green
    "shared": (160, 80, 220),        # purple
    "sprite": (220, 130, 50),        # orange
    "tileset": (100, 200, 200),      # teal
    "card": (200, 100, 150),         # pink
}


def _load_elements(elements_input) -> dict:
    """Load elements from a file path or dict."""
    if isinstance(elements_input, dict):
        return elements_input
    with open(elements_input, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_font(size: int):
    """Try to load a readable font, fall back to default."""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except (OSError, IOError):
        pass
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except (OSError, IOError):
        pass
    return ImageFont.load_default()


def annotate_image(
    source_path: str,
    elements_input,
    output_path: str,
) -> None:
    """Draw annotated bounding boxes on a source image.

    Args:
        source_path: path to the source design image
        elements_input: path to elements.json or a dict
        output_path: path for the annotated output image
    """
    elements = _load_elements(elements_input)
    img = Image.open(source_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _get_font(14)
    font_small = _get_font(11)

    counter = 1

    # Draw regular elements by layer (bottom first, top last)
    for layer_name in ["bottom", "middle", "top"]:
        layer_elements = elements.get("layers", {}).get(layer_name, [])
        for elem in layer_elements:
            name = elem.get("name", "unknown")
            elem_type = elem.get("type", "unknown")
            bbox = elem.get("bbox", [0, 0, 0, 0])
            color = TYPE_COLORS.get(elem_type, (200, 200, 200))

            left, top, right, bottom = bbox

            # Draw semi-transparent fill
            fill_color = (*color, 40)
            draw.rectangle([left, top, right, bottom], fill=fill_color)

            # Draw border
            border_color = (*color, 200)
            for i in range(2):
                draw.rectangle(
                    [left - i, top - i, right + i, bottom + i],
                    outline=border_color,
                )

            # Draw label
            label = f"#{counter} {elem_type}: {name}"
            label_y = max(0, top - 18)
            # Label background
            lbbox = font.getbbox(label)
            lw = lbbox[2] - lbbox[0]
            draw.rectangle(
                [left, label_y, left + lw + 8, label_y + 16],
                fill=(*color, 180),
            )
            draw.text((left + 4, label_y + 1), label, fill=(255, 255, 255, 255), font=font)

            counter += 1

    # Draw shared assets
    shared = elements.get("shared_assets", [])
    for asset in shared:
        name = asset.get("name", "unknown")
        bbox = asset.get("bbox", [0, 0, 0, 0])
        reuse = asset.get("reuse_count", 0)
        color = TYPE_COLORS["shared"]

        left, top, right, bottom = bbox

        # Dashed border effect: draw segments
        dash_len = 6
        gap_len = 4
        border_color = (*color, 220)
        for edge in [
            ((left, top), (right, top)),       # top
            ((right, top), (right, bottom)),   # right
            ((right, bottom), (left, bottom)), # bottom
            ((left, bottom), (left, top)),     # left
        ]:
            (x1, y1), (x2, y2) = edge
            length = max(abs(x2 - x1), abs(y2 - y1))
            if length == 0:
                continue
            dx = (x2 - x1) / length
            dy = (y2 - y1) / length
            pos = 0
            while pos < length:
                seg_end = min(pos + dash_len, length)
                draw.line(
                    [x1 + dx * pos, y1 + dy * pos, x1 + dx * seg_end, y1 + dy * seg_end],
                    fill=border_color,
                    width=2,
                )
                pos = seg_end + gap_len

        # Shared label
        label = f"shared: {name} x{reuse}"
        label_y = min(img.height - 16, bottom + 2)
        lbbox = font_small.getbbox(label)
        lw = lbbox[2] - lbbox[0]
        draw.rectangle(
            [left, label_y, left + lw + 8, label_y + 14],
            fill=(*color, 180),
        )
        draw.text((left + 4, label_y), label, fill=(255, 255, 255, 255), font=font_small)

    # Composite overlay onto original
    result = Image.alpha_composite(img, overlay)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    result.save(output_path, "PNG")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_annotate.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/annotate.py tests/test_annotate.py
git commit -m "feat: add annotated preview generation for extract mode"
```

---

## Task 3: Extract Module (`extract.py`)

**Files:**
- Create: `game_asset_tools/extract.py`
- Create: `tests/test_extract.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_extract.py
import os
import json
from PIL import Image
from game_asset_tools.extract import (
    crop_element,
    extract_elements,
    validate_elements,
    load_elements,
)


def _make_test_image(tmp_dir, width=400, height=300):
    """Create a test image with distinct colored regions."""
    img = Image.new("RGBA", (width, height), (200, 200, 200, 255))
    # Red square at (50,50)-(150,150) - "character"
    for x in range(50, 150):
        for y in range(50, 150):
            img.putpixel((x, y), (255, 0, 0, 255))
    # Blue square at (200,50)-(260,110) - "icon"
    for x in range(200, 260):
        for y in range(50, 110):
            img.putpixel((x, y), (0, 0, 255, 255))
    path = os.path.join(tmp_dir, "design.png")
    img.save(path)
    return path


def _make_elements_file(tmp_dir, elements_dict):
    path = os.path.join(tmp_dir, "elements.json")
    with open(path, "w") as f:
        json.dump(elements_dict, f)
    return path


def test_crop_element_basic(tmp_dir):
    src_path = _make_test_image(tmp_dir)
    out_path = os.path.join(tmp_dir, "cropped.png")
    crop_element(src_path, out_path, bbox=[50, 50, 150, 150], padding=0)
    result = Image.open(out_path)
    assert result.size == (100, 100)


def test_crop_element_with_padding(tmp_dir):
    src_path = _make_test_image(tmp_dir)
    out_path = os.path.join(tmp_dir, "cropped.png")
    crop_element(src_path, out_path, bbox=[50, 50, 150, 150], padding=10)
    result = Image.open(out_path)
    assert result.size == (120, 120)


def test_crop_element_padding_clamp(tmp_dir):
    src_path = _make_test_image(tmp_dir)
    out_path = os.path.join(tmp_dir, "cropped.png")
    crop_element(src_path, out_path, bbox=[0, 0, 50, 50], padding=100)
    result = Image.open(out_path)
    # Should clamp to image bounds (400x300)
    assert result.size[0] <= 400
    assert result.size[1] <= 300


def test_validate_elements_valid(tmp_dir):
    elements = {
        "source": "test.png",
        "source_size": [400, 300],
        "layers": {
            "middle": [{"name": "hero", "type": "character", "bbox": [0, 0, 100, 100]}]
        },
        "shared_assets": [],
    }
    errors = validate_elements(elements, image_size=(400, 300))
    assert len(errors) == 0


def test_validate_elements_bbox_out_of_bounds(tmp_dir):
    elements = {
        "source": "test.png",
        "source_size": [400, 300],
        "layers": {
            "middle": [{"name": "hero", "type": "character", "bbox": [0, 0, 500, 400]}]
        },
        "shared_assets": [],
    }
    errors = validate_elements(elements, image_size=(400, 300))
    assert len(errors) > 0


def test_validate_elements_missing_name(tmp_dir):
    elements = {
        "source": "test.png",
        "source_size": [400, 300],
        "layers": {
            "middle": [{"type": "character", "bbox": [0, 0, 100, 100]}]
        },
        "shared_assets": [],
    }
    errors = validate_elements(elements, image_size=(400, 300))
    assert len(errors) > 0


def test_load_elements_from_file(tmp_dir):
    elements_dict = {
        "source": "test.png",
        "source_size": [400, 300],
        "layers": {},
        "shared_assets": [],
    }
    path = _make_elements_file(tmp_dir, elements_dict)
    loaded = load_elements(path)
    assert loaded["source"] == "test.png"


def test_extract_elements_basic(tmp_dir):
    """Full extraction pipeline: crop elements from a design image."""
    src_path = _make_test_image(tmp_dir)
    out_dir = os.path.join(tmp_dir, "output")
    os.makedirs(out_dir)

    elements = {
        "source": src_path,
        "source_size": [400, 300],
        "layers": {
            "middle": [
                {
                    "name": "hero",
                    "type": "character",
                    "bbox": [50, 50, 150, 150],
                    "needs_remove_bg": False,
                    "needs_trim": False,
                }
            ],
            "top": [
                {
                    "name": "icon_fire",
                    "type": "icon",
                    "bbox": [200, 50, 260, 110],
                    "needs_remove_bg": False,
                    "needs_trim": False,
                }
            ],
        },
        "shared_assets": [],
    }

    results = extract_elements(src_path, elements, out_dir)
    assert len(results) == 2
    assert all(os.path.exists(r["output_path"]) for r in results)


def test_extract_with_trim(tmp_dir):
    """Extraction with trim should produce smaller output."""
    # Create image with small content on large transparent canvas
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    for x in range(80, 120):
        for y in range(80, 120):
            img.putpixel((x, y), (255, 0, 0, 255))
    src_path = os.path.join(tmp_dir, "design.png")
    img.save(src_path)

    out_dir = os.path.join(tmp_dir, "output")
    os.makedirs(out_dir)

    elements = {
        "source": src_path,
        "source_size": [200, 200],
        "layers": {
            "middle": [
                {
                    "name": "item",
                    "type": "icon",
                    "bbox": [60, 60, 140, 140],
                    "needs_remove_bg": False,
                    "needs_trim": True,
                    "trim_padding": 2,
                }
            ],
        },
        "shared_assets": [],
    }

    results = extract_elements(src_path, elements, out_dir)
    assert len(results) == 1
    result_img = Image.open(results[0]["output_path"])
    # Should be trimmed close to the 40x40 content + 2px padding = 44x44
    assert result_img.size[0] < 80
    assert result_img.size[1] < 80


def test_extract_shared_assets(tmp_dir):
    """Shared assets should be extracted only once to shared/ subdirectory."""
    src_path = _make_test_image(tmp_dir)
    out_dir = os.path.join(tmp_dir, "output")
    os.makedirs(out_dir)

    elements = {
        "source": src_path,
        "source_size": [400, 300],
        "layers": {
            "top": [
                {"name": "icon_fire", "type": "icon", "bbox": [200, 50, 260, 110],
                 "uses_shared": ["frame"], "needs_remove_bg": False},
                {"name": "icon_ice", "type": "icon", "bbox": [200, 50, 260, 110],
                 "uses_shared": ["frame"], "needs_remove_bg": False},
            ],
        },
        "shared_assets": [
            {"name": "frame", "type": "ui", "bbox": [200, 50, 260, 110],
             "reuse_count": 2},
        ],
    }

    results = extract_elements(src_path, elements, out_dir)
    # 2 icons + 1 shared frame = 3
    shared_results = [r for r in results if r.get("is_shared")]
    assert len(shared_results) == 1
    assert "shared" in shared_results[0]["output_path"]


def test_extract_bottom_layer_flagged(tmp_dir):
    """Bottom layer with needs_inpaint should be flagged, not processed."""
    src_path = _make_test_image(tmp_dir)
    out_dir = os.path.join(tmp_dir, "output")
    os.makedirs(out_dir)

    elements = {
        "source": src_path,
        "source_size": [400, 300],
        "layers": {
            "bottom": [
                {
                    "name": "bg",
                    "type": "background",
                    "bbox": [0, 0, 400, 300],
                    "needs_inpaint": True,
                    "inpaint_prompt": "Remove characters",
                }
            ],
        },
        "shared_assets": [],
    }

    results = extract_elements(src_path, elements, out_dir)
    bg_results = [r for r in results if r["type"] == "background"]
    assert len(bg_results) == 1
    assert bg_results[0].get("needs_inpaint") is True
    # If needs_inpaint, just crop for now (skill handles inpaint via MCP)
    assert os.path.exists(bg_results[0]["output_path"])
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_extract.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement extract.py**

```python
# game_asset_tools/extract.py
"""Batch element extraction from design images."""

import json
import os
from PIL import Image

from game_asset_tools.trim import trim_transparent
from game_asset_tools.remove_bg import remove_background, is_rembg_available
from game_asset_tools.naming import TYPE_ABBREVIATIONS


def load_elements(path: str) -> dict:
    """Load elements definition from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_elements(elements: dict, image_size: tuple[int, int]) -> list[str]:
    """Validate elements definition. Returns list of error messages."""
    errors = []
    img_w, img_h = image_size

    for layer_name in ["bottom", "middle", "top"]:
        for elem in elements.get("layers", {}).get(layer_name, []):
            if "name" not in elem:
                errors.append(f"Element in layer '{layer_name}' missing 'name'")
            if "bbox" not in elem:
                errors.append(f"Element '{elem.get('name', '?')}' missing 'bbox'")
            elif len(elem["bbox"]) == 4:
                left, top, right, bottom = elem["bbox"]
                if right > img_w or bottom > img_h:
                    errors.append(
                        f"Element '{elem.get('name', '?')}' bbox [{left},{top},{right},{bottom}] "
                        f"exceeds image bounds [{img_w},{img_h}]"
                    )
            if "type" not in elem:
                errors.append(f"Element '{elem.get('name', '?')}' missing 'type'")

    return errors


def crop_element(
    source_path: str,
    output_path: str,
    bbox: list[int],
    padding: int = 0,
) -> None:
    """Crop a rectangular region from source image with optional padding."""
    img = Image.open(source_path).convert("RGBA")
    left, top, right, bottom = bbox

    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(img.width, right + padding)
    bottom = min(img.height, bottom + padding)

    cropped = img.crop((left, top, right, bottom))
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    cropped.save(output_path, "PNG")


def _get_output_subdir(asset_type: str) -> str:
    """Map asset type to output subdirectory."""
    mapping = {
        "character": "characters",
        "icon": "icons",
        "ui": "ui",
        "background": "backgrounds",
        "sprite": "sprites",
        "tileset": "tilesets",
        "card": "cards",
    }
    return mapping.get(asset_type, asset_type)


def extract_elements(
    source_path: str,
    elements: dict,
    output_dir: str,
    remove_bg: bool = True,
    trim: bool = True,
    crop_padding: int = 4,
) -> list[dict]:
    """Extract all elements from a design image.

    Args:
        source_path: path to source design image
        elements: elements definition dict
        output_dir: base output directory
        remove_bg: whether to run rembg on extracted elements
        trim: whether to trim transparent edges
        crop_padding: extra pixels around bbox when cropping

    Returns:
        List of result dicts with output_path, type, name, etc.
    """
    results = []
    processed_shared = set()

    # Process shared assets first (extract only once)
    for asset in elements.get("shared_assets", []):
        name = asset["name"]
        if name in processed_shared:
            continue

        asset_type = asset.get("type", "ui")
        bbox = asset["bbox"]
        subdir = os.path.join(output_dir, _get_output_subdir(asset_type), "shared")
        out_path = os.path.join(subdir, f"{name}.png")

        crop_element(source_path, out_path, bbox, padding=crop_padding)

        # Optional remove_bg
        if remove_bg and is_rembg_available():
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            remove_background(out_path, tmp_path)
            os.replace(tmp_path, out_path)

        processed_shared.add(name)
        results.append({
            "name": name,
            "type": asset_type,
            "output_path": out_path,
            "is_shared": True,
            "reuse_count": asset.get("reuse_count", 0),
        })

    # Process layers
    for layer_name in ["bottom", "middle", "top"]:
        for elem in elements.get("layers", {}).get(layer_name, []):
            name = elem["name"]
            elem_type = elem.get("type", "unknown")
            bbox = elem["bbox"]
            needs_rembg = elem.get("needs_remove_bg", True) and remove_bg
            needs_trim = elem.get("needs_trim", True) and trim
            needs_inpaint = elem.get("needs_inpaint", False)
            trim_padding = elem.get("trim_padding", 2)

            subdir = os.path.join(output_dir, _get_output_subdir(elem_type))
            out_path = os.path.join(subdir, f"{name}.png")

            # Step 1: Crop from source
            crop_element(source_path, out_path, bbox, padding=crop_padding)

            # Step 2: Remove background (skip for backgrounds)
            if needs_rembg and elem_type != "background" and is_rembg_available():
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp_path = tmp.name
                remove_background(out_path, tmp_path)
                os.replace(tmp_path, out_path)

            # Step 3: Trim transparent edges
            if needs_trim and elem_type != "background":
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp_path = tmp.name
                result = trim_transparent(out_path, tmp_path, padding=trim_padding)
                if result:
                    os.replace(tmp_path, out_path)
                else:
                    # Fully transparent after processing — keep original crop
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

            result_entry = {
                "name": name,
                "type": elem_type,
                "layer": layer_name,
                "output_path": out_path,
                "bbox": bbox,
            }

            if needs_inpaint:
                result_entry["needs_inpaint"] = True
                result_entry["inpaint_prompt"] = elem.get("inpaint_prompt", "")

            results.append(result_entry)

    return results
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_extract.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/extract.py tests/test_extract.py
git commit -m "feat: add batch element extraction module"
```

---

## Task 4: CLI Integration

**Files:**
- Modify: `game_asset_tools/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add failing CLI tests**

Add to `tests/test_cli.py`:

```python
def test_cli_trim(tmp_dir):
    # Create RGBA image with content
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    for x in range(50, 150):
        for y in range(50, 150):
            img.putpixel((x, y), (255, 0, 0, 255))
    in_path = os.path.join(tmp_dir, "input.png")
    img.save(in_path)
    out_path = os.path.join(tmp_dir, "trimmed.png")

    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "trim",
         "--input", in_path, "--output", out_path, "--padding", "2"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert os.path.exists(out_path)
    trimmed = Image.open(out_path)
    assert trimmed.size[0] < 200


def test_cli_annotate(tmp_dir):
    # Create source image
    src_path = os.path.join(tmp_dir, "source.png")
    Image.new("RGB", (400, 300), (200, 200, 200)).save(src_path)

    # Create elements file
    elements = {
        "source": "source.png", "source_size": [400, 300],
        "layers": {"middle": [{"name": "hero", "type": "character", "bbox": [50, 50, 200, 250]}]},
        "shared_assets": [],
    }
    elements_path = os.path.join(tmp_dir, "elements.json")
    with open(elements_path, "w") as f:
        json.dump(elements, f)

    out_path = os.path.join(tmp_dir, "annotated.png")
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "annotate",
         "--input", src_path, "--elements", elements_path, "--output", out_path],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert os.path.exists(out_path)


def test_cli_extract(tmp_dir):
    # Create source image
    src_path = os.path.join(tmp_dir, "source.png")
    img = Image.new("RGBA", (400, 300), (200, 200, 200, 255))
    for x in range(100, 200):
        for y in range(100, 200):
            img.putpixel((x, y), (255, 0, 0, 255))
    img.save(src_path)

    # Create elements file
    elements = {
        "source": src_path, "source_size": [400, 300],
        "layers": {"middle": [
            {"name": "hero", "type": "character", "bbox": [100, 100, 200, 200],
             "needs_remove_bg": False, "needs_trim": False}
        ]},
        "shared_assets": [],
    }
    elements_path = os.path.join(tmp_dir, "elements.json")
    with open(elements_path, "w") as f:
        json.dump(elements, f)

    out_dir = os.path.join(tmp_dir, "output")
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "extract",
         "--input", src_path, "--elements", elements_path, "--output-dir", out_dir],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
```

- [ ] **Step 2: Run new tests to verify they fail**

```bash
python3 -m pytest tests/test_cli.py::test_cli_trim tests/test_cli.py::test_cli_annotate tests/test_cli.py::test_cli_extract -v
```

Expected: FAIL

- [ ] **Step 3: Add CLI commands to cli.py**

Add to `_build_parser()` in `cli.py`:

```python
    # --- trim ---
    p_trim = subparsers.add_parser("trim", help="Trim transparent edges from an image")
    p_trim.add_argument("--input", required=True, help="Input image path")
    p_trim.add_argument("--output", required=True, help="Output image path")
    p_trim.add_argument("--padding", type=int, default=0, help="Pixels of padding to keep")

    # --- annotate ---
    p_ann = subparsers.add_parser("annotate", help="Generate annotated preview of detected elements")
    p_ann.add_argument("--input", required=True, help="Source design image path")
    p_ann.add_argument("--elements", required=True, help="Path to elements.json")
    p_ann.add_argument("--output", required=True, help="Output annotated image path")

    # --- extract ---
    p_ext = subparsers.add_parser("extract", help="Extract elements from a design image")
    p_ext.add_argument("--input", required=True, help="Source design image path")
    p_ext.add_argument("--elements", required=True, help="Path to elements.json")
    p_ext.add_argument("--output-dir", dest="output_dir", required=True, help="Output directory")
    p_ext.add_argument("--no-remove-bg", dest="remove_bg", action="store_false", default=True, help="Skip background removal")
    p_ext.add_argument("--no-trim", dest="do_trim", action="store_false", default=True, help="Skip trim")
    p_ext.add_argument("--padding", type=int, default=4, help="Crop padding pixels")
```

Add command handlers:

```python
def _cmd_trim(args):
    from game_asset_tools.trim import trim_transparent
    result = trim_transparent(args.input, args.output, padding=args.padding)
    if result:
        print(f"Trimmed: {args.output}")
    else:
        print("Image is fully transparent, no output produced")


def _cmd_annotate(args):
    from game_asset_tools.annotate import annotate_image
    annotate_image(args.input, args.elements, args.output)
    print(f"Annotated: {args.output}")


def _cmd_extract(args):
    from game_asset_tools.extract import extract_elements, load_elements
    elements = load_elements(args.elements)
    results = extract_elements(
        source_path=args.input,
        elements=elements,
        output_dir=args.output_dir,
        remove_bg=args.remove_bg,
        trim=args.do_trim,
        crop_padding=args.padding,
    )
    print(f"Extracted {len(results)} elements")
    for r in results:
        flag = " [needs inpaint]" if r.get("needs_inpaint") else ""
        shared = " [shared]" if r.get("is_shared") else ""
        print(f"  {r['type']}: {r['name']} → {r['output_path']}{flag}{shared}")
```

Add to `_COMMAND_HANDLERS`:

```python
_COMMAND_HANDLERS = {
    # ... existing ...
    "trim": _cmd_trim,
    "annotate": _cmd_annotate,
    "extract": _cmd_extract,
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_cli.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/cli.py tests/test_cli.py
git commit -m "feat: add trim, annotate, extract CLI commands"
```

---

## Task 5: Skill File Update — Extract Mode

**Files:**
- Modify: `skills/game-asset.md`

- [ ] **Step 1: Add Extract Mode section to skill file**

Append the following to the end of `skills/game-asset.md` (before the final `## Important Notes` section):

```markdown
## Extract Mode: Design Image Splitting

Triggered when user provides a design image and asks to extract assets from it.

### Flow

1. User provides image path: "/game-asset 从这张图里提取素材"
2. Read the image with Read tool to analyze visually
3. Identify all elements with their:
   - Name, type (character/icon/ui/background/sprite/tileset)
   - Bounding box [left, top, right, bottom]
   - Layer (bottom/middle/top)
   - Whether it needs background removal
   - Whether it's a shared component (same border/frame used by multiple elements)

4. Write elements.json:
   ```json
   {
     "source": "path/to/design.png",
     "source_size": [width, height],
     "layers": {
       "bottom": [...],
       "middle": [...],
       "top": [...]
     },
     "shared_assets": [...]
   }
   ```

5. Generate annotated preview:
   ```bash
   python3 -m game_asset_tools annotate --input design.png --elements elements.json --output annotated.png
   ```

6. Show annotated preview via Read tool, ask user to confirm

7. User adjustments:
   - "删掉 3 号" → remove from elements.json
   - "2 号改名 ice_arrow" → update name
   - "1 号往右扩 20px" → adjust bbox
   - Re-run annotate after changes

8. On confirmation, extract:
   ```bash
   python3 -m game_asset_tools extract --input design.png --elements elements.json --output-dir output/
   ```

9. For background elements with needs_inpaint=true:
   - Use `mcp__gemini-image__edit_image` with the inpaint_prompt
   - Save result to output/backgrounds/

10. Show results, update manifest

### Element Detection Guidelines

When analyzing a design image, look for:
- **Characters**: human/creature figures, usually middle layer
- **Icons**: small square/circular elements, skill icons, item icons
- **UI elements**: buttons, bars, panels, frames, text labels
- **Background**: the scene behind everything
- **Shared components**: borders/frames that appear multiple times identically

Estimate bounding boxes as [left, top, right, bottom] in pixels.
Mark elements that overlap others as higher layer.
```

- [ ] **Step 2: Verify skill file syntax**

Read the file back to confirm proper formatting.

- [ ] **Step 3: Commit**

```bash
git add skills/game-asset.md
git commit -m "feat: add Extract Mode to game-asset skill"
```

---

## Task 6: Integration Test

**Files:**
- Modify: `tests/test_integration.py`

- [ ] **Step 1: Add extract pipeline integration test**

```python
def test_extract_pipeline(tmp_dir):
    """Full extract pipeline: design image → annotate → extract → verify outputs."""
    # Create a mock design image with distinct elements
    img = Image.new("RGBA", (800, 600), (180, 200, 220, 255))
    # "Character" - red figure in center
    for x in range(300, 500):
        for y in range(100, 500):
            img.putpixel((x, y), (220, 50, 50, 255))
    # "Icon" - yellow square top-left
    for x in range(20, 84):
        for y in range(20, 84):
            img.putpixel((x, y), (240, 200, 40, 255))
    # "Button" - blue bar at bottom
    for x in range(250, 550):
        for y in range(520, 570):
            img.putpixel((x, y), (50, 120, 220, 255))
    src_path = os.path.join(tmp_dir, "design.png")
    img.save(src_path)

    # Create elements definition
    elements = {
        "source": src_path,
        "source_size": [800, 600],
        "layers": {
            "bottom": [
                {"name": "scene_bg", "type": "background", "bbox": [0, 0, 800, 600],
                 "needs_remove_bg": False, "needs_trim": False}
            ],
            "middle": [
                {"name": "hero_warrior", "type": "character", "bbox": [300, 100, 500, 500],
                 "needs_remove_bg": False, "needs_trim": True, "trim_padding": 4}
            ],
            "top": [
                {"name": "skill_icon", "type": "icon", "bbox": [20, 20, 84, 84],
                 "needs_remove_bg": False, "needs_trim": True, "trim_padding": 2},
                {"name": "btn_action", "type": "ui", "bbox": [250, 520, 550, 570],
                 "needs_remove_bg": False, "needs_trim": True, "trim_padding": 2},
            ],
        },
        "shared_assets": [],
    }
    elements_path = os.path.join(tmp_dir, "elements.json")
    with open(elements_path, "w") as f:
        json.dump(elements, f)

    # Step 1: Annotate
    from game_asset_tools.annotate import annotate_image
    annotated_path = os.path.join(tmp_dir, "annotated.png")
    annotate_image(src_path, elements_path, annotated_path)
    assert os.path.exists(annotated_path)

    # Step 2: Extract
    from game_asset_tools.extract import extract_elements
    out_dir = os.path.join(tmp_dir, "output")
    results = extract_elements(src_path, elements, out_dir, remove_bg=False)
    assert len(results) == 4

    # Verify outputs exist
    types_found = {r["type"] for r in results}
    assert "background" in types_found
    assert "character" in types_found
    assert "icon" in types_found
    assert "ui" in types_found

    for r in results:
        assert os.path.exists(r["output_path"])
```

- [ ] **Step 2: Run the integration test**

```bash
python3 -m pytest tests/test_integration.py::test_extract_pipeline -v
```

Expected: PASS

- [ ] **Step 3: Run full test suite**

```bash
python3 -m pytest tests/ -v --tb=short
```

Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add extract pipeline integration test"
```
