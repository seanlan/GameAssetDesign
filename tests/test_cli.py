import os
import subprocess
import sys
from PIL import Image


def test_cli_help():
    result = subprocess.run([sys.executable, "-m", "game_asset_tools", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage" in result.stdout.lower() or "game_asset_tools" in result.stdout.lower()


def test_cli_resize(tmp_dir):
    in_path = os.path.join(tmp_dir, "in.png")
    out_path = os.path.join(tmp_dir, "out.png")
    Image.new("RGB", (100, 100), (255, 0, 0)).save(in_path)
    result = subprocess.run([sys.executable, "-m", "game_asset_tools", "resize", "--input", in_path, "--output", out_path, "--size", "64x64", "--mode", "contain"], capture_output=True, text=True)
    assert result.returncode == 0
    assert os.path.exists(out_path)
    img = Image.open(out_path)
    assert img.size == (64, 64)


def test_cli_sprite_sheet(sample_frames, tmp_dir):
    frames_dir, _ = sample_frames
    output = os.path.join(tmp_dir, "sheet.png")
    meta = os.path.join(tmp_dir, "sheet.json")
    result = subprocess.run([sys.executable, "-m", "game_asset_tools", "sprite_sheet", "--input-dir", frames_dir, "--output", output, "--meta", meta, "--cols", "2", "--frame-size", "64x64"], capture_output=True, text=True)
    assert result.returncode == 0
    assert os.path.exists(output)
    assert os.path.exists(meta)


def test_cli_preview(tmp_dir):
    assets_dir = os.path.join(tmp_dir, "assets")
    os.makedirs(assets_dir)
    Image.new("RGB", (32, 32), (255, 0, 0)).save(os.path.join(assets_dir, "test.png"))
    output = os.path.join(tmp_dir, "preview.html")
    result = subprocess.run([sys.executable, "-m", "game_asset_tools", "preview", "--input-dir", assets_dir, "--output", output], capture_output=True, text=True)
    assert result.returncode == 0
    assert os.path.exists(output)


def test_cli_unknown_command():
    result = subprocess.run([sys.executable, "-m", "game_asset_tools", "nonexistent"], capture_output=True, text=True)
    assert result.returncode != 0


def test_cli_trim(tmp_dir):
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    for x in range(50, 150):
        for y in range(50, 150):
            img.putpixel((x, y), (255, 0, 0, 255))
    in_path = os.path.join(tmp_dir, "input.png")
    img.save(in_path)
    out_path = os.path.join(tmp_dir, "trimmed.png")
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "trim",
         "--input", in_path, "--output", out_path, "--padding", "2"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert os.path.exists(out_path)
    trimmed = Image.open(out_path)
    assert trimmed.size[0] < 200


def test_cli_annotate(tmp_dir):
    import json
    src_path = os.path.join(tmp_dir, "source.png")
    Image.new("RGB", (400, 300), (200, 200, 200)).save(src_path)
    elements = {
        "source": "source.png", "source_size": [400, 300],
        "layers": {"middle": [{"name": "hero", "type": "character", "bbox": [50, 50, 200, 250]}]},
        "shared_assets": [],
    }
    elements_path = os.path.join(tmp_dir, "elements.json")
    with open(elements_path, "w") as f:
        json.dump(elements, f)
    out_path = os.path.join(tmp_dir, "annotated.png")
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "annotate",
         "--input", src_path, "--elements", elements_path, "--output", out_path],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert os.path.exists(out_path)


def test_cli_extract(tmp_dir):
    import json
    src_path = os.path.join(tmp_dir, "source.png")
    img = Image.new("RGBA", (400, 300), (200, 200, 200, 255))
    for x in range(100, 200):
        for y in range(100, 200):
            img.putpixel((x, y), (255, 0, 0, 255))
    img.save(src_path)
    elements = {
        "source": src_path, "source_size": [400, 300],
        "layers": {"middle": [
            {"name": "hero", "type": "character", "bbox": [100, 100, 200, 200],
             "needs_remove_bg": False, "needs_trim": False}
        ]},
        "shared_assets": [],
    }
    elements_path = os.path.join(tmp_dir, "elements.json")
    with open(elements_path, "w") as f:
        json.dump(elements, f)
    out_dir = os.path.join(tmp_dir, "output")
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "extract",
         "--input", src_path, "--elements", elements_path, "--output-dir", out_dir],
        capture_output=True, text=True,
    )
    assert result.returncode == 0


def test_cli_version_save(tmp_dir):
    asset_path = os.path.join(tmp_dir, "test.png")
    Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(asset_path)
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "version", "save",
         "--asset", asset_path, "--action", "generated"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "v1" in result.stdout


def test_cli_version_list(tmp_dir):
    asset_path = os.path.join(tmp_dir, "test.png")
    Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(asset_path)
    subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "version", "save",
         "--asset", asset_path, "--action", "generated"],
        capture_output=True, text=True,
    )
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "version", "list",
         "--asset", asset_path],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "v1" in result.stdout


def test_cli_manager(tmp_dir):
    out_dir = os.path.join(tmp_dir, "output")
    icons_dir = os.path.join(out_dir, "icons")
    os.makedirs(icons_dir)
    Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(os.path.join(icons_dir, "test.png"))
    html_path = os.path.join(tmp_dir, "manager.html")
    result = subprocess.run(
        [sys.executable, "-m", "game_asset_tools", "manager",
         "--output-dir", out_dir, "--output", html_path],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert os.path.exists(html_path)
