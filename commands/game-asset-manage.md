---
name: game-asset-manage
description: Open the asset manager — browse, filter, and manage all project assets.
---

# Asset Manager

## Launch

```bash
python3 -m game_asset_tools manager --output-dir output/ --manifest output/manifest.json --output output/asset_manager.html
open output/asset_manager.html
```

If web server is running (`python3 -m game_asset_tools serve`), open `http://localhost:8080` instead.

## Features

The asset manager provides:

- **Browse** — Grid view of all assets with thumbnails
- **Filter** — By type (character/icon/ui/card/background/sprite/tileset)
- **Sort** — By time, type, name
- **Search** — By filename or keyword
- **Select** — Click to select assets for batch operations
- **Detail view** — Expand to see: prompt, model, style, generation time, post-processing steps, version history, relationships
- **Progress dashboard** — Project completion status (requires `requirements` in project config)

## Operations from Manager

After selecting assets, user can request:
- `/game-asset:refine` — Fix selected assets
- `/game-asset:export` — Export selected assets
- `/game-asset:atlas` — Pack selected into atlas
- `/game-asset:version` — View version history

## Auto-Refresh

The manager page is regenerated after every operation:
- After `/game-asset:generate`
- After `/game-asset:extract`
- After `/game-asset:refine`
- After any delete/rename/reclassify
