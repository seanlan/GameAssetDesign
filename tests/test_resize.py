import os
from PIL import Image
from game_asset_tools.resize import resize_image, resize_batch


def test_resize_contain(sample_rgb_image, tmp_dir):
    output = os.path.join(tmp_dir, "out.png")
    resize_image(sample_rgb_image, output, size=(64, 64), mode="contain")
    img = Image.open(output)
    assert img.size == (64, 64)
    assert img.mode == "RGBA"


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
    corner = img.getpixel((0, 0))
    assert corner[3] == 0


def test_resize_batch(sample_rgb_image, tmp_dir):
    in_dir = os.path.join(tmp_dir, "in")
    out_dir = os.path.join(tmp_dir, "out")
    os.makedirs(in_dir)
    os.makedirs(out_dir)
    img = Image.open(sample_rgb_image)
    img.save(os.path.join(in_dir, "a.png"))
    img.save(os.path.join(in_dir, "b.png"))

    resize_batch(in_dir, out_dir, size=(32, 32), mode="contain")
    assert len(os.listdir(out_dir)) == 2
    for f in os.listdir(out_dir):
        result = Image.open(os.path.join(out_dir, f))
        assert result.size == (32, 32)
