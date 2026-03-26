# Phase 2B: Asset Manager + Version History Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the unified Asset Manager HTML page with refinement workflow, asset version history management, and asset relationship tracking in the manifest.

**Architecture:** Three new/modified modules: `version.py` (version chain management), `manager.py` (replaces preview.py, generates interactive management HTML), and `manifest.py` extension (relationship tracking). The manager page supports both terminal dialog and browser interactive modes for refinement. Skill file orchestrates refinement operations via MCP tools.

**Tech Stack:** Python 3.10+, Pillow, HTML/CSS/JS (self-contained), existing game_asset_tools modules

**Spec:** `docs/superpowers/specs/2026-03-26-game-asset-skill-design.md` → "Asset Version History", "Unified Asset Manager", "Asset Refinement", "Asset Relationship Graph" sections

---

## File Structure

```
game_asset_tools/
├── version.py           # NEW: Asset version management
├── manager.py           # NEW: Asset manager HTML generation (replaces preview.py)
├── manifest.py          # MODIFY: Add relationships support
├── cli.py               # MODIFY: Add version, manager commands

tests/
├── test_version.py      # NEW
├── test_manager.py      # NEW
├── test_manifest.py     # MODIFY: Add relationship tests

skills/
└── game-asset.md        # MODIFY: Add refinement workflow
```

---

## Task 1: Version Module (`version.py`)

**Files:**
- Create: `game_asset_tools/version.py`
- Create: `tests/test_version.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_version.py
import os
import json
from PIL import Image
from game_asset_tools.version import VersionManager


def _create_asset(tmp_dir, name="test_asset.png", color=(255, 0, 0)):
    path = os.path.join(tmp_dir, name)
    Image.new("RGBA", (64, 64), (*color, 255)).save(path)
    return path


def test_save_first_version(tmp_dir):
    asset_path = _create_asset(tmp_dir)
    vm = VersionManager(asset_path)
    vm.save_version(action="generated", prompt="A test asset", model="gemini")

    assert vm.current_version == 1
    versions_dir = vm.versions_dir
    assert os.path.exists(os.path.join(versions_dir, "v1.png"))
    assert os.path.exists(os.path.join(versions_dir, "history.json"))


def test_save_multiple_versions(tmp_dir):
    asset_path = _create_asset(tmp_dir)
    vm = VersionManager(asset_path)
    vm.save_version(action="generated", prompt="A test asset")

    # Modify asset and save v2
    Image.new("RGBA", (64, 64), (0, 255, 0, 255)).save(asset_path)
    vm.save_version(action="edge_fix", note="Remove fringe")

    assert vm.current_version == 2
    assert os.path.exists(os.path.join(vm.versions_dir, "v1.png"))
    assert os.path.exists(os.path.join(vm.versions_dir, "v2.png"))


def test_list_versions(tmp_dir):
    asset_path = _create_asset(tmp_dir)
    vm = VersionManager(asset_path)
    vm.save_version(action="generated")
    Image.new("RGBA", (64, 64), (0, 255, 0, 255)).save(asset_path)
    vm.save_version(action="edge_fix", note="Fix edges")

    versions = vm.list_versions()
    assert len(versions) == 2
    assert versions[0]["version"] == 1
    assert versions[1]["version"] == 2
    assert versions[1]["action"] == "edge_fix"


def test_rollback(tmp_dir):
    asset_path = _create_asset(tmp_dir, color=(255, 0, 0))
    vm = VersionManager(asset_path)
    vm.save_version(action="generated")

    # Change to green and save v2
    Image.new("RGBA", (64, 64), (0, 255, 0, 255)).save(asset_path)
    vm.save_version(action="ai_edit", note="Change color")

    # Rollback to v1
    vm.rollback(1)

    # Current asset should be red again
    img = Image.open(asset_path)
    pixel = img.getpixel((32, 32))
    assert pixel[0] == 255  # red
    assert pixel[1] == 0
    assert vm.current_version == 1


def test_rollback_invalid_version(tmp_dir):
    import pytest
    asset_path = _create_asset(tmp_dir)
    vm = VersionManager(asset_path)
    vm.save_version(action="generated")
    with pytest.raises(ValueError):
        vm.rollback(99)


def test_compare_versions(tmp_dir):
    asset_path = _create_asset(tmp_dir, color=(255, 0, 0))
    vm = VersionManager(asset_path)
    vm.save_version(action="generated")

    Image.new("RGBA", (64, 64), (0, 0, 255, 255)).save(asset_path)
    vm.save_version(action="ai_edit")

    compare_path = os.path.join(tmp_dir, "compare.png")
    vm.compare(1, 2, compare_path)
    assert os.path.exists(compare_path)
    compare_img = Image.open(compare_path)
    # Side-by-side: width should be 2x original + gap
    assert compare_img.width > 64


def test_version_manager_loads_existing(tmp_dir):
    asset_path = _create_asset(tmp_dir)
    vm1 = VersionManager(asset_path)
    vm1.save_version(action="generated")
    Image.new("RGBA", (64, 64), (0, 255, 0, 255)).save(asset_path)
    vm1.save_version(action="edit")

    # New instance should load existing history
    vm2 = VersionManager(asset_path)
    assert vm2.current_version == 2
    assert len(vm2.list_versions()) == 2


def test_get_version_path(tmp_dir):
    asset_path = _create_asset(tmp_dir)
    vm = VersionManager(asset_path)
    vm.save_version(action="generated")
    v1_path = vm.get_version_path(1)
    assert os.path.exists(v1_path)
    assert v1_path.endswith("v1.png")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_version.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement version.py**

```python
# game_asset_tools/version.py
"""Asset version management — save, list, rollback, compare versions."""

