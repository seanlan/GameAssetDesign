# tests/test_manager.py
import os
import json
from PIL import Image
from game_asset_tools.manager import generate_manager_html


def _setup_output(tmp_dir):
    """Create a mock output directory with assets and manifest."""
    out_dir = os.path.join(tmp_dir, "output")
    icons_dir = os.path.join(out_dir, "icons")
    chars_dir = os.path.join(out_dir, "characters")
    os.makedirs(icons_dir)
    os.makedirs(chars_dir)

    # Create test assets
    for i in range(3):
        Image.new("RGBA", (64, 64), (i * 80, 100, 200, 255)).save(
            os.path.join(icons_dir, f"icon_item_{i}.png")
        )
    Image.new("RGBA", (128, 128), (200, 50, 50, 255)).save(
        os.path.join(chars_dir, "char_hero.png")
    )

    # Create manifest
    manifest = {
        "project": "test_game",
        "assets": [
            {"file": "icons/icon_item_0.png", "type": "icon", "prompt": "A potion icon",
             "model": "gemini", "style": "anime", "generated_at": "2026-03-26T14:00:00Z"},
            {"file": "icons/icon_item_1.png", "type": "icon", "prompt": "A sword icon",
             "model": "gemini", "style": "anime", "generated_at": "2026-03-26T14:01:00Z"},
            {"file": "icons/icon_item_2.png", "type": "icon", "prompt": "A shield icon",
             "model": "gemini", "style": "anime", "generated_at": "2026-03-26T14:02:00Z"},
            {"file": "characters/char_hero.png", "type": "character", "prompt": "A hero",
             "model": "gemini", "style": "anime", "generated_at": "2026-03-26T14:03:00Z",
             "relationships": {"used_by": ["cards/card_hero.png"]}},
        ],
    }
    manifest_path = os.path.join(out_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f)

    return out_dir, manifest_path


def test_generate_manager_html(tmp_dir):
    out_dir, manifest_path = _setup_output(tmp_dir)
    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, manifest_path, html_path)
    assert os.path.exists(html_path)

    with open(html_path) as f:
        html = f.read()
    assert "Asset Manager" in html
    assert "icon_item_0" in html
    assert "char_hero" in html


def test_manager_has_filter_controls(tmp_dir):
    out_dir, manifest_path = _setup_output(tmp_dir)
    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, manifest_path, html_path)

    with open(html_path) as f:
        html = f.read()
    assert "filter" in html.lower() or "filterType" in html


def test_manager_has_refinement_controls(tmp_dir):
    out_dir, manifest_path = _setup_output(tmp_dir)
    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, manifest_path, html_path)

    with open(html_path) as f:
        html = f.read()
    assert "edge_fix" in html
    assert "ai_edit" in html
    assert "ai_inpaint" in html
    assert "style_unify" in html


def test_manager_has_hidden_data_element(tmp_dir):
    out_dir, manifest_path = _setup_output(tmp_dir)
    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, manifest_path, html_path)

    with open(html_path) as f:
        html = f.read()
    assert "manager-tasks-data" in html


def test_manager_embeds_images_base64(tmp_dir):
    out_dir, manifest_path = _setup_output(tmp_dir)
    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, manifest_path, html_path)

    with open(html_path) as f:
        html = f.read()
    assert "data:image/png;base64," in html


def test_manager_shows_manifest_details(tmp_dir):
    out_dir, manifest_path = _setup_output(tmp_dir)
    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, manifest_path, html_path)

    with open(html_path) as f:
        html = f.read()
    assert "A potion icon" in html or "potion" in html.lower()
    assert "gemini" in html


def test_manager_no_manifest(tmp_dir):
    """Should work even without a manifest file."""
    out_dir = os.path.join(tmp_dir, "output")
    icons_dir = os.path.join(out_dir, "icons")
    os.makedirs(icons_dir)
    Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(
        os.path.join(icons_dir, "test.png")
    )

    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, None, html_path)
    assert os.path.exists(html_path)
    with open(html_path) as f:
        html = f.read()
    assert "test.png" in html


def test_manager_with_progress_dashboard(tmp_dir):
    out_dir = os.path.join(tmp_dir, "output")
    icons_dir = os.path.join(out_dir, "icons")
    os.makedirs(icons_dir)
    Image.new("RGBA", (64, 64), (200, 100, 100, 255)).save(os.path.join(icons_dir, "icon_fireball_64.png"))

    import yaml
    config_path = os.path.join(tmp_dir, "project.yaml")
    config = {
        "project": {"name": "Test RPG", "engine": "unity"},
        "style": {"preset": "anime", "keywords": "", "palette": []},
        "assets": {},
        "output": {"base_dir": "output/", "naming": "{type}_{name}"},
        "requirements": {
            "icons": [{"name": "fireball"}, {"name": "ice_arrow"}, {"name": "healing"}]
        },
    }
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    html_path = os.path.join(tmp_dir, "manager.html")
    generate_manager_html(out_dir, None, html_path, project_config=config_path)

    with open(html_path) as f:
        html = f.read()
    assert "1/3" in html or "33%" in html
    assert "ice_arrow" in html or "healing" in html
