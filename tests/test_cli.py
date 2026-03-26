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
