---
name: game-asset-manage
description: Manage assets — browse, export, atlas, version history, web UI.
---

# Manage Assets

## Browse

List all assets:
```bash
ls output/characters/ output/icons/ output/ui/ output/backgrounds/ output/cards/ output/sprites/
```

Or generate HTML manager:
```bash
python3 -m game_asset_tools manager --output-dir output/ --manifest output/manifest.json --output output/asset_manager.html
open output/asset_manager.html
```

## Export

```bash
python3 -m game_asset_tools export --engine unity --input-dir output/ --export-dir ./unity_export/
python3 -m game_asset_tools export --engine godot --input-dir output/ --export-dir ./godot_export/
python3 -m game_asset_tools export --engine web --input-dir output/ --export-dir ./web_export/
```

## Atlas

```bash
python3 -m game_asset_tools atlas --input-dir output/icons/ --output output/sprites/atlas.png --meta output/sprites/atlas.json --max-size 1024x1024
```

## Version History

```bash
python3 -m game_asset_tools version list --asset output/characters/hero.png
python3 -m game_asset_tools version rollback --asset output/characters/hero.png --to 1
```

## Nine-Slice

```bash
python3 -m game_asset_tools nine_slice --input output/ui/panel.png --output-dir output/ui/panel_sliced/ --border 12 --preview
```

## Web Service

```bash
# Start (from project directory)
PYTHONPATH=${CLAUDE_PLUGIN_ROOT} uvicorn server.main:app --port 8080 --app-dir ${CLAUDE_PLUGIN_ROOT}
# Open http://localhost:8080
```

## Resize

```bash
python3 -m game_asset_tools resize --input asset.png --output asset_64.png --size 64x64 --mode contain
```
