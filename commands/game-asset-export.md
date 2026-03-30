---
name: game-asset-export
description: Export assets for game engines — Unity, Godot, Cocos, or Web format.
---

# Export Assets

## Usage

```
/game-asset:export unity
/game-asset:export godot
/game-asset:export web
/game-asset:export cocos
```

## Command

```bash
python3 -m game_asset_tools export --engine {engine} --input-dir output/ --export-dir ./{engine}_export/
```

## Supported Engines

| Engine | Output Structure |
|--------|-----------------|
| Unity | `Assets/Sprites/`, `Assets/UI/`, `Assets/Backgrounds/` |
| Godot | `assets/characters/`, `assets/icons/`, `assets/ui/` |
| Cocos | `assets/sprites/`, `assets/ui/`, `assets/backgrounds/` |
| Web | `images/` + `manifest.json` |

## After Export

Open the export directory and inform user:
```bash
open ./{engine}_export/
```
```
"导出完成: {count} 个文件 → ./{engine}_export/"
```
