# game_asset_tools/manager.py
"""Unified Asset Manager HTML generation.

Replaces preview.py. Generates a self-contained interactive HTML page for:
- Browsing all project assets with filtering and sorting
- Selecting assets for refinement operations
- Viewing manifest provenance details
- Submitting refinement tasks (readable by skill via Chrome tools)
"""

import base64
import json
import os
from PIL import Image


ASSET_SUBDIRS = {
    "characters": "character",
    "icons": "icon",
    "ui": "ui",
    "cards": "card",
    "backgrounds": "background",
    "sprites": "sprite",
    "tilesets": "tileset",
}


def _scan_assets(output_dir: str) -> list[dict]:
    """Scan output directory for all asset files."""
    assets = []
    for subdir, asset_type in ASSET_SUBDIRS.items():
        dir_path = os.path.join(output_dir, subdir)
        if not os.path.isdir(dir_path):
            continue
        for root, dirs, files in os.walk(dir_path):
            # Skip .versions directories
            dirs[:] = [d for d in dirs if d != ".versions"]
            for fname in sorted(files):
                if fname.lower().endswith((".png", ".jpg", ".jpeg")) and not fname.startswith("."):
                    fpath = os.path.join(root, fname)
                    rel_path = os.path.relpath(fpath, output_dir)
                    is_shared = "shared" in root
                    try:
                        img = Image.open(fpath)
                        w, h = img.size
                    except Exception:
                        w, h = 0, 0
                    assets.append({
                        "file": rel_path,
                        "filename": fname,
                        "type": asset_type,
                        "path": fpath,
                        "width": w,
                        "height": h,
                        "size_bytes": os.path.getsize(fpath),
                        "is_shared": is_shared,
                    })
    return assets


def _merge_manifest(assets: list[dict], manifest_path: str | None) -> list[dict]:
    """Merge manifest metadata into scanned assets."""
    if not manifest_path or not os.path.exists(manifest_path):
        return assets

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    manifest_map = {}
    for entry in manifest.get("assets", []):
        manifest_map[entry.get("file", "")] = entry

    for asset in assets:
        meta = manifest_map.get(asset["file"], {})
        asset["prompt"] = meta.get("prompt", "")
        asset["model"] = meta.get("model", "")
        asset["style"] = meta.get("style", "")
        asset["generated_at"] = meta.get("generated_at", "")
        asset["post_processing"] = meta.get("post_processing", [])
        asset["relationships"] = meta.get("relationships", {})

    return assets


