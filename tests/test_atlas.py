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