import json
import os
import shutil
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont


class VersionManager:
    """Manages version history for a single asset file."""

    def __init__(self, asset_path: str):
        self.asset_path = os.path.abspath(asset_path)
        asset_dir = os.path.dirname(self.asset_path)
        asset_stem = os.path.splitext(os.path.basename(self.asset_path))[0]

        self.versions_dir = os.path.join(asset_dir, ".versions", asset_stem)
        self.history_path = os.path.join(self.versions_dir, "history.json")
        self.current_version = 0
        self._history: list[dict] = []

        # Load existing history if present
        if os.path.exists(self.history_path):
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._history = data.get("versions", [])
                self.current_version = data.get("current_version", 0)

    def save_version(
        self,
        action: str,
        prompt: str = "",
        model: str = "",
        note: str = "",
    ) -> int:
        """Save current asset state as a new version."""
        os.makedirs(self.versions_dir, exist_ok=True)

        self.current_version += 1
        version_path = os.path.join(self.versions_dir, f"v{self.current_version}.png")
        shutil.copy2(self.asset_path, version_path)

        entry = {
            "version": self.current_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
        }
        if prompt:
            entry["prompt"] = prompt
        if model:
            entry["model"] = model
        if note:
            entry["note"] = note

        self._history.append(entry)
        self._save_history()
        return self.current_version

    def list_versions(self) -> list[dict]:
        """Return list of all version entries."""
        return list(self._history)

    def get_version_path(self, version: int) -> str:
        """Get the file path for a specific version."""
        path = os.path.join(self.versions_dir, f"v{version}.png")
        if not os.path.exists(path):
            raise ValueError(f"Version {version} not found at {path}")
        return path

    def rollback(self, version: int) -> None:
        """Restore asset to a previous version."""
        path = os.path.join(self.versions_dir, f"v{version}.png")
        if not os.path.exists(path):
            raise ValueError(f"Version {version} not found")
        shutil.copy2(path, self.asset_path)
        self.current_version = version
        self._save_history()

    def compare(self, v1: int, v2: int, output_path: str, gap: int = 4) -> None:
        """Create a side-by-side comparison image of two versions."""
        path1 = self.get_version_path(v1)
        path2 = self.get_version_path(v2)

        img1 = Image.open(path1).convert("RGBA")
        img2 = Image.open(path2).convert("RGBA")

        # Normalize heights
        max_h = max(img1.height, img2.height)
        if img1.height != max_h:
            ratio = max_h / img1.height
            img1 = img1.resize((int(img1.width * ratio), max_h), Image.LANCZOS)
        if img2.height != max_h:
            ratio = max_h / img2.height
            img2 = img2.resize((int(img2.width * ratio), max_h), Image.LANCZOS)

        # Create comparison canvas
        label_h = 24
        total_w = img1.width + gap + img2.width
        total_h = max_h + label_h
        canvas = Image.new("RGBA", (total_w, total_h), (40, 40, 40, 255))

        canvas.paste(img1, (0, label_h), img1)
        canvas.paste(img2, (img1.width + gap, label_h), img2)

        # Draw labels
        draw = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except (OSError, IOError):
            font = ImageFont.load_default()
        draw.text((4, 4), f"v{v1}", fill=(200, 200, 200, 255), font=font)
        draw.text((img1.width + gap + 4, 4), f"v{v2}", fill=(200, 200, 200, 255), font=font)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        canvas.save(output_path, "PNG")

    def _save_history(self) -> None:
        data = {
            "asset": os.path.splitext(os.path.basename(self.asset_path))[0],
            "current_version": self.current_version,
            "versions": self._history,
        }
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_version.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/version.py tests/test_version.py
git commit -m "feat: add asset version management module"
```

---

## Task 2: Manifest Relationships Extension

**Files:**
- Modify: `game_asset_tools/manifest.py`
- Modify: `tests/test_manifest.py`

- [ ] **Step 1: Add failing tests**

Add to `tests/test_manifest.py`:

```python
def test_manifest_with_relationships(tmp_dir):
    m = Manifest(tmp_dir, "test_project")
    m.add_entry(
        file="characters/char_mage.png",
        asset_type="character",
        prompt="A mage",
        model="gemini",
        relationships={
            "derived_from": ".tmp/raw/mage_raw.png",
            "used_by": ["cards/card_mage.png"],
        },
    )
    m.save()

    with open(os.path.join(tmp_dir, "manifest.json")) as f:
        data = json.load(f)
    entry = data["assets"][0]
    assert "relationships" in entry
    assert entry["relationships"]["derived_from"] == ".tmp/raw/mage_raw.png"
    assert "cards/card_mage.png" in entry["relationships"]["used_by"]


