import os
import pytest
from PIL import Image
from game_asset_tools.config import load_config, get_asset_config, get_style_keywords, find_config


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


def test_get_requirements(tmp_dir):
    from game_asset_tools.config import get_requirements
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
requirements:
  characters:
    - name: "fire_mage"
      sizes: [512, 1024]
    - name: "ice_archer"
  icons:
    - name: "fireball"
    - name: "ice_arrow"
    - name: "healing"
""")
    config = load_config(config_path)
    reqs = get_requirements(config)
    assert "characters" in reqs
    assert len(reqs["characters"]) == 2
    assert reqs["characters"][0]["name"] == "fire_mage"
    assert len(reqs["icons"]) == 3


def test_get_requirements_empty(tmp_dir):
    from game_asset_tools.config import get_requirements
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
    reqs = get_requirements(config)
    assert reqs == {}


def test_check_progress(tmp_dir):
    from game_asset_tools.config import get_requirements, check_progress
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
requirements:
  characters:
    - name: "fire_mage"
    - name: "ice_archer"
  icons:
    - name: "fireball"
    - name: "healing"
""")
    config = load_config(config_path)
    reqs = get_requirements(config)

    # Create some matching assets
    out_dir = os.path.join(tmp_dir, "output")
    chars_dir = os.path.join(out_dir, "characters")
    icons_dir = os.path.join(out_dir, "icons")
    os.makedirs(chars_dir)
    os.makedirs(icons_dir)
    Image.new("RGBA", (64, 64), (255, 0, 0, 255)).save(os.path.join(chars_dir, "char_fire_mage_512_v1.png"))
    Image.new("RGBA", (64, 64), (255, 0, 0, 255)).save(os.path.join(icons_dir, "icon_fireball_64_v1.png"))

    progress = check_progress(reqs, out_dir)
    assert progress["characters"]["total"] == 2
    assert progress["characters"]["done"] == 1
    assert "fire_mage" in progress["characters"]["completed"]
    assert "ice_archer" in progress["characters"]["missing"]
    assert progress["icons"]["done"] == 1
    assert "healing" in progress["icons"]["missing"]


def test_find_config_primary(tmp_dir):
    config_path = os.path.join(tmp_dir, "game-assets.yaml")
    with open(config_path, "w") as f:
        f.write("project:\n  name: Test\n")
    result = find_config(tmp_dir)
    assert result == config_path


def test_find_config_legacy(tmp_dir):
    projects_dir = os.path.join(tmp_dir, "projects")
    os.makedirs(projects_dir)
    config_path = os.path.join(projects_dir, "my_game.yaml")
    with open(config_path, "w") as f:
        f.write("project:\n  name: Test\n")
    result = find_config(tmp_dir)
    assert result == config_path


def test_find_config_none(tmp_dir):
    result = find_config(tmp_dir)
    assert result is None


def test_get_templates(tmp_dir):
    from game_asset_tools.config import get_templates
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
templates:
  - name: "skill_icon"
    type: "icon"
    prompt_template: "A {name} skill icon"
  - name: "character"
    type: "character"
    prompt_template: "A {name} character"
""")
    config = load_config(config_path)
    templates = get_templates(config)
    assert len(templates) == 2
    assert templates[0]["name"] == "skill_icon"


def test_get_templates_empty(tmp_dir):
    from game_asset_tools.config import get_templates
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
    templates = get_templates(config)
    assert templates == []


def test_find_config_primary_over_legacy(tmp_dir):
    """Primary game-assets.yaml should take priority over projects/."""
    primary = os.path.join(tmp_dir, "game-assets.yaml")
    with open(primary, "w") as f:
        f.write("project:\n  name: Primary\n")
    projects_dir = os.path.join(tmp_dir, "projects")
    os.makedirs(projects_dir)
    with open(os.path.join(projects_dir, "legacy.yaml"), "w") as f:
        f.write("project:\n  name: Legacy\n")
    result = find_config(tmp_dir)
    assert result == primary
