"""Test fixtures from conftest.py."""

import os
from PIL import Image


def test_tmp_dir(tmp_dir):
    """Test that tmp_dir fixture provides a writable directory."""
    assert os.path.isdir(tmp_dir)
    test_file = os.path.join(tmp_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("test")
    assert os.path.exists(test_file)


def test_sample_rgb_image(sample_rgb_image):
    """Test that sample_rgb_image fixture creates a valid RGB image."""
    assert os.path.exists(sample_rgb_image)
    img = Image.open(sample_rgb_image)
    assert img.mode == "RGB"
    assert img.size == (100, 100)


def test_sample_rgba_image(sample_rgba_image):
    """Test that sample_rgba_image fixture creates a valid RGBA image."""
    assert os.path.exists(sample_rgba_image)
    img = Image.open(sample_rgba_image)
    assert img.mode == "RGBA"
    assert img.size == (100, 100)


def test_sample_frames(sample_frames):
    """Test that sample_frames fixture creates multiple frame images."""
    frames_dir, paths = sample_frames
    assert os.path.isdir(frames_dir)
    assert len(paths) == 4
    for path in paths:
        assert os.path.exists(path)
        img = Image.open(path)
        assert img.mode == "RGBA"
        assert img.size == (64, 64)
