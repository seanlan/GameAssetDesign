# tests/test_export.py
import os
import json
from PIL import Image
from game_asset_tools.export import export_for_engine, SUPPORTED_ENGINES


def _setup_assets(tmp_dir):
    out_dir = os.path.join(tmp_dir, "output")
    for subdir in ["characters", "icons", "ui", "backgrounds"]:
        d = os.path.join(out_dir, subdir)
        os.makedirs(d)
        Image.new("RGBA", (64, 64), (100, 100, 100, 255)).save(os.path.join(d, f"test_{subdir}.png"))
    return out_dir


def test_supported_engines():
    assert "unity" in SUPPORTED_ENGINES
    assert "godot" in SUPPORTED_ENGINES
    assert "cocos" in SUPPORTED_ENGINES
    assert "web" in SUPPORTED_ENGINES


def test_export_unity(tmp_dir):
    input_dir = _setup_assets(tmp_dir)
    export_dir = os.path.join(tmp_dir, "unity_export")
    result = export_for_engine("unity", input_dir, export_dir)
    assert os.path.isdir(os.path.join(export_dir, "Assets", "Sprites", "Characters"))
    assert os.path.isdir(os.path.join(export_dir, "Assets", "Sprites", "Icons"))
    assert os.path.isdir(os.path.join(export_dir, "Assets", "UI"))
    assert os.path.isdir(os.path.join(export_dir, "Assets", "Backgrounds"))
    # Check files were copied
    chars = os.listdir(os.path.join(export_dir, "Assets", "Sprites", "Characters"))
    assert any(f.endswith(".png") for f in chars)
    assert result["total"] > 0


def test_export_godot(tmp_dir):
    input_dir = _setup_assets(tmp_dir)
    export_dir = os.path.join(tmp_dir, "godot_export")
    result = export_for_engine("godot", input_dir, export_dir)
    assert os.path.isdir(os.path.join(export_dir, "assets", "characters"))
    assert os.path.isdir(os.path.join(export_dir, "assets", "icons"))
    assert result["total"] > 0


def test_export_web(tmp_dir):
    input_dir = _setup_assets(tmp_dir)
    export_dir = os.path.join(tmp_dir, "web_export")
    result = export_for_engine("web", input_dir, export_dir)
    assert os.path.isdir(os.path.join(export_dir, "images", "characters"))
    # Should have a manifest
    assert os.path.exists(os.path.join(export_dir, "manifest.json"))
    assert result["total"] > 0


def test_export_cocos(tmp_dir):
    input_dir = _setup_assets(tmp_dir)
    export_dir = os.path.join(tmp_dir, "cocos_export")
    result = export_for_engine("cocos", input_dir, export_dir)
    assert os.path.isdir(os.path.join(export_dir, "assets"))
    assert result["total"] > 0


def test_export_invalid_engine(tmp_dir):
    import pytest
    input_dir = _setup_assets(tmp_dir)
    with pytest.raises(ValueError, match="Unsupported engine"):
        export_for_engine("unreal", input_dir, os.path.join(tmp_dir, "out"))


def test_export_empty_input(tmp_dir):
    input_dir = os.path.join(tmp_dir, "empty_output")
    os.makedirs(input_dir)
    export_dir = os.path.join(tmp_dir, "export")
    result = export_for_engine("web", input_dir, export_dir)
    assert result["total"] == 0