def test_manifest_add_relationship(tmp_dir):
    m = Manifest(tmp_dir, "test_project")
    m.add_entry(file="a.png", asset_type="icon", prompt="test", model="gemini")
    m.save()

    m2 = Manifest(tmp_dir, "test_project")
    m2.add_relationship("a.png", "used_by", "card.png")
    m2.save()

    with open(os.path.join(tmp_dir, "manifest.json")) as f:
        data = json.load(f)
    entry = data["assets"][0]
    assert "relationships" in entry
    assert "card.png" in entry["relationships"]["used_by"]


def test_manifest_get_entry(tmp_dir):
    m = Manifest(tmp_dir, "test_project")
    m.add_entry(file="a.png", asset_type="icon", prompt="test", model="gemini")
    m.add_entry(file="b.png", asset_type="character", prompt="test2", model="gemini")
    m.save()

    entry = m.get_entry("a.png")
    assert entry is not None
    assert entry["type"] == "icon"

    missing = m.get_entry("nonexistent.png")
    assert missing is None
```

- [ ] **Step 2: Run new tests to verify they fail**

```bash
python3 -m pytest tests/test_manifest.py -v
```

Expected: New tests FAIL

- [ ] **Step 3: Add relationship support to manifest.py**

Add `relationships` parameter to `add_entry()`:

```python
    def add_entry(
        self,
        # ... existing params ...
        relationships: dict | None = None,
    ) -> None:
        # ... existing code ...
        if relationships:
            entry["relationships"] = relationships

        self.entries.append(entry)
```

Add `get_entry()` and `add_relationship()` methods:

```python
    def get_entry(self, file: str) -> dict | None:
        """Find an entry by file path."""
        for entry in self.entries:
            if entry.get("file") == file:
                return entry
        return None

    def add_relationship(self, file: str, rel_type: str, target: str) -> None:
        """Add a relationship to an existing entry."""
        entry = self.get_entry(file)
        if entry is None:
            return
        if "relationships" not in entry:
            entry["relationships"] = {}
        if rel_type not in entry["relationships"]:
            entry["relationships"][rel_type] = []
        if isinstance(entry["relationships"][rel_type], str):
            entry["relationships"][rel_type] = [entry["relationships"][rel_type]]
        if target not in entry["relationships"][rel_type]:
            entry["relationships"][rel_type].append(target)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_manifest.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/manifest.py tests/test_manifest.py
git commit -m "feat: add relationship tracking to manifest"
```

---

## Task 3: Asset Manager Module (`manager.py`)

**Files:**
- Create: `game_asset_tools/manager.py`
- Create: `tests/test_manager.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_manager.py
import os
import json
from PIL import Image
from game_asset_tools.manager import generate_manager_html


def _setup_output(tmp_dir):
    """Create a mock output directory with assets and manifest."""
    out_dir = os.path.join(tmp_dir, "output")
    icons_dir = os.path.join(out_dir, "icons")
    chars_dir = os.path.join(out_dir, "characters")
    os.makedirs(icons_dir)
    os.makedirs(chars_dir)

    # Create test assets
    for i in range(3):
        Image.new("RGBA", (64, 64), (i * 80, 100, 200, 255)).save(
            os.path.join(icons_dir, f"icon_item_{i}.png")
        )
    Image.new("RGBA", (128, 128), (200, 50, 50, 255)).save(
        os.path.join(chars_dir, "char_hero.png")
    )

    # Create manifest
    manifest = {
        "project": "test_game",
        "assets": [
            {"file": "icons/icon_item_0.png", "type": "icon", "prompt": "A potion icon",
             "model": "gemini", "style": "anime", "generated_at": "2026-03-26T14:00:00Z"},
            {"file": "icons/icon_item_1.png", "type": "icon", "prompt": "A sword icon",
             "model": "gemini", "style": "anime", "generated_at": "2026-03-26T14:01:00Z"},
            {"file": "icons/icon_item_2.png", "type": "icon", "prompt": "A shield icon",
             "model": "gemini", "style": "anime", "generated_at": "2026-03-26T14:02:00Z"},
            {"file": "characters/char_hero.png", "type": "character", "prompt": "A hero",
             "model": "gemini", "style": "anime", "generated_at": "2026-03-26T14:03:00Z",
             "relationships": {"used_by": ["cards/card_hero.png"]}},
        ],
    }
    manifest_path = os.path.join(out_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f)

    return out_dir, manifest_path


