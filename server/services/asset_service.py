"""Asset management service — wraps game_asset_tools for the API layer."""

import json
import os
import glob
from PIL import Image

from game_asset_tools.manifest import Manifest
from game_asset_tools.version import VersionManager
from game_asset_tools.extract import extract_elements, load_elements


ASSET_SUBDIRS = {
    "characters": "character",
    "icons": "icon",
    "ui": "ui",
    "cards": "card",
    "backgrounds": "background",
    "sprites": "sprite",
    "tilesets": "tileset",
}


class AssetService:
    """Manages project assets, manifest, and versions.

    Uses CWD as the project root — serves whichever project directory
    the server was started from.
    """

    def __init__(self, project_root: str | None = None):
        self.project_root = project_root or os.getcwd()
        self.output_dir = os.path.join(PROJECT_ROOT, "output")
        self.tmp_dir = os.path.join(self.output_dir, ".tmp")
        self.manifest_path = os.path.join(self.output_dir, "manifest.json")

    def list_assets(self) -> list[dict]:
        """Scan output directory and merge with manifest metadata."""
        assets = []

        # Load manifest
        manifest_map = {}
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path) as f:
                data = json.load(f)
                for entry in data.get("assets", []):
                    manifest_map[entry.get("file", "")] = entry

        # Scan directories
        for subdir, asset_type in ASSET_SUBDIRS.items():
            dir_path = os.path.join(self.output_dir, subdir)
            if not os.path.isdir(dir_path):
                continue
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if d != ".versions"]
                for fname in sorted(files):
                    if fname.lower().endswith((".png", ".jpg", ".jpeg")) and not fname.startswith("."):
                        fpath = os.path.join(root, fname)
                        rel_path = os.path.relpath(fpath, self.output_dir)
                        is_shared = "shared" in root

                        try:
                            img = Image.open(fpath)
                            w, h = img.size
                        except Exception:
                            w, h = 0, 0

                        meta = manifest_map.get(rel_path, {})
                        assets.append({
                            "file": rel_path,
                            "filename": fname,
                            "name": os.path.splitext(fname)[0],
                            "type": asset_type,
                            "path": fpath,
                            "width": w,
                            "height": h,
                            "size_bytes": os.path.getsize(fpath),
                            "is_shared": is_shared,
                            "prompt": meta.get("prompt", ""),
                            "model": meta.get("model", ""),
                            "style": meta.get("style", ""),
                            "generated_at": meta.get("generated_at", ""),
                            "relationships": meta.get("relationships", {}),
                            "image_url": f"/output/{rel_path}",
                        })

        return assets

    def get_asset(self, name: str) -> dict | None:
        """Find asset by name (without extension)."""
        for asset in self.list_assets():
            if asset["name"] == name or asset["filename"] == name:
                return asset
        return None

    def get_asset_path(self, name: str) -> str | None:
        """Get filesystem path for an asset."""
        asset = self.get_asset(name)
        return asset["path"] if asset else None

    def update_asset(self, name: str, updates: dict) -> dict | None:
        """Update asset metadata."""
        asset = self.get_asset(name)
        if not asset:
            return None

        # Handle rename
        if "name" in updates and updates["name"] != asset["name"]:
            new_name = updates["name"]
            old_path = asset["path"]
            ext = os.path.splitext(old_path)[1]
            new_path = os.path.join(os.path.dirname(old_path), new_name + ext)
            os.rename(old_path, new_path)
            asset["path"] = new_path
            asset["filename"] = new_name + ext
            asset["name"] = new_name

        # Handle reclassify
        if "type" in updates and updates["type"] != asset["type"]:
            new_type = updates["type"]
            type_to_dir = {v: k for k, v in ASSET_SUBDIRS.items()}
            new_subdir = type_to_dir.get(new_type, new_type)
            new_dir = os.path.join(self.output_dir, new_subdir)
            os.makedirs(new_dir, exist_ok=True)
            new_path = os.path.join(new_dir, asset["filename"])
            os.rename(asset["path"], new_path)
            asset["path"] = new_path
            asset["type"] = new_type

        return asset

    def delete_asset(self, name: str) -> bool:
        """Delete an asset file."""
        asset = self.get_asset(name)
        if not asset:
            return False
        if os.path.exists(asset["path"]):
            os.remove(asset["path"])
        return True

    def list_versions(self, name: str) -> list[dict] | None:
        """Get version history for an asset."""
        path = self.get_asset_path(name)
        if not path:
            return None
        vm = VersionManager(path)
        return vm.list_versions()

    def rollback(self, name: str, version: int) -> bool:
        """Rollback an asset to a previous version."""
        path = self.get_asset_path(name)
        if not path:
            return False
        try:
            vm = VersionManager(path)
            vm.rollback(version)
            return True
        except ValueError:
            return False

    def compare_versions(self, name: str, v1: int, v2: int) -> str | None:
        """Generate comparison image."""
        path = self.get_asset_path(name)
        if not path:
            return None
        try:
            vm = VersionManager(path)
            output = os.path.join(self.tmp_dir, f"compare_{name}_{v1}_{v2}.png")
            os.makedirs(self.tmp_dir, exist_ok=True)
            vm.compare(v1, v2, output)
            return output
        except ValueError:
            return None

    def get_project_config(self) -> dict | None:
        """Load project config from game-assets.yaml in project root."""
        from game_asset_tools.config import find_config, load_config
        path = find_config(self.project_root)
        if not path:
            return None
        return load_config(path)

    def extract_from_elements(self, elements_path: str) -> dict:
        """Run extraction pipeline."""
        elements = load_elements(elements_path)
        source = elements.get("source", "")
        results = extract_elements(
            source_path=source,
            elements=elements,
            output_dir=self.output_dir,
            remove_bg=False,
            trim=False,
            crop_padding=0,
        )
        return {"extracted": len(results), "results": [{"name": r["name"], "type": r["type"], "path": r["output_path"]} for r in results]}
