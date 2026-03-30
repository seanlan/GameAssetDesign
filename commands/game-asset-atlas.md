---
name: game-asset-atlas
description: Pack multiple sprites into optimized texture atlases for game engines.
---

# Texture Atlas Packing

## Usage

```
/game-asset:atlas icons
/game-asset:atlas output/icons/ --max-size 2048x2048
```

## Command

```bash
python3 -m game_asset_tools atlas \
  --input-dir output/icons/ \
  --output output/sprites/atlas.png \
  --meta output/sprites/atlas.json \
  --max-size 2048x2048 \
  --padding 2 \
  --format generic
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--max-size` | 2048x2048 | Maximum atlas dimensions |
| `--padding` | 2 | Pixel spacing between sprites |
| `--format` | generic | Metadata format: `generic` or `phaser` |

## Output

- `atlas.png` (or `atlas_0.png`, `atlas_1.png` if multiple pages needed)
- `atlas.json` — sprite coordinates metadata

## After Packing

Show the atlas image and metadata summary:
```
"图集打包完成: {count} 个精灵 → {atlas_size}. Metadata: atlas.json"
```
