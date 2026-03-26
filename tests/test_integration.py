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
