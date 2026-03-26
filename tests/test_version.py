# tests/test_version.py
import os
import json
from PIL import Image
from game_asset_tools.version import VersionManager


def _create_asset(tmp_dir, name="test_asset.png", color=(255, 0, 0)):
    path = os.path.join(tmp_dir, name)
    Image.new("RGBA", (64, 64), (*color, 255)).save(path)
    return path


def test_save_first_version(tmp_dir):
    asset_path = _create_asset(tmp_dir)
    vm = VersionManager(asset_path)
    vm.save_version(action="generated", prompt="A test asset", model="gemini")

    assert vm.current_version == 1
    versions_dir = vm.versions_dir
    assert os.path.exists(os.path.join(versions_dir, "v1.png"))
    assert os.path.exists(os.path.join(versions_dir, "history.json"))


def test_save_multiple_versions(tmp_dir):
    asset_path = _create_asset(tmp_dir)
    vm = VersionManager(asset_path)
    vm.save_version(action="generated", prompt="A test asset")

    # Modify asset and save v2
    Image.new("RGBA", (64, 64), (0, 255, 0, 255)).save(asset_path)
    vm.save_version(action="edge_fix", note="Remove fringe")

    assert vm.current_version == 2
    assert os.path.exists(os.path.join(vm.versions_dir, "v1.png"))
    assert os.path.exists(os.path.join(vm.versions_dir, "v2.png"))


def test_list_versions(tmp_dir):
    asset_path = _create_asset(tmp_dir)
    vm = VersionManager(asset_path)
    vm.save_version(action="generated")
    Image.new("RGBA", (64, 64), (0, 255, 0, 255)).save(asset_path)
    vm.save_version(action="edge_fix", note="Fix edges")

    versions = vm.list_versions()
    assert len(versions) == 2
    assert versions[0]["version"] == 1
    assert versions[1]["version"] == 2
    assert versions[1]["action"] == "edge_fix"


def test_rollback(tmp_dir):
    asset_path = _create_asset(tmp_dir, color=(255, 0, 0))
    vm = VersionManager(asset_path)
    vm.save_version(action="generated")

    # Change to green and save v2
    Image.new("RGBA", (64, 64), (0, 255, 0, 255)).save(asset_path)
    vm.save_version(action="ai_edit", note="Change color")

    # Rollback to v1
    vm.rollback(1)

    # Current asset should be red again
    img = Image.open(asset_path)
    pixel = img.getpixel((32, 32))
    assert pixel[0] == 255  # red
    assert pixel[1] == 0
    assert vm.current_version == 1


def test_rollback_invalid_version(tmp_dir):
    import pytest
    asset_path = _create_asset(tmp_dir)
    vm = VersionManager(asset_path)
    vm.save_version(action="generated")
    with pytest.raises(ValueError):
        vm.rollback(99)


def test_compare_versions(tmp_dir):
    asset_path = _create_asset(tmp_dir, color=(255, 0, 0))
    vm = VersionManager(asset_path)
    vm.save_version(action="generated")

    Image.new("RGBA", (64, 64), (0, 0, 255, 255)).save(asset_path)
    vm.save_version(action="ai_edit")

    compare_path = os.path.join(tmp_dir, "compare.png")
    vm.compare(1, 2, compare_path)
    assert os.path.exists(compare_path)
    compare_img = Image.open(compare_path)
    # Side-by-side: width should be 2x original + gap
    assert compare_img.width > 64


def test_version_manager_loads_existing(tmp_dir):
    asset_path = _create_asset(tmp_dir)
    vm1 = VersionManager(asset_path)
    vm1.save_version(action="generated")
    Image.new("RGBA", (64, 64), (0, 255, 0, 255)).save(asset_path)
    vm1.save_version(action="edit")

    # New instance should load existing history
    vm2 = VersionManager(asset_path)
    assert vm2.current_version == 2
    assert len(vm2.list_versions()) == 2


def test_get_version_path(tmp_dir):
    asset_path = _create_asset(tmp_dir)
    vm = VersionManager(asset_path)
    vm.save_version(action="generated")
    v1_path = vm.get_version_path(1)
    assert os.path.exists(v1_path)
    assert v1_path.endswith("v1.png")
