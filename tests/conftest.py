# tests/conftest.py
import os
import tempfile
import pytest
from PIL import Image


@pytest.fixture
def tmp_dir():
    """Provide a temporary directory that is cleaned up after test."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sample_rgb_image(tmp_dir):
    """Create a 100x100 RGB test image and return its path."""
    path = os.path.join(tmp_dir, "test_rgb.png")
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    img.save(path)
    return path


@pytest.fixture
def sample_rgba_image(tmp_dir):
    """Create a 100x100 RGBA test image with a centered opaque square on transparent bg."""
    path = os.path.join(tmp_dir, "test_rgba.png")
    img = Image.new("RGBA", (100, 100), color=(0, 0, 0, 0))
    for x in range(25, 75):
        for y in range(25, 75):
            img.putpixel((x, y), (255, 0, 0, 255))
    img.save(path)
    return path


@pytest.fixture
def sample_frames(tmp_dir):
    """Create 4 numbered frame images in a subdirectory."""
    frames_dir = os.path.join(tmp_dir, "frames")
    os.makedirs(frames_dir)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    paths = []
    for i, color in enumerate(colors):
        path = os.path.join(frames_dir, f"frame_{i:03d}.png")
        img = Image.new("RGBA", (64, 64), color=(*color, 255))
        img.save(path)
        paths.append(path)
    return frames_dir, paths