def test_generate_manager_html(tmp_dir):
    out_dir, manifest_path = _setup_output(tmp_dir)
    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, manifest_path, html_path)
    assert os.path.exists(html_path)

    with open(html_path) as f:
        html = f.read()
    assert "Asset Manager" in html
    assert "icon_item_0" in html
    assert "char_hero" in html


def test_manager_has_filter_controls(tmp_dir):
    out_dir, manifest_path = _setup_output(tmp_dir)
    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, manifest_path, html_path)

    with open(html_path) as f:
        html = f.read()
    assert "filter" in html.lower() or "filterType" in html


def test_manager_has_refinement_controls(tmp_dir):
    out_dir, manifest_path = _setup_output(tmp_dir)
    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, manifest_path, html_path)

    with open(html_path) as f:
        html = f.read()
    assert "edge_fix" in html
    assert "ai_edit" in html
    assert "ai_inpaint" in html
    assert "style_unify" in html


def test_manager_has_hidden_data_element(tmp_dir):
    out_dir, manifest_path = _setup_output(tmp_dir)
    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, manifest_path, html_path)

    with open(html_path) as f:
        html = f.read()
    assert "manager-tasks-data" in html


def test_manager_embeds_images_base64(tmp_dir):
    out_dir, manifest_path = _setup_output(tmp_dir)
    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, manifest_path, html_path)

    with open(html_path) as f:
        html = f.read()
    assert "data:image/png;base64," in html


def test_manager_shows_manifest_details(tmp_dir):
    out_dir, manifest_path = _setup_output(tmp_dir)
    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, manifest_path, html_path)

    with open(html_path) as f:
        html = f.read()
    assert "A potion icon" in html or "potion" in html.lower()
    assert "gemini" in html


def test_manager_no_manifest(tmp_dir):
    """Should work even without a manifest file."""
    out_dir = os.path.join(tmp_dir, "output")
    icons_dir = os.path.join(out_dir, "icons")
    os.makedirs(icons_dir)
    Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(
        os.path.join(icons_dir, "test.png")
    )

    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, None, html_path)
    assert os.path.exists(html_path)
    with open(html_path) as f:
        html = f.read()
    assert "test.png" in html
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_manager.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement manager.py**

