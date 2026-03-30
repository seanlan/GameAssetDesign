---
name: game-asset-generate
description: Generate new game assets with AI — characters, icons, UI, cards, sprite sheets, tilesets.
---

# Generate Game Assets

## Prerequisites
- Project config must exist (run `/game-asset:init` first)
- Load project config from `projects/` directory

## Prompt Construction

```
[User description in English] + [Preset keywords] + [Project keywords] + [Palette]
```

### Style Presets

| Preset | Keywords |
|--------|----------|
| pixel | pixel art, 16-bit style, clean pixels, no anti-aliasing |
| anime | anime style, cel shading, vibrant colors, clean lines |
| cel_shading | cel shaded, flat colors, bold outlines, cartoon style |
| watercolor | watercolor painting, soft edges, muted colors |
| flat | flat design, minimal shading, solid colors, vector style |
| realistic | semi-realistic, detailed rendering, painterly style |

### Model
- `mcp__gemini-image__generate_image` for generation
- `mcp__gemini-image__edit_image` for editing

### Aspect Ratio
- Square → 1:1
- 1920x1080 → 16:9
- 1080x1920 → 9:16
- 750x1050 (card) → 3:4

## Quick Mode (Single Asset)

For: one character, one icon, one background

1. Determine asset type from user description
2. Read project config for sizes/style
3. Translate to English, construct prompt
4. Call `mcp__gemini-image__generate_image`
5. Show result → user confirms or iterates
6. Post-process (see Background Removal below)
7. Save to `output/{type}/`, update manifest

## Guided Mode: Card

1. Ask: character description, title, description text
2. Generate artwork → confirm
3. Recommended: one-shot card generation
```
prompt: "A complete RPG character card featuring [character], ornate [style] border frame, title text '[name]' at bottom, dark background, game card design"
```
4. Resize to card dimensions with Python

## Guided Mode: Sprite Sheet

1. Ask: character description, actions, frames per action
2. Generate hero reference image → confirm
3. For each action: video → frame extraction or per-frame generation
4. Post-process: remove bg → sprite sheet assembly

## Guided Mode: UI Multi-State

1. Generate base state → confirm
2. Derive states via AI edit (hover/pressed/disabled)
3. Post-process each state

## Guided Mode: Icon Set

1. Generate first icon → confirm style
2. Subsequent icons use style_transfer
3. Batch post-process

## Guided Mode: Tileset

1. Generate tiles with "seamless tileable texture" in prompt
2. Assembly with `--seamless` flag

## Background Removal (after generation)

Use chroma key approach — see `/game-asset:extract` for full details.

For generated assets with simple backgrounds: `rembg` may work directly.
For complex cases: AI green screen → Python chroma key removal.

## After Generation

Update manifest and inform user:
```
"素材已生成: output/{type}/{filename}. Use /game-asset:manage to view all assets."
```
