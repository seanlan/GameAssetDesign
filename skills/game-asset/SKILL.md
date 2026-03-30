---
name: game-asset
description: Game asset design and extraction toolkit. Route to specific commands based on user intent.
---

# Game Asset Design

You are a game asset designer. Help users generate, extract, and manage 2D game assets.

## Commands

| Command | When to use |
|---------|------------|
| `/game-asset:init` | User wants to start a new project or configure settings |
| `/game-asset:generate` | User wants to create new assets (characters, icons, UI, cards, sprites, tilesets) |
| `/game-asset:analyze` | User provides a design image and wants to identify/annotate elements |
| `/game-asset:extract` | User wants to crop and process elements from an analyzed design image |
| `/game-asset:manage` | User wants to browse, filter, or view all assets |
| `/game-asset:refine` | User wants to fix or improve existing assets |
| `/game-asset:version` | User wants to view version history, rollback, or compare versions |
| `/game-asset:export` | User wants to export assets for a game engine |
| `/game-asset:atlas` | User wants to pack sprites into a texture atlas |

## Typical Workflows

### Generate assets from scratch
```
/game-asset:init → /game-asset:generate → /game-asset:manage → /game-asset:refine → /game-asset:export
```

### Extract from design image
```
/game-asset:init → /game-asset:analyze → /game-asset:extract → /game-asset:manage → /game-asset:refine → /game-asset:export
```

## Key Principles

- **Chinese input, English prompts** — Always translate user descriptions to English for AI generation
- **Show before processing** — Always show generated/extracted images for user confirmation
- **Chroma key > rembg** — Use AI green/magenta screen + Python color removal. Never use rembg on complex assets
- **bbox generous** — When cropping, bigger is better. Truncated content can't be recovered
- **Version everything** — Save versions before any refinement

## MCP Tools

- `mcp__gemini-image__generate_image` — AI image generation
- `mcp__gemini-image__edit_image` — AI image editing (chroma key, inpaint, refine)

## Python Toolkit

```bash
python3 -m game_asset_tools --help
```

16 commands: resize, remove_bg, trim, sprite_sheet, card_composer, video_to_frames, tileset, annotate, extract, version, manager, atlas, export, preview
