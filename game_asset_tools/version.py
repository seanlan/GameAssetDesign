# game_asset_tools/version.py
"""Asset version management — save, list, rollback, compare versions."""

import json
import os
import shutil
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont


class VersionManager:
    """Manages version history for a single asset file."""

    def __init__(self, asset_path: str):
        self.asset_path = os.path.abspath(asset_path)
        asset_dir = os.path.dirname(self.asset_path)
        asset_stem = os.path.splitext(os.path.basename(self.asset_path))[0]

        self.versions_dir = os.path.join(asset_dir, ".versions", asset_stem)
        self.history_path = os.path.join(self.versions_dir, "history.json")
        self.current_version = 0
        self._history: list[dict] = []

        # Load existing history if present
        if os.path.exists(self.history_path):
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._history = data.get("versions", [])
                self.current_version = data.get("current_version", 0)

    def save_version(
        self,
        action: str,
        prompt: str = "",
        model: str = "",
        note: str = "",
    ) -> int:
        """Save current asset state as a new version."""
        os.makedirs(self.versions_dir, exist_ok=True)

        self.current_version += 1
        version_path = os.path.join(self.versions_dir, f"v{self.current_version}.png")
        shutil.copy2(self.asset_path, version_path)

        entry = {
            "version": self.current_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
        }
        if prompt:
            entry["prompt"] = prompt
        if model:
            entry["model"] = model
        if note:
            entry["note"] = note

        self._history.append(entry)
        self._save_history()
        return self.current_version

    def list_versions(self) -> list[dict]:
        """Return list of all version entries."""
        return list(self._history)

    def get_version_path(self, version: int) -> str:
        """Get the file path for a specific version."""
        path = os.path.join(self.versions_dir, f"v{version}.png")
        if not os.path.exists(path):
            raise ValueError(f"Version {version} not found at {path}")
        return path

    def rollback(self, version: int) -> None:
        """Restore asset to a previous version."""
        path = os.path.join(self.versions_dir, f"v{version}.png")
        if not os.path.exists(path):
            raise ValueError(f"Version {version} not found")
        shutil.copy2(path, self.asset_path)
        self.current_version = version
        self._save_history()

    def compare(self, v1: int, v2: int, output_path: str, gap: int = 4) -> None:
        """Create a side-by-side comparison image of two versions."""
        path1 = self.get_version_path(v1)
        path2 = self.get_version_path(v2)

        img1 = Image.open(path1).convert("RGBA")
        img2 = Image.open(path2).convert("RGBA")

        # Normalize heights
        max_h = max(img1.height, img2.height)
        if img1.height != max_h:
            ratio = max_h / img1.height
            img1 = img1.resize((int(img1.width * ratio), max_h), Image.LANCZOS)
        if img2.height != max_h:
            ratio = max_h / img2.height
            img2 = img2.resize((int(img2.width * ratio), max_h), Image.LANCZOS)

        # Create comparison canvas
        label_h = 24
        total_w = img1.width + gap + img2.width
        total_h = max_h + label_h
        canvas = Image.new("RGBA", (total_w, total_h), (40, 40, 40, 255))

        canvas.paste(img1, (0, label_h), img1)
        canvas.paste(img2, (img1.width + gap, label_h), img2)

        # Draw labels
        draw = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except (OSError, IOError):
            font = ImageFont.load_default()
        draw.text((4, 4), f"v{v1}", fill=(200, 200, 200, 255), font=font)
        draw.text((img1.width + gap + 4, 4), f"v{v2}", fill=(200, 200, 200, 255), font=font)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        canvas.save(output_path, "PNG")

    def _save_history(self) -> None:
        data = {
            "asset": os.path.splitext(os.path.basename(self.asset_path))[0],
            "current_version": self.current_version,
            "versions": self._history,
        }
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
