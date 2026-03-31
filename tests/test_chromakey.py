import os
import numpy as np
from PIL import Image
from game_asset_tools.chromakey import (
    remove_chromakey,
    select_chroma_color,
    despill_green,
    despill_magenta,
)


def test_select_chroma_color_warm(tmp_dir):
    """Warm-toned image should select green chroma key."""
    img = Image.new("RGB", (100, 100), (200, 100, 50))  # warm orange
    path = os.path.join(tmp_dir, "warm.png")
    img.save(path)
    color = select_chroma_color(path)
    assert color == "green"


def test_select_chroma_color_cool(tmp_dir):
    """Cool-toned image should select magenta chroma key."""
    img = Image.new("RGB", (100, 100), (50, 100, 200))  # cool blue
    path = os.path.join(tmp_dir, "cool.png")
    img.save(path)
    color = select_chroma_color(path)
    assert color == "magenta"


def test_select_chroma_color_green_content(tmp_dir):
    """Green content should select magenta (avoid same hue)."""
    img = Image.new("RGB", (100, 100), (50, 200, 50))  # green
    path = os.path.join(tmp_dir, "green.png")
    img.save(path)
    color = select_chroma_color(path)
    assert color == "magenta"


def test_remove_chromakey_green(tmp_dir):
    """Remove green background from image."""
    # Create image: red square on green background
    img = Image.new("RGBA", (100, 100), (0, 255, 0, 255))  # green bg
    for x in range(25, 75):
        for y in range(25, 75):
            img.putpixel((x, y), (255, 0, 0, 255))  # red content
    in_path = os.path.join(tmp_dir, "green_bg.png")
    out_path = os.path.join(tmp_dir, "result.png")
    img.save(in_path)

    remove_chromakey(in_path, out_path, color="green")
    result = Image.open(out_path)
    assert result.mode == "RGBA"
    # Corner should be transparent (was green)
    assert result.getpixel((0, 0))[3] == 0
    # Center should be opaque (was red)
    assert result.getpixel((50, 50))[3] > 200


def test_remove_chromakey_magenta(tmp_dir):
    """Remove magenta background from image."""
    img = Image.new("RGBA", (100, 100), (255, 0, 255, 255))  # magenta bg
    for x in range(25, 75):
        for y in range(25, 75):
            img.putpixel((x, y), (0, 100, 200, 255))  # blue content
    in_path = os.path.join(tmp_dir, "magenta_bg.png")
    out_path = os.path.join(tmp_dir, "result.png")
    img.save(in_path)

    remove_chromakey(in_path, out_path, color="magenta")
    result = Image.open(out_path)
    assert result.getpixel((0, 0))[3] == 0
    assert result.getpixel((50, 50))[3] > 200


def test_remove_chromakey_auto(tmp_dir):
    """Auto-detect chroma color and remove."""
    # Green background with warm content
    img = Image.new("RGBA", (100, 100), (0, 255, 0, 255))
    for x in range(25, 75):
        for y in range(25, 75):
            img.putpixel((x, y), (200, 100, 50, 255))
    in_path = os.path.join(tmp_dir, "auto.png")
    out_path = os.path.join(tmp_dir, "result.png")
    img.save(in_path)

    remove_chromakey(in_path, out_path, color="auto")
    result = Image.open(out_path)
    assert result.getpixel((0, 0))[3] == 0


def test_remove_chromakey_with_despill(tmp_dir):
    """Despill should reduce green fringing on edges."""
    img = Image.new("RGBA", (100, 100), (0, 255, 0, 255))
    # Create edge pixels that are mixed green+red (simulating fringing)
    for x in range(20, 80):
        for y in range(20, 80):
            if 20 <= x < 25 or 75 <= x < 80 or 20 <= y < 25 or 75 <= y < 80:
                img.putpixel((x, y), (100, 200, 50, 255))  # green-ish edge
            else:
                img.putpixel((x, y), (200, 50, 50, 255))  # red content
    in_path = os.path.join(tmp_dir, "fringe.png")
    out_path = os.path.join(tmp_dir, "result.png")
    img.save(in_path)

    remove_chromakey(in_path, out_path, color="green", despill=True)
    result = Image.open(out_path)
    # Edge pixel should have reduced green
    edge_pixel = result.getpixel((22, 50))
    # After despill, G should not dominate
    assert edge_pixel[1] <= max(edge_pixel[0], edge_pixel[2]) + 30


def test_despill_green():
    """Green despill should reduce G channel where it dominates."""
    arr = np.array([[[100, 200, 50, 255]]], dtype=np.float32)
    result = despill_green(arr.copy())
    assert result[0, 0, 1] < 200  # G reduced


def test_despill_magenta():
    """Magenta despill should reduce R+B where they dominate over G."""
    arr = np.array([[[200, 50, 200, 255]]], dtype=np.float32)
    result = despill_magenta(arr.copy())
    # R and B should be reduced toward G
    assert result[0, 0, 0] < 200
    assert result[0, 0, 2] < 200