```python
# game_asset_tools/manager.py
"""Unified Asset Manager HTML generation.

Replaces preview.py. Generates a self-contained interactive HTML page for:
- Browsing all project assets with filtering and sorting
- Selecting assets for refinement operations
- Viewing manifest provenance details
- Submitting refinement tasks (readable by skill via Chrome tools)
"""

import base64
import json
import os
from PIL import Image


ASSET_SUBDIRS = {
    "characters": "character",
    "icons": "icon",
    "ui": "ui",
    "cards": "card",
    "backgrounds": "background",
    "sprites": "sprite",
    "tilesets": "tileset",
}


def _scan_assets(output_dir: str) -> list[dict]:
    """Scan output directory for all asset files."""
    assets = []
    for subdir, asset_type in ASSET_SUBDIRS.items():
        dir_path = os.path.join(output_dir, subdir)
        if not os.path.isdir(dir_path):
            continue
        for root, dirs, files in os.walk(dir_path):
            # Skip .versions directories
            dirs[:] = [d for d in dirs if d != ".versions"]
            for fname in sorted(files):
                if fname.lower().endswith((".png", ".jpg", ".jpeg")) and not fname.startswith("."):
                    fpath = os.path.join(root, fname)
                    rel_path = os.path.relpath(fpath, output_dir)
                    is_shared = "shared" in root
                    try:
                        img = Image.open(fpath)
                        w, h = img.size
                    except Exception:
                        w, h = 0, 0
                    assets.append({
                        "file": rel_path,
                        "filename": fname,
                        "type": asset_type,
                        "path": fpath,
                        "width": w,
                        "height": h,
                        "size_bytes": os.path.getsize(fpath),
                        "is_shared": is_shared,
                    })
    return assets


def _merge_manifest(assets: list[dict], manifest_path: str | None) -> list[dict]:
    """Merge manifest metadata into scanned assets."""
    if not manifest_path or not os.path.exists(manifest_path):
        return assets

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    manifest_map = {}
    for entry in manifest.get("assets", []):
        manifest_map[entry.get("file", "")] = entry

    for asset in assets:
        meta = manifest_map.get(asset["file"], {})
        asset["prompt"] = meta.get("prompt", "")
        asset["model"] = meta.get("model", "")
        asset["style"] = meta.get("style", "")
        asset["generated_at"] = meta.get("generated_at", "")
        asset["post_processing"] = meta.get("post_processing", [])
        asset["relationships"] = meta.get("relationships", {})

    return assets


def _asset_to_b64(path: str) -> str:
    """Read an image file and return base64-encoded data URI."""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    ext = path.rsplit(".", 1)[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")
    return f"data:{mime};base64,{data}"


def generate_manager_html(
    output_dir: str,
    manifest_path: str | None,
    html_path: str,
    project_name: str = "",
) -> None:
    """Generate the unified asset manager HTML page."""
    assets = _scan_assets(output_dir)
    assets = _merge_manifest(assets, manifest_path)

    if not project_name and manifest_path and os.path.exists(manifest_path):
        with open(manifest_path) as f:
            project_name = json.load(f).get("project", "Game Assets")

    if not project_name:
        project_name = "Game Assets"

    # Build asset cards HTML
    cards_html = ""
    assets_json = []
    for idx, asset in enumerate(assets):
        b64 = _asset_to_b64(asset["path"])
        size_str = f"{asset['size_bytes'] / 1024:.1f}KB" if asset["size_bytes"] > 1024 else f"{asset['size_bytes']}B"
        shared_badge = ' <span class="badge shared">shared</span>' if asset.get("is_shared") else ""

        # Build detail info
        details = []
        if asset.get("prompt"):
            details.append(f"Prompt: {asset['prompt']}")
        if asset.get("model"):
            details.append(f"Model: {asset['model']}")
        if asset.get("style"):
            details.append(f"Style: {asset['style']}")
        if asset.get("generated_at"):
            details.append(f"Time: {asset['generated_at'][:19]}")
        if asset.get("post_processing"):
            details.append(f"Post: {', '.join(asset['post_processing'])}")
        rels = asset.get("relationships", {})
        if rels.get("derived_from"):
            details.append(f"From: {rels['derived_from']}")
        if rels.get("used_by"):
            details.append(f"Used by: {', '.join(rels['used_by'])}")
        details_html = "<br>".join(details) if details else "No metadata"

        cards_html += f"""
    <div class="card" data-idx="{idx}" data-type="{asset['type']}" data-name="{asset['filename']}" data-file="{asset['file']}" onclick="toggleCard(this)">
      <div class="card-check">&#9744;</div>
      <img src="{b64}" alt="{asset['filename']}" loading="lazy">
      <div class="info">
        <div class="fname">#{idx+1} {asset['filename']}{shared_badge}</div>
        <div class="meta">{asset['type']} &middot; {asset['width']}x{asset['height']} &middot; {size_str}</div>
      </div>
      <div class="details">{details_html}</div>
    </div>"""

        assets_json.append({
            "idx": idx,
            "file": asset["file"],
            "filename": asset["filename"],
            "type": asset["type"],
        })

    # Count by type
    type_counts = {}
    for a in assets:
        t = a["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    filter_buttons = "".join(
        f'<button class="fbtn" onclick="filterType(\'{t}\')">{t} ({c})</button>'
        for t, c in sorted(type_counts.items())
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Asset Manager: {project_name}</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, 'Segoe UI', sans-serif; background: #0f0f1a; color: #e0e0e0; }}
.header {{ background: #1a1a2e; padding: 16px 24px; border-bottom: 1px solid #2a2a4a; }}
.header h1 {{ color: #e94560; font-size: 20px; }}
.toolbar {{ background: #16213e; padding: 10px 24px; border-bottom: 1px solid #1a1a3e; display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }}
.fbtn {{ background: #0f3460; color: #ccc; border: 1px solid #1a4a80; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; }}
.fbtn:hover, .fbtn.active {{ background: #e94560; color: #fff; border-color: #e94560; }}
.search {{ background: #0a0a1a; color: #eee; border: 1px solid #333; padding: 4px 10px; border-radius: 4px; font-size: 12px; width: 180px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; padding: 16px 24px; }}
.card {{ background: #16213e; border-radius: 8px; overflow: hidden; border: 2px solid transparent; cursor: pointer; transition: border-color 0.15s; position: relative; }}
.card:hover {{ border-color: #3a5a8a; }}
.card.selected {{ border-color: #e94560; }}
.card.selected .card-check {{ color: #e94560; }}
.card-check {{ position: absolute; top: 6px; right: 6px; font-size: 18px; color: #555; }}
.card img {{ width: 100%; height: 140px; object-fit: contain; background: repeating-conic-gradient(#222 0% 25%, #2a2a2a 0% 50%) 50%/12px 12px; }}
.info {{ padding: 6px 10px; }}
.fname {{ font-size: 11px; font-weight: 600; word-break: break-all; }}
.meta {{ font-size: 10px; color: #888; margin-top: 2px; }}
.badge {{ font-size: 9px; padding: 1px 5px; border-radius: 3px; }}
.badge.shared {{ background: #6a3dad; color: #fff; }}
.details {{ display: none; padding: 6px 10px; font-size: 10px; color: #999; border-top: 1px solid #1a1a3e; line-height: 1.6; }}
.card.expanded .details {{ display: block; }}
.actions {{ background: #1a1a2e; padding: 12px 24px; border-top: 1px solid #2a2a4a; display: none; }}
.actions.visible {{ display: block; }}
.actions h3 {{ font-size: 14px; color: #e94560; margin-bottom: 8px; }}
.abtn {{ background: #0f3460; color: #ccc; border: 1px solid #1a4a80; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-size: 12px; margin-right: 6px; }}
.abtn:hover {{ background: #e94560; color: #fff; }}
.note-input {{ background: #0a0a1a; color: #eee; border: 1px solid #333; padding: 6px 10px; border-radius: 4px; font-size: 12px; width: 100%; margin: 8px 0; }}
.submit-btn {{ background: #e94560; color: #fff; border: none; padding: 8px 20px; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: 600; }}
.submit-btn:hover {{ background: #c73650; }}
#manager-tasks-data {{ display: none; }}
</style>
</head>
<body>
<div class="header"><h1>Asset Manager: {project_name}</h1></div>
<div class="toolbar">
  <button class="fbtn active" onclick="filterType('all')">all ({len(assets)})</button>
  {filter_buttons}
  <input class="search" type="text" placeholder="Search..." oninput="searchAssets(this.value)">
  <button class="fbtn" onclick="selectAll()">Select All</button>
  <button class="fbtn" onclick="deselectAll()">Deselect</button>
</div>
<div class="grid" id="grid">{cards_html}
</div>
<div class="actions" id="actions">
  <h3>Selected: <span id="sel-count">0</span> assets</h3>
  <div>
    <button class="abtn" onclick="setRefineType('edge_fix')">edge_fix</button>
    <button class="abtn" onclick="setRefineType('ai_edit')">ai_edit</button>
    <button class="abtn" onclick="setRefineType('ai_inpaint')">ai_inpaint</button>
    <button class="abtn" onclick="setRefineType('style_unify')">style_unify</button>
    <button class="abtn" onclick="setRefineType('delete')" style="border-color:#c33">delete</button>
    <button class="abtn" onclick="setRefineType('reclassify')">reclassify</button>
  </div>
  <input class="note-input" id="note" type="text" placeholder="Describe what to change...">
  <button class="submit-btn" onclick="submitTasks()">Submit</button>
</div>
<pre id="manager-tasks-data"></pre>
<script>
const assets = {json.dumps(assets_json)};
let selectedIdxs = new Set();
let currentRefineType = '';

function toggleCard(el) {{
  const idx = parseInt(el.dataset.idx);
  if (el.classList.contains('expanded') && !el.classList.contains('selected')) {{
    el.classList.remove('expanded');
    return;
  }}
  el.classList.toggle('selected');
  el.querySelector('.card-check').innerHTML = el.classList.contains('selected') ? '&#9745;' : '&#9744;';
  if (el.classList.contains('selected')) selectedIdxs.add(idx); else selectedIdxs.delete(idx);
  updateActions();
  // Toggle detail on double concept - expand on second click
  if (!el.classList.contains('selected')) el.classList.toggle('expanded');
}}

function updateActions() {{
  const panel = document.getElementById('actions');
  document.getElementById('sel-count').textContent = selectedIdxs.size;
  panel.classList.toggle('visible', selectedIdxs.size > 0);
}}

function filterType(type) {{
  document.querySelectorAll('.fbtn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  document.querySelectorAll('.card').forEach(c => {{
    c.style.display = (type === 'all' || c.dataset.type === type) ? '' : 'none';
  }});
}}

function searchAssets(q) {{
  q = q.toLowerCase();
  document.querySelectorAll('.card').forEach(c => {{
    c.style.display = c.dataset.name.toLowerCase().includes(q) ? '' : 'none';
  }});
}}

function selectAll() {{
  document.querySelectorAll('.card').forEach(c => {{
    if (c.style.display !== 'none') {{
      c.classList.add('selected');
      c.querySelector('.card-check').innerHTML = '&#9745;';
      selectedIdxs.add(parseInt(c.dataset.idx));
    }}
  }});
  updateActions();
}}

function deselectAll() {{
  document.querySelectorAll('.card').forEach(c => {{
    c.classList.remove('selected');
    c.querySelector('.card-check').innerHTML = '&#9744;';
  }});
  selectedIdxs.clear();
  updateActions();
}}

function setRefineType(t) {{ currentRefineType = t; }}

function submitTasks() {{
  const note = document.getElementById('note').value;
  const tasks = [];
  selectedIdxs.forEach(idx => {{
    const a = assets[idx];
    tasks.push({{ asset_id: idx+1, file: a.file, name: a.filename, type: currentRefineType, note: note }});
  }});
  const data = JSON.stringify({{ tasks: tasks }}, null, 2);
  document.getElementById('manager-tasks-data').textContent = data;
  alert('Tasks submitted (' + tasks.length + '). Skill can now read the data.');
}}
</script>
</body>
</html>"""

    os.makedirs(os.path.dirname(html_path) or ".", exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_manager.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/manager.py tests/test_manager.py
git commit -m "feat: add unified asset manager HTML generation"
```

