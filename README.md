# Game Asset Design

A Claude Code skill for generating, extracting, and managing 2D game assets. Combines AI image generation (Gemini) with a Python post-processing toolkit to produce game-engine-ready assets.

## Features

### Asset Generation
Generate production-ready game assets with AI:
- Characters, icons, UI elements, cards, sprite sheets, tilesets
- 6 style presets: pixel, anime, cel_shading, watercolor, flat, realistic
- Project config for consistent style across all assets

### Design Image Extraction
Extract individual assets from design mockups, screenshots, or reference images:

```
Design Image → Analyze (bbox calibration) → Crop → AI Refine (chroma key) → Remove Background
```

- AI-powered element detection with layer separation (top/middle/bottom)
- Annotated preview for visual confirmation before extraction
- Shared border/frame separation (border + content as independent assets)
- Chroma key background removal — green (#00FF00) or magenta (#FF00FF), never white

### Asset Management
- Interactive HTML asset manager (filter, sort, select, refine)
- Version history with rollback and side-by-side comparison
- Refinement workflow: edge fix, AI edit, AI inpaint, style unify
- Project progress dashboard with requirements tracking

### Export & Packaging
- Engine-specific export: Unity, Godot, Cocos, Web
- Texture atlas packing (shelf-first-fit) with Phaser/generic metadata

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
- Claude Code
- `gemini-image` MCP server (for AI image generation/editing)
- Optional: `imgbb` MCP server (for image sharing)

## Usage

```
/game-asset generate a fire mage character portrait
/game-asset extract assets from this UI design [image path]
/game-asset open asset manager
/game-asset export for Unity
/game-asset pack icons into texture atlas
```

## Python CLI

```bash
python3 -m game_asset_tools --help
```

16 commands:

| Command | Description |
|---------|-------------|
| `resize` | Resize/crop images (contain, cover, stretch) |
| `remove_bg` | Background removal via rembg |
| `trim` | Trim transparent edges |
| `sprite_sheet` | Assemble sprite sheet + frame metadata |
| `card_composer` | Card composition with text rendering |
| `video_to_frames` | Extract frames from video + dedup |
| `tileset` | Tileset assembly + seamless blending |
| `annotate` | Draw element detection boxes on design image |
| `extract` | Batch extract elements from design image |
| `version` | Asset version management (save/list/rollback/compare) |
| `manager` | Generate interactive asset manager HTML |
| `atlas` | Texture atlas packing |
| `export` | Engine-specific export (Unity/Godot/Cocos/Web) |
| `preview` | Generate asset preview page |

## Project Structure

```
skills/game-asset.md     — Claude Code skill file
game_asset_tools/        — Python post-processing toolkit (16 commands)
projects/                — Project configs (style, sizes, requirements)
templates/               — Card templates, fonts
output/                  — Asset output directory
tests/                   — 130+ tests
```

## Key Design Decisions

**Background removal**: AI chroma key + Python color removal. rembg alone destroys semi-transparent elements (sword blades, glow effects, icon borders). The pipeline: AI replaces background with chroma key color (green/magenta) → Python precisely removes that color by distance calculation → despill correction.

**Icon border/content separation**: Icons with shared borders are split into reusable border (transparent center) + swappable content (with background plate). AI removes border and extends background fill; Python handles chroma key removal for the border asset.

**Bbox calibration**: Claude's visual coordinate estimation has 20-50px error. Pixel-level color scanning calibrates boundaries before extraction.

## License

MIT
