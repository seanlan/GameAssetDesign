import os
from PIL import Image
from game_asset_tools.preview import generate_preview_html


def test_generate_preview_html(tmp_dir):
    assets_dir = os.path.join(tmp_dir, "assets")
    os.makedirs(assets_dir)
    for i in range(3):
        img = Image.new("RGB", (64, 64), (i * 80, 100, 100))
        img.save(os.path.join(assets_dir, f"icon_{i}.png"))
    output = os.path.join(tmp_dir, "preview.html")
    generate_preview_html(assets_dir, output)
    assert os.path.exists(output)
    with open(output) as f:
        html = f.read()
    assert "icon_0.png" in html
    assert "icon_1.png" in html
    assert "icon_2.png" in html
    assert "<img" in html
    assert "64 x 64" in html


def test_generate_preview_html_empty_dir(tmp_dir):
    assets_dir = os.path.join(tmp_dir, "empty")
    os.makedirs(assets_dir)
    output = os.path.join(tmp_dir, "preview.html")
    generate_preview_html(assets_dir, output)
    assert os.path.exists(output)
    with open(output) as f:
        html = f.read()
    assert "No assets found" in html


def test_preview_uses_base64_embedding(tmp_dir):
    assets_dir = os.path.join(tmp_dir, "assets")
    os.makedirs(assets_dir)
    Image.new("RGB", (32, 32), (255, 0, 0)).save(os.path.join(assets_dir, "test.png"))
    output = os.path.join(tmp_dir, "preview.html")
    generate_preview_html(assets_dir, output)
    with open(output) as f:
        html = f.read()
    assert "data:image/png;base64," in html
