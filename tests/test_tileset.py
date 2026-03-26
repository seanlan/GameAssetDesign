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
    assert sheet.size == (96, 64)
    with open(meta) as f:
        data = json.load(f)
    assert len(data["tiles"]) == 6


def test_make_seamless(tmp_dir):
    tile_path = os.path.join(tmp_dir, "tile.png")
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 255))
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