def _asset_to_b64(path: str) -> str:
    """Read an image file and return base64-encoded data URI."""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    ext = path.rsplit(".", 1)[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")
    return f"data:{mime};base64,{data}"


def _build_dashboard_html(progress: dict) -> str:
    """Generate progress dashboard HTML section from check_progress() result."""
    if not progress:
        return ""

    rows = ""
    total_done = 0
    total_all = 0
    all_missing = []

    for category, data in sorted(progress.items()):
        done = data["done"]
        total = data["total"]
        total_done += done
        total_all += total
        pct = int(done / total * 100) if total > 0 else 0
        missing = data.get("missing", [])
        all_missing.extend([(category, m) for m in missing])
        bar_color = "#4caf50" if pct == 100 else ("#e94560" if pct == 0 else "#f0a020")
        rows += f"""
  <div class="dash-row">
    <span class="dash-cat">{category}</span>
    <div class="dash-bar-wrap">
      <div class="dash-bar" style="width:{pct}%;background:{bar_color}"></div>
    </div>
    <span class="dash-pct">{done}/{total}</span>
  </div>"""

    # Overall summary
    overall_pct = int(total_done / total_all * 100) if total_all > 0 else 0

    # Missing items list (up to 20)
    missing_items_html = ""
    if all_missing:
        items_html = "".join(
            f'<span class="missing-tag">{cat}: {name}</span>'
            for cat, name in all_missing[:20]
        )
        if len(all_missing) > 20:
            items_html += f'<span class="missing-tag">...+{len(all_missing)-20} more</span>'
        missing_items_html = f'<div class="missing-list"><strong>Missing:</strong> {items_html}</div>'

    return f"""
<div class="dashboard">
  <div class="dash-header">
    <span>Progress: {total_done}/{total_all} ({overall_pct}%)</span>
  </div>
  {rows}
  {missing_items_html}
</div>"""


def generate_manager_html(
    output_dir: str,
    manifest_path: str | None,
    html_path: str,
    project_name: str = "",
    project_config: str | None = None,
) -> None:
    """Generate the unified asset manager HTML page."""
    assets = _scan_assets(output_dir)
    assets = _merge_manifest(assets, manifest_path)

    if not project_name and manifest_path and os.path.exists(manifest_path):
        with open(manifest_path) as f:
            project_name = json.load(f).get("project", "Game Assets")

    if not project_name:
        project_name = "Game Assets"

    # Build progress dashboard if project_config provided
    dashboard_html = ""
    if project_config and os.path.exists(project_config):
        from game_asset_tools.config import load_config, get_requirements, check_progress
        try:
            cfg = load_config(project_config)
            requirements = get_requirements(cfg)
            if requirements:
                progress = check_progress(requirements, output_dir)
                dashboard_html = _build_dashboard_html(progress)
        except Exception:
            pass  # Dashboard is optional; don't fail HTML generation

    # Build asset cards HTML
    cards_html = ""
    assets_json = []
    for idx, asset in enumerate(assets):
        b64 = _asset_to_b64(asset["path"])
        size_str = f"{asset['size_bytes'] / 1024:.1f}KB" if asset["size_bytes"] > 1024 else f"{asset['size_bytes']}B"
        shared_badge = ' <span class="badge shared">shared</span>' if asset.get("is_shared") else ""

        # Build detail info
        details = []
        if asset.get("prompt"):
            details.append(f"Prompt: {asset['prompt']}")
        if asset.get("model"):
            details.append(f"Model: {asset['model']}")
        if asset.get("style"):
            details.append(f"Style: {asset['style']}")
        if asset.get("generated_at"):
            details.append(f"Time: {asset['generated_at'][:19]}")
        if asset.get("post_processing"):
            details.append(f"Post: {', '.join(asset['post_processing'])}")
        rels = asset.get("relationships", {})
        if rels.get("derived_from"):
            details.append(f"From: {rels['derived_from']}")
        if rels.get("used_by"):
            details.append(f"Used by: {', '.join(rels['used_by'])}")
        details_html = "<br>".join(details) if details else "No metadata"

        cards_html += f"""
    <div class="card" data-idx="{idx}" data-type="{asset['type']}" data-name="{asset['filename']}" data-file="{asset['file']}" onclick="toggleCard(this)">
      <div class="card-check">&#9744;</div>
      <img src="{b64}" alt="{asset['filename']}" loading="lazy">
      <div class="info">
        <div class="fname">#{idx+1} {asset['filename']}{shared_badge}</div>
        <div class="meta">{asset['type']} &middot; {asset['width']}x{asset['height']} &middot; {size_str}</div>
      </div>
      <div class="details">{details_html}</div>
    </div>"""

        assets_json.append({
            "idx": idx,
            "file": asset["file"],
            "filename": asset["filename"],
            "type": asset["type"],
        })

    # Count by type
    type_counts = {}
    for a in assets:
        t = a["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    filter_buttons = "".join(
        f'<button class="fbtn" onclick="filterType(\'{t}\')">{t} ({c})</button>'
        for t, c in sorted(type_counts.items())
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Asset Manager: {project_name}</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, 'Segoe UI', sans-serif; background: #0f0f1a; color: #e0e0e0; }}
.header {{ background: #1a1a2e; padding: 16px 24px; border-bottom: 1px solid #2a2a4a; }}
.header h1 {{ color: #e94560; font-size: 20px; }}
.toolbar {{ background: #16213e; padding: 10px 24px; border-bottom: 1px solid #1a1a3e; display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }}
.fbtn {{ background: #0f3460; color: #ccc; border: 1px solid #1a4a80; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; }}
.fbtn:hover, .fbtn.active {{ background: #e94560; color: #fff; border-color: #e94560; }}
.search {{ background: #0a0a1a; color: #eee; border: 1px solid #333; padding: 4px 10px; border-radius: 4px; font-size: 12px; width: 180px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; padding: 16px 24px; }}
.card {{ background: #16213e; border-radius: 8px; overflow: hidden; border: 2px solid transparent; cursor: pointer; transition: border-color 0.15s; position: relative; }}
.card:hover {{ border-color: #3a5a8a; }}
.card.selected {{ border-color: #e94560; }}
.card.selected .card-check {{ color: #e94560; }}
.card-check {{ position: absolute; top: 6px; right: 6px; font-size: 18px; color: #555; }}
.card img {{ width: 100%; height: 140px; object-fit: contain; background: repeating-conic-gradient(#222 0% 25%, #2a2a2a 0% 50%) 50%/12px 12px; }}
.info {{ padding: 6px 10px; }}
.fname {{ font-size: 11px; font-weight: 600; word-break: break-all; }}
.meta {{ font-size: 10px; color: #888; margin-top: 2px; }}
.badge {{ font-size: 9px; padding: 1px 5px; border-radius: 3px; }}
.badge.shared {{ background: #6a3dad; color: #fff; }}
.details {{ display: none; padding: 6px 10px; font-size: 10px; color: #999; border-top: 1px solid #1a1a3e; line-height: 1.6; }}
.card.expanded .details {{ display: block; }}
.actions {{ background: #1a1a2e; padding: 12px 24px; border-top: 1px solid #2a2a4a; display: none; }}
.actions.visible {{ display: block; }}
.actions h3 {{ font-size: 14px; color: #e94560; margin-bottom: 8px; }}
.abtn {{ background: #0f3460; color: #ccc; border: 1px solid #1a4a80; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-size: 12px; margin-right: 6px; }}
.abtn:hover {{ background: #e94560; color: #fff; }}
.note-input {{ background: #0a0a1a; color: #eee; border: 1px solid #333; padding: 6px 10px; border-radius: 4px; font-size: 12px; width: 100%; margin: 8px 0; }}
.submit-btn {{ background: #e94560; color: #fff; border: none; padding: 8px 20px; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: 600; }}
.submit-btn:hover {{ background: #c73650; }}
#manager-tasks-data {{ display: none; }}
.dashboard {{ background: #16213e; border: 1px solid #2a2a4a; margin: 12px 24px; border-radius: 8px; padding: 12px 16px; }}
.dash-header {{ font-size: 13px; font-weight: 600; color: #e94560; margin-bottom: 8px; }}
.dash-row {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }}
.dash-cat {{ font-size: 11px; color: #aaa; width: 100px; flex-shrink: 0; text-transform: capitalize; }}
.dash-bar-wrap {{ flex: 1; background: #0a0a1a; border-radius: 4px; height: 10px; overflow: hidden; }}
.dash-bar {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
.dash-pct {{ font-size: 11px; color: #ccc; width: 40px; text-align: right; flex-shrink: 0; }}
.missing-list {{ margin-top: 8px; font-size: 11px; color: #999; }}
.missing-tag {{ display: inline-block; background: #2a1a2e; border: 1px solid #4a2a5a; border-radius: 3px; padding: 1px 6px; margin: 2px; color: #d08aff; }}
</style>
</head>
<body>
<div class="header"><h1>Asset Manager: {project_name}</h1></div>
<div class="toolbar">
  <button class="fbtn active" onclick="filterType('all')">all ({len(assets)})</button>
  {filter_buttons}
  <input class="search" type="text" placeholder="Search..." oninput="searchAssets(this.value)">
  <button class="fbtn" onclick="selectAll()">Select All</button>
  <button class="fbtn" onclick="deselectAll()">Deselect</button>
</div>
{dashboard_html}
<div class="grid" id="grid">{cards_html}
</div>
<div class="actions" id="actions">
  <h3>Selected: <span id="sel-count">0</span> assets</h3>
  <div>
    <button class="abtn" onclick="setRefineType('edge_fix')">edge_fix</button>
    <button class="abtn" onclick="setRefineType('ai_edit')">ai_edit</button>
    <button class="abtn" onclick="setRefineType('ai_inpaint')">ai_inpaint</button>
    <button class="abtn" onclick="setRefineType('style_unify')">style_unify</button>
    <button class="abtn" onclick="setRefineType('delete')" style="border-color:#c33">delete</button>
    <button class="abtn" onclick="setRefineType('reclassify')">reclassify</button>
  </div>
  <input class="note-input" id="note" type="text" placeholder="Describe what to change...">
  <button class="submit-btn" onclick="submitTasks()">Submit</button>
</div>
<pre id="manager-tasks-data"></pre>
<script>
const assets = {json.dumps(assets_json)};
let selectedIdxs = new Set();
let currentRefineType = '';

function toggleCard(el) {{
  const idx = parseInt(el.dataset.idx);
  if (el.classList.contains('expanded') && !el.classList.contains('selected')) {{
    el.classList.remove('expanded');
    return;
  }}
  el.classList.toggle('selected');
  el.querySelector('.card-check').innerHTML = el.classList.contains('selected') ? '&#9745;' : '&#9744;';
  if (el.classList.contains('selected')) selectedIdxs.add(idx); else selectedIdxs.delete(idx);
  updateActions();
  // Toggle detail on double concept - expand on second click
  if (!el.classList.contains('selected')) el.classList.toggle('expanded');
}}

function updateActions() {{
  const panel = document.getElementById('actions');
  document.getElementById('sel-count').textContent = selectedIdxs.size;
  panel.classList.toggle('visible', selectedIdxs.size > 0);
}}

function filterType(type) {{
  document.querySelectorAll('.fbtn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  document.querySelectorAll('.card').forEach(c => {{
    c.style.display = (type === 'all' || c.dataset.type === type) ? '' : 'none';
  }});
}}

function searchAssets(q) {{
  q = q.toLowerCase();
  document.querySelectorAll('.card').forEach(c => {{
    c.style.display = c.dataset.name.toLowerCase().includes(q) ? '' : 'none';
  }});
}}

function selectAll() {{
  document.querySelectorAll('.card').forEach(c => {{
    if (c.style.display !== 'none') {{
      c.classList.add('selected');
      c.querySelector('.card-check').innerHTML = '&#9745;';
      selectedIdxs.add(parseInt(c.dataset.idx));
    }}
  }});
  updateActions();
}}

function deselectAll() {{
  document.querySelectorAll('.card').forEach(c => {{
    c.classList.remove('selected');
    c.querySelector('.card-check').innerHTML = '&#9744;';
  }});
  selectedIdxs.clear();
  updateActions();
}}

function setRefineType(t) {{ currentRefineType = t; }}

function submitTasks() {{
  const note = document.getElementById('note').value;
  const tasks = [];
  selectedIdxs.forEach(idx => {{
    const a = assets[idx];
    tasks.push({{ asset_id: idx+1, file: a.file, name: a.filename, type: currentRefineType, note: note }});
  }});
  const data = JSON.stringify({{ tasks: tasks }}, null, 2);
  document.getElementById('manager-tasks-data').textContent = data;
  alert('Tasks submitted (' + tasks.length + '). Skill can now read the data.');
}}
</script>
</body>
</html>"""

    os.makedirs(os.path.dirname(html_path) or ".", exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
