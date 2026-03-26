import os
import pytest
from PIL import Image
from game_asset_tools.remove_bg import remove_background, remove_background_batch, is_rembg_available


def test_is_rembg_available():
    result = is_rembg_available()
    assert isinstance(result, bool)


def test_remove_background_outputs_rgba(sample_rgb_image, tmp_dir):
    if not is_rembg_available():
        pytest.skip("rembg not installed")
    output = os.path.join(tmp_dir, "no_bg.png")
    remove_background(sample_rgb_image, output)
    img = Image.open(output)
    assert img.mode == "RGBA"


def test_remove_background_file_not_found(tmp_dir):
    output = os.path.join(tmp_dir, "out.png")
    with pytest.raises(FileNotFoundError):
        remove_background("/nonexistent/image.png", output)


def test_remove_background_batch(sample_rgb_image, tmp_dir):
    if not is_rembg_available():
        pytest.skip("rembg not installed")
    in_dir = os.path.join(tmp_dir, "in")
    out_dir = os.path.join(tmp_dir, "out")
    os.makedirs(in_dir)
    img = Image.open(sample_rgb_image)
    img.save(os.path.join(in_dir, "a.png"))
    img.save(os.path.join(in_dir, "b.png"))

    remove_background_batch(in_dir, out_dir)
    assert len(os.listdir(out_dir)) == 2
    for f in os.listdir(out_dir):
        result = Image.open(os.path.join(out_dir, f))
        assert result.mode == "RGBA"
