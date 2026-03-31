import os
from PIL import Image
from game_asset_tools.auto_detect import detect_elements


def test_detect_elements_basic(tmp_dir):
    """Should detect distinct colored rectangles."""
    img = Image.new("RGB", (400, 300), (200, 200, 200))
    # Draw distinct elements
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 150, 150], fill=(255, 0, 0))   # red square
    draw.rectangle([200, 50, 350, 250], fill=(0, 0, 255))  # blue rectangle
    draw.rectangle([50, 200, 120, 270], fill=(0, 255, 0))  # green square
    path = os.path.join(tmp_dir, "design.png")
    img.save(path)

    result = detect_elements(path, min_size=20)
    assert "layers" in result
    total = sum(len(v) for v in result["layers"].values())
    assert total >= 2  # Should detect at least 2 elements


def test_detect_elements_format(tmp_dir):
    """Output format should be valid elements.json."""
    img = Image.new("RGB", (200, 200), (100, 100, 100))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([30, 30, 80, 80], fill=(255, 0, 0))
    path = os.path.join(tmp_dir, "test.png")
    img.save(path)

    result = detect_elements(path)
    assert "source" in result
    assert "source_size" in result
    assert "layers" in result
    assert "shared_assets" in result
    assert result["source_size"] == [200, 200]


def test_detect_no_elements(tmp_dir):
    """Uniform image should detect 0 elements."""
    img = Image.new("RGB", (200, 200), (128, 128, 128))
    path = os.path.join(tmp_dir, "uniform.png")
    img.save(path)

    result = detect_elements(path)
    total = sum(len(v) for v in result["layers"].values())
    assert total == 0
