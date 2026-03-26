import os
import pytest
from game_asset_tools.config import load_config, get_asset_config, get_style_keywords


def test_load_config_valid(tmp_dir):
    config_path = os.path.join(tmp_dir, "test.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test Game"
  engine: "unity"
style:
  preset: "anime"
  reference_image: null
  keywords: "fantasy theme"
  palette: ["#FF0000"]
assets:
  character:
    sizes: [512]
    format: "png"
    transparent: true
output:
  base_dir: "output/"
  naming: "{type}_{name}_{size}"
""")
    config = load_config(config_path)
    assert config["project"]["name"] == "Test Game"
    assert config["style"]["preset"] == "anime"


def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path.yaml")


def test_load_config_validates_required_keys(tmp_dir):
    config_path = os.path.join(tmp_dir, "bad.yaml")
    with open(config_path, "w") as f:
        f.write("foo: bar\n")
    with pytest.raises(ValueError, match="Missing required"):
        load_config(config_path)


def test_load_config_validates_preset(tmp_dir):
    config_path = os.path.join(tmp_dir, "bad.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test"
  engine: "unity"
style:
  preset: "nonexistent_style"
  keywords: ""
  palette: []
assets: {}
output:
  base_dir: "output/"
  naming: "{type}_{name}"
""")
    with pytest.raises(ValueError, match="Unknown preset"):
        load_config(config_path)


def test_get_asset_config(tmp_dir):
    config_path = os.path.join(tmp_dir, "test.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test"
  engine: "unity"
style:
  preset: "anime"
  keywords: ""
  palette: []
assets:
  character:
    sizes: [512, 1024]
    format: "png"
    transparent: true
  icon:
    sizes: [64]
    format: "png"
    transparent: true
output:
  base_dir: "output/"
  naming: "{type}_{name}"
""")
    config = load_config(config_path)
    char_config = get_asset_config(config, "character")
    assert char_config["sizes"] == [512, 1024]
    assert char_config["transparent"] is True
    icon_config = get_asset_config(config, "icon")
    assert icon_config["sizes"] == [64]


def test_get_asset_config_unknown_type(tmp_dir):
    config_path = os.path.join(tmp_dir, "test.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test"
  engine: "unity"
style:
  preset: "anime"
  keywords: ""
  palette: []
assets: {}
output:
  base_dir: "output/"
  naming: "{type}_{name}"
""")
    config = load_config(config_path)
    result = get_asset_config(config, "nonexistent")
    assert result is None


def test_get_style_keywords_with_preset(tmp_dir):
    config_path = os.path.join(tmp_dir, "test.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test"
  engine: "unity"
style:
  preset: "anime"
  keywords: "fantasy theme"
  palette: ["#FF0000", "#00FF00"]
assets: {}
output:
  base_dir: "output/"
  naming: "{type}_{name}"
""")
    config = load_config(config_path)
    keywords = get_style_keywords(config)
    assert "anime style" in keywords
    assert "fantasy theme" in keywords
    assert "#FF0000" in keywords


def test_get_style_keywords_pixel_preset(tmp_dir):
    config_path = os.path.join(tmp_dir, "test.yaml")
    with open(config_path, "w") as f:
        f.write("""
project:
  name: "Test"
  engine: "unity"
style:
  preset: "pixel"
  keywords: ""
  palette: []
assets: {}
output:
  base_dir: "output/"
  naming: "{type}_{name}"
""")
    config = load_config(config_path)
    keywords = get_style_keywords(config)
    assert "pixel art" in keywords
    assert "16-bit style" in keywords