---

## Task 4: CLI Integration — version + manager commands

**Files:**
- Modify: `game_asset_tools/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add failing CLI tests**

Add to `tests/test_cli.py`:

```python
def test_cli_version_save(tmp_dir):
    asset_path = os.path.join(tmp_dir, "test.png")
    Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(asset_path)
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "version", "save",
         "--asset", asset_path, "--action", "generated"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "v1" in result.stdout


def test_cli_version_list(tmp_dir):
    asset_path = os.path.join(tmp_dir, "test.png")
    Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(asset_path)
    subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "version", "save",
         "--asset", asset_path, "--action", "generated"],
        capture_output=True, text=True,
    )
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "version", "list",
         "--asset", asset_path],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "v1" in result.stdout


def test_cli_manager(tmp_dir):
    out_dir = os.path.join(tmp_dir, "output")
    icons_dir = os.path.join(out_dir, "icons")
    os.makedirs(icons_dir)
    Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(os.path.join(icons_dir, "test.png"))
    html_path = os.path.join(tmp_dir, "manager.html")
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "manager",
         "--output-dir", out_dir, "--output", html_path],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert os.path.exists(html_path)
```

- [ ] **Step 2: Run new tests to verify they fail**

```bash
python3 -m pytest tests/test_cli.py::test_cli_version_save tests/test_cli.py::test_cli_version_list tests/test_cli.py::test_cli_manager -v
```

Expected: FAIL

- [ ] **Step 3: Add CLI commands**

Add to `cli.py`:

```python
def _cmd_version(args):
    from game_asset_tools.version import VersionManager
    vm = VersionManager(args.asset)

    if args.version_action == "save":
        v = vm.save_version(action=args.action, note=args.note or "")
        print(f"Saved v{v}")
    elif args.version_action == "list":
        versions = vm.list_versions()
        for v in versions:
            note = f" - {v.get('note', '')}" if v.get('note') else ""
            print(f"  v{v['version']}: {v['action']}{note} ({v.get('timestamp', '')[:19]})")
    elif args.version_action == "rollback":
        vm.rollback(args.to)
        print(f"Rolled back to v{args.to}")
    elif args.version_action == "compare":
        vm.compare(args.v1, args.v2, args.output)
        print(f"Comparison: {args.output}")


