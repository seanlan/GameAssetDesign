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


def test_manifest_with_relationships(tmp_dir):
    m = Manifest(tmp_dir, "test_project")
    m.add_entry(
        file="characters/char_mage.png", asset_type="character",
        prompt="A mage", model="gemini",
        relationships={"derived_from": ".tmp/raw/mage_raw.png", "used_by": ["cards/card_mage.png"]},
    )
    m.save()
    with open(os.path.join(tmp_dir, "manifest.json")) as f:
        data = json.load(f)
    entry = data["assets"][0]
    assert "relationships" in entry
    assert entry["relationships"]["derived_from"] == ".tmp/raw/mage_raw.png"


def test_manifest_add_relationship(tmp_dir):
    m = Manifest(tmp_dir, "test_project")
    m.add_entry(file="a.png", asset_type="icon", prompt="test", model="gemini")
    m.save()
    m2 = Manifest(tmp_dir, "test_project")
    m2.add_relationship("a.png", "used_by", "card.png")
    m2.save()
    with open(os.path.join(tmp_dir, "manifest.json")) as f:
        data = json.load(f)
    assert "card.png" in data["assets"][0]["relationships"]["used_by"]


def test_manifest_get_entry(tmp_dir):
    m = Manifest(tmp_dir, "test_project")
    m.add_entry(file="a.png", asset_type="icon", prompt="test", model="gemini")
    m.add_entry(file="b.png", asset_type="character", prompt="test2", model="gemini")
    m.save()
    entry = m.get_entry("a.png")
    assert entry is not None
    assert entry["type"] == "icon"
    assert m.get_entry("nonexistent.png") is None
