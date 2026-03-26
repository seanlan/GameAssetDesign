import os
from PIL import Image
from game_asset_tools.trim import trim_transparent, get_content_bbox


def test_get_content_bbox_centered_square(tmp_dir):
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    for x in range(25, 75):
        for y in range(25, 75):
            img.putpixel((x, y), (255, 0, 0, 255))
    path = os.path.join(tmp_dir, "test.png")
    img.save(path)
    bbox = get_content_bbox(path)
    assert bbox == (25, 25, 75, 75)


def test_get_content_bbox_fully_transparent(tmp_dir):
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    path = os.path.join(tmp_dir, "empty.png")
    img.save(path)
    bbox = get_content_bbox(path)
    assert bbox is None


def test_trim_transparent_basic(tmp_dir):
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
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    for x in range(0, 50):
        for y in range(0, 50):
            img.putpixel((x, y), (255, 0, 0, 255))
    in_path = os.path.join(tmp_dir, "input.png")
    out_path = os.path.join(tmp_dir, "output.png")
    img.save(in_path)
    trim_transparent(in_path, out_path, padding=20)
    result = Image.open(out_path)
    assert result.size == (70, 70)


def test_trim_fully_transparent_returns_none(tmp_dir):
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    in_path = os.path.join(tmp_dir, "empty.png")
    out_path = os.path.join(tmp_dir, "output.png")
    img.save(in_path)
    result = trim_transparent(in_path, out_path, padding=0)
    assert result is None
    assert not os.path.exists(out_path)


def test_trim_rgb_input_converts(tmp_dir):
    img = Image.new("RGB", (100, 100), (255, 0, 0))
    in_path = os.path.join(tmp_dir, "rgb.png")
    out_path = os.path.join(tmp_dir, "output.png")
    img.save(in_path)
    trim_transparent(in_path, out_path, padding=0)
    result = Image.open(out_path)
    assert result.size == (100, 100)
