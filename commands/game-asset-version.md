---
name: game-asset-version
description: Asset version management — view history, rollback, compare versions side by side.
---

# Version Management

## Commands

### List version history
```bash
python3 -m game_asset_tools version list --asset output/characters/warrior.png
```

### Rollback to a previous version
```bash
python3 -m game_asset_tools version rollback --asset output/characters/warrior.png --to 1
```

### Compare two versions side by side
```bash
python3 -m game_asset_tools version compare --asset output/characters/warrior.png --v1 1 --v2 3 --output output/.tmp/compare.png
```
Show the comparison image via Read tool.

### Save current state as a version
```bash
python3 -m game_asset_tools version save --asset output/characters/warrior.png --action "ai_edit" --note "Changed color to red"
```

## Usage Examples

```
/game-asset:version 显示 warrior 的版本历史
/game-asset:version 回滚 warrior 到 v1
/game-asset:version 对比 warrior 的 v1 和 v3
```

## Version Storage

```
output/characters/
├── warrior.png                    ← Current version
└── .versions/warrior/
    ├── v1.png
    ├── v2.png
    ├── v3.png
    └── history.json
```