def _cmd_manager(args):
    from game_asset_tools.manager import generate_manager_html
    manifest = args.manifest if args.manifest and os.path.exists(args.manifest) else None
    generate_manager_html(args.output_dir, manifest, args.output)
    print(f"Manager: {args.output}")
```

Add to `_build_parser()`:

```python
    # --- version ---
    p_ver = subparsers.add_parser("version", help="Manage asset versions")
    ver_sub = p_ver.add_subparsers(dest="version_action")
    vs = ver_sub.add_parser("save")
    vs.add_argument("--asset", required=True)
    vs.add_argument("--action", required=True)
    vs.add_argument("--note", default="")
    vl = ver_sub.add_parser("list")
    vl.add_argument("--asset", required=True)
    vr = ver_sub.add_parser("rollback")
    vr.add_argument("--asset", required=True)
    vr.add_argument("--to", type=int, required=True)
    vc = ver_sub.add_parser("compare")
    vc.add_argument("--asset", required=True)
    vc.add_argument("--v1", type=int, required=True)
    vc.add_argument("--v2", type=int, required=True)
    vc.add_argument("--output", required=True)

    # --- manager ---
    p_mgr = subparsers.add_parser("manager", help="Generate asset manager HTML")
    p_mgr.add_argument("--output-dir", dest="output_dir", required=True)
    p_mgr.add_argument("--manifest", default=None)
    p_mgr.add_argument("--output", required=True)
