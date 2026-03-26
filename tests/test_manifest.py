import os
import json
from game_asset_tools.manifest import Manifest


def test_create_new_manifest(tmp_dir):
    m = Manifest(tmp_dir, "test_project")
    m.add_entry(
        file="characters/char_mage_v1.png",
        asset_type="character",
        prompt="A fire mage",
        model="gemini",
        style="anime",
        aspect_ratio="1:1",
        raw_file=".tmp/raw/mage.png",
        post_processing=["remove_bg", "resize:512x512"],
        preset="anime",
    )
    m.save()

    manifest_path = os.path.join(tmp_dir, "manifest.json")
    assert os.path.exists(manifest_path)

    with open(manifest_path) as f:
        data = json.load(f)
    assert data["project"] == "test_project"
    assert len(data["assets"]) == 1
    assert data["assets"][0]["file"] == "characters/char_mage_v1.png"


def test_append_to_existing_manifest(tmp_dir):
    m = Manifest(tmp_dir, "test_project")
    m.add_entry(file="a.png", asset_type="icon", prompt="icon1", model="gemini")
    m.save()

    m2 = Manifest(tmp_dir, "test_project")
    m2.add_entry(file="b.png", asset_type="icon", prompt="icon2", model="gemini")
    m2.save()

    with open(os.path.join(tmp_dir, "manifest.json")) as f:
        data = json.load(f)
    assert len(data["assets"]) == 2


def test_manifest_entry_has_timestamp(tmp_dir):
    m = Manifest(tmp_dir, "test_project")
    m.add_entry(file="a.png", asset_type="icon", prompt="test", model="gemini")
    m.save()

    with open(os.path.join(tmp_dir, "manifest.json")) as f:
        data = json.load(f)
    assert "generated_at" in data["assets"][0]
