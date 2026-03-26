"""Generation manifest for asset traceability."""

import json
import os
from datetime import datetime, timezone


class Manifest:
    """Manages a manifest.json file tracking generated assets."""

    def __init__(self, output_dir: str, project_name: str):
        self.path = os.path.join(output_dir, "manifest.json")
        self.project_name = project_name
        self.entries: list[dict] = []

        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.entries = data.get("assets", [])

    def add_entry(
        self,
        file: str,
        asset_type: str,
        prompt: str,
        model: str,
        style: str = "",
        aspect_ratio: str = "",
        raw_file: str = "",
        post_processing: list[str] | None = None,
        preset: str = "",
        reference_image: str | None = None,
        project_config: str = "",
        relationships: dict | None = None,
    ) -> None:
        """Add a generation record."""
        entry = {
            "file": file,
            "type": asset_type,
            "prompt": prompt,
            "model": model,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        if style:
            entry["style"] = style
        if aspect_ratio:
            entry["aspect_ratio"] = aspect_ratio
        if raw_file:
            entry["raw_file"] = raw_file
        if post_processing:
            entry["post_processing"] = post_processing
        if preset:
            entry["preset"] = preset
        if reference_image:
            entry["reference_image"] = reference_image
        if project_config:
            entry["project_config"] = project_config
        if relationships:
            entry["relationships"] = relationships

        self.entries.append(entry)

    def get_entry(self, file: str) -> dict | None:
        """Return the entry dict for the given file, or None if not found."""
        for entry in self.entries:
            if entry.get("file") == file:
                return entry
        return None

    def add_relationship(self, file: str, rel_type: str, target: str) -> None:
        """Add a relationship target to an existing entry."""
        entry = self.get_entry(file)
        if entry is None:
            return
        if "relationships" not in entry:
            entry["relationships"] = {}
        if rel_type not in entry["relationships"]:
            entry["relationships"][rel_type] = []
        if isinstance(entry["relationships"][rel_type], str):
            entry["relationships"][rel_type] = [entry["relationships"][rel_type]]
        if target not in entry["relationships"][rel_type]:
            entry["relationships"][rel_type].append(target)

    def save(self) -> None:
        """Write manifest to disk."""
        data = {
            "project": self.project_name,
            "assets": self.entries,
        }
        os.makedirs(os.path.dirname(self.path) if os.path.dirname(self.path) else ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
