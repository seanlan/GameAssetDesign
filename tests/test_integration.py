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
    """Simulate: AI generates image → resize → name → manifest."""
    raw = Image.new("RGB", (1024, 1024), (200, 50, 50))
    raw_path = os.path.join(tmp_dir, "raw_mage.png")
    raw.save(raw_path)

    output_dir = os.path.join(tmp_dir, "output", "characters")
    os.makedirs(output_dir)
    filename = generate_filename(
        template="{type}_{name}_{size}_{variant}",
        asset_type="character", name="fire_mage", size="512", variant="v1",
    )
    output_path = os.path.join(output_dir, filename)
    resize_image(raw_path, output_path, (512, 512), mode="contain")

    assert os.path.exists(output_path)
    img = Image.open(output_path)
    assert img.size == (512, 512)

    manifest = Manifest(os.path.join(tmp_dir, "output"), "test_game")
    manifest.add_entry(
        file=f"characters/{filename}", asset_type="character",
        prompt="A fire mage with red robes", model="gemini",
        style="anime", post_processing=["resize:512x512"],
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
    assert sheet.size == (384, 256)
    with open(meta_path) as f:
        meta = json.load(f)
    assert len(meta["frames"]) == 6


def test_config_and_style_integration(tmp_dir):
    """Test loading a config and generating style keywords."""
    config_path = os.path.join(tmp_dir, "game-assets.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test RPG"
  engine: "unity"
style:
  preset: "anime"
  keywords: "fantasy theme"
  palette: ["#FF0000"]
assets:
  character:
    sizes: [512, 1024]
    format: "png"
    transparent: true
output:
  base_dir: "output/"
  naming: "{type}_{name}"
""")
    config = load_config(config_path)
    assert config["project"]["name"] == "Test RPG"

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


def test_extract_pipeline(tmp_dir):
    """Full extract pipeline: design image → annotate → extract → verify outputs."""
    import json
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


def test_atlas_pipeline(tmp_dir):
    """Pack icons into atlas and verify metadata."""
    import json
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
        Image.new("RGBA", (64, 64), (100, 100, 100, 255)).save(os.path.join(d, "test.png"))

    export_dir = os.path.join(tmp_dir, "web_export")
    result = export_for_engine("web", input_dir, export_dir)
    assert result["total"] == 2
    assert os.path.exists(os.path.join(export_dir, "manifest.json"))
    assert os.path.isdir(os.path.join(export_dir, "images", "characters"))
