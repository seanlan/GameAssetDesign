# Game Asset Design

A Claude Code skill for generating, extracting, and managing 2D game assets.

## Install

```bash
claude plugin add github:lanjinmin/GameAssetDesign
```

Or manually:

```bash
git clone https://github.com/lanjinmin/GameAssetDesign.git
cd GameAssetDesign
pip3 install -r requirements.txt
```

## Requirements

- Python 3.10+
- Claude Code with `gemini-image` MCP server configured
- Optional: `imgbb` MCP server for image sharing

## Usage

In Claude Code, use the `/game-asset` skill:

```
/game-asset generate a fire mage character
/game-asset extract assets from this design image
/game-asset open asset manager
/game-asset export for Unity
```

## Features

### Generate Assets
- Characters, icons, UI elements, cards, sprite sheets, tilesets
- Style presets: pixel, anime, cel_shading, watercolor, flat, realistic
- Project config controls style, sizes, and output structure

### Extract from Design Images
- AI-powered element detection with layer separation
- Annotated preview for visual confirmation
- Shared border/frame separation
- Chroma key background removal (green/magenta)

### Post-Processing Pipeline
```
Design Image → Analyze → Crop → AI Refine (chroma key bg) → Remove Background
```

### Asset Management
- Interactive HTML asset manager with filtering, sorting, selection
- Version history (save, rollback, compare)
- Refinement workflow (edge fix, AI edit, inpaint, style unify)
- Project progress dashboard

### Export
- Engine-specific export: Unity, Godot, Cocos, Web
- Texture atlas packing with metadata

## Python CLI

```bash
python3 -m game_asset_tools --help
```

16 commands: `resize`, `remove_bg`, `trim`, `sprite_sheet`, `card_composer`, `video_to_frames`, `tileset`, `annotate`, `extract`, `version`, `manager`, `atlas`, `export`, `preview`

## License

MIT