```

Add `import os` at top if not present, and add to `_COMMAND_HANDLERS`:

```python
    "version": _cmd_version,
    "manager": _cmd_manager,
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_cli.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add game_asset_tools/cli.py tests/test_cli.py
git commit -m "feat: add version and manager CLI commands"
```

---

## Task 5: Skill File Update — Refinement + Manager workflow

**Files:**
- Modify: `skills/game-asset.md`

- [ ] **Step 1: Add refinement and manager sections**

Add after the Extract Mode section in `skills/game-asset.md`:

```markdown
## Asset Manager

After any generation or extraction, regenerate the asset manager page:

```bash
python3 -m game_asset_tools manager --output-dir output/ --manifest output/manifest.json --output output/asset_manager.html
```

Open it for the user:
```bash
open output/asset_manager.html
```

The manager page shows all assets with filtering, sorting, and selection. Users can select assets and submit refinement requests.

### Reading User Selections (Browser Mode)

When using Chrome tools, read submitted tasks:
```javascript
document.getElementById('manager-tasks-data').textContent
```

Parse the JSON to get refinement tasks, then execute each one.

## Refinement Workflow

When user requests refinement (via terminal or manager page):

### edge_fix — Re-process background removal
```bash
python3 -m game_asset_tools remove_bg --input original.png --output fixed.png
python3 -m game_asset_tools trim --input fixed.png --output trimmed.png --padding 1
```
Then save version:
```bash
python3 -m game_asset_tools version save --asset path/to/asset.png --action "edge_fix" --note "user description"
```

### ai_edit — AI-powered content modification
Use MCP edit_image with the user's note as prompt:
- `mcp__gemini-image__edit_image` with prompt = user's note
Then save version.

### ai_inpaint — Fill missing parts
Use MCP edit_image with completion prompt:
- prompt: "Complete the missing [part described by user]"
Then save version.

### style_unify — Match project style
Use MCP style_transfer with project reference image.
Then save version.

### After each refinement:
1. Show result via Read tool
2. Ask user to confirm
3. If satisfied: save version, update manifest
4. If not: retry with different approach
5. Regenerate asset_manager.html

## Version Management

Users can request version operations:
- "显示 fire_mage 的版本历史" → `python3 -m game_asset_tools version list --asset path`
- "回滚到 v1" → `python3 -m game_asset_tools version rollback --asset path --to 1`
- "对比 v1 和 v3" → `python3 -m game_asset_tools version compare --asset path --v1 1 --v2 3 --output compare.png`
```

- [ ] **Step 2: Commit**

```bash
git add skills/game-asset.md
git commit -m "feat: add refinement workflow and version management to skill"
```

---

## Task 6: Integration Test

**Files:**
- Modify: `tests/test_integration.py`

- [ ] **Step 1: Add version + manager integration tests**

```python
def test_version_workflow(tmp_dir):
    """Full version workflow: create → edit → rollback."""
    from game_asset_tools.version import VersionManager

    asset_path = os.path.join(tmp_dir, "char_mage.png")
    Image.new("RGBA", (64, 64), (255, 0, 0, 255)).save(asset_path)

    vm = VersionManager(asset_path)
    vm.save_version(action="generated", prompt="A mage character")
    assert vm.current_version == 1

    # Simulate edit
    Image.new("RGBA", (64, 64), (0, 255, 0, 255)).save(asset_path)
    vm.save_version(action="ai_edit", note="Changed color to green")
    assert vm.current_version == 2

    # Rollback
    vm.rollback(1)
    img = Image.open(asset_path)
    assert img.getpixel((32, 32))[0] == 255  # red restored

    # Compare
    compare_path = os.path.join(tmp_dir, "compare.png")
    vm2 = VersionManager(asset_path)
    vm2.compare(1, 2, compare_path)
    assert os.path.exists(compare_path)


def test_manager_with_manifest(tmp_dir):
    """Generate manager page from assets + manifest."""
    from game_asset_tools.manager import generate_manager_html
    from game_asset_tools.manifest import Manifest

    out_dir = os.path.join(tmp_dir, "output")
    icons_dir = os.path.join(out_dir, "icons")
    os.makedirs(icons_dir)

    for i in range(3):
        Image.new("RGBA", (64, 64), (i * 80, 100, 200, 255)).save(
            os.path.join(icons_dir, f"icon_{i}.png")
        )

    m = Manifest(out_dir, "test_game")
    for i in range(3):
        m.add_entry(
            file=f"icons/icon_{i}.png", asset_type="icon",
            prompt=f"Icon {i}", model="gemini", style="anime",
        )
    m.save()

    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, os.path.join(out_dir, "manifest.json"), html_path)
    assert os.path.exists(html_path)

    with open(html_path) as f:
        html = f.read()
    assert "icon_0" in html
    assert "Asset Manager" in html
    assert "edge_fix" in html
```

- [ ] **Step 2: Run full test suite**

```bash
python3 -m pytest tests/ -v --tb=short
```

Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add version and manager integration tests"
```
