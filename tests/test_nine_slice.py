import os
import json
import sys
import subprocess
from PIL import Image
from game_asset_tools.nine_slice import slice_nine, generate_nine_slice_preview, NineSliceData


def test_slice_nine_basic(tmp_dir):
    """Slice a 100x100 image with 20px borders into 9 parts."""
    img = Image.new("RGBA", (100, 100), (200, 100, 50, 255))
    in_path = os.path.join(tmp_dir, "btn.png")
    img.save(in_path)

    result = slice_nine(in_path, tmp_dir, border=20)

    assert len(result.slices) == 9
    # Check corner sizes
    tl = Image.open(result.slices["top_left"])
    assert tl.size == (20, 20)
    # Check center
    center = Image.open(result.slices["center"])
    assert center.size == (60, 60)
    # Check metadata
    assert result.border == 20
    assert result.original_size == (100, 100)


def test_slice_nine_asymmetric(tmp_dir):
    """Slice with different horizontal and vertical borders."""
    img = Image.new("RGBA", (200, 100), (100, 100, 200, 255))
    in_path = os.path.join(tmp_dir, "panel.png")
    img.save(in_path)

    result = slice_nine(in_path, tmp_dir, border_x=30, border_y=15)

    tl = Image.open(result.slices["top_left"])
    assert tl.size == (30, 15)
    center = Image.open(result.slices["center"])
    assert center.size == (140, 70)


def test_slice_nine_meta_json(tmp_dir):
    """Should output a metadata JSON file."""
    img = Image.new("RGBA", (80, 80), (50, 150, 50, 255))
    in_path = os.path.join(tmp_dir, "frame.png")
    img.save(in_path)

    result = slice_nine(in_path, tmp_dir, border=10)

    meta_path = os.path.join(tmp_dir, "nine_slice.json")
    result.save_meta(meta_path)
    assert os.path.exists(meta_path)

    with open(meta_path) as f:
        data = json.load(f)
    assert data["border"]["left"] == 10
    assert data["border"]["right"] == 10
    assert data["border"]["top"] == 10
    assert data["border"]["bottom"] == 10
    assert data["original_size"] == [80, 80]
    assert "unity" in data["engine_configs"]
    assert "godot" in data["engine_configs"]


def test_generate_preview(tmp_dir):
    """Generate a preview showing the 9-slice stretched."""
    img = Image.new("RGBA", (60, 60), (100, 50, 150, 255))
    # Draw distinct corners
    for x in range(15):
        for y in range(15):
            img.putpixel((x, y), (255, 0, 0, 255))  # top-left red
            img.putpixel((59-x, y), (0, 255, 0, 255))  # top-right green
            img.putpixel((x, 59-y), (0, 0, 255, 255))  # bottom-left blue
            img.putpixel((59-x, 59-y), (255, 255, 0, 255))  # bottom-right yellow
    in_path = os.path.join(tmp_dir, "btn.png")
    img.save(in_path)

    result = slice_nine(in_path, tmp_dir, border=15)
    preview_path = os.path.join(tmp_dir, "preview.png")
    generate_nine_slice_preview(result, preview_path, target_size=(200, 100))

    preview = Image.open(preview_path)
    assert preview.size == (200, 100)
    # Corners should be preserved (not stretched)
    assert preview.getpixel((5, 5))[0] > 200  # top-left still red


def test_slice_nine_too_small_border(tmp_dir):
    """Border larger than half the image should raise error."""
    import pytest
    img = Image.new("RGBA", (40, 40), (100, 100, 100, 255))
    in_path = os.path.join(tmp_dir, "small.png")
    img.save(in_path)

    with pytest.raises(ValueError):
        slice_nine(in_path, tmp_dir, border=25)


def test_cli_nine_slice(tmp_dir):
    img = Image.new("RGBA", (80, 80), (200, 100, 50, 255))
    in_path = os.path.join(tmp_dir, "btn.png")
    img.save(in_path)
    out_dir = os.path.join(tmp_dir, "sliced")
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "nine_slice",
         "--input", in_path, "--output-dir", out_dir, "--border", "10", "--preview"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert os.path.exists(os.path.join(out_dir, "nine_slice.json"))
    assert os.path.exists(os.path.join(out_dir, "preview.png"))
