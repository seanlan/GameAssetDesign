---
name: game-asset
description: Game asset design and extraction toolkit. Route to specific commands based on user intent.
---

# Game Asset Design

You are a game asset designer. Help users generate, extract, and manage 2D game assets.

## ALWAYS start here

1. Check if `game-assets.yaml` exists in current directory
2. If not → run `/game-asset:init` first
3. If yes → read `style.reference_image` for style consistency
4. Read `data/rules.csv` for priority rules (1=critical, 8=low)
5. Read `data/pipelines.csv` for the correct processing pipeline

## Knowledge Base

All data files are in `skills/game-asset/data/`:

| File | Purpose |
|------|---------|
| `asset_types.csv` | Asset type specs: sizes, aspect ratios, transparency, prompt suffixes |
| `pipelines.csv` | Step-by-step processing pipeline per asset type (priority ordered) |
| `styles.csv` | Style presets: prompt keywords, NanoBanana/Gemini params, chroma key color |
| `rules.csv` | Decision rules with priority levels 1-8 (1=critical) |
| `prompt_templates.csv` | Reusable prompt templates with variable placeholders |

**Read these files before generating or processing assets.** They codify tested best practices.

## Commands

| Command | When to use |
|---------|------------|
| `/game-asset:init` | FIRST command. Create project config with style and reference image |
| `/game-asset:generate` | Create new assets. Read `asset_types.csv` + `prompt_templates.csv` first |
| `/game-asset:analyze` | Analyze design image. Read `rules.csv` priority 3 (bbox rules) |
| `/game-asset:extract` | Extract from design. Read `pipelines.csv` for correct pipeline per type |
| `/game-asset:refine` | Fix/improve assets. Read `rules.csv` priority 1-2 (quality + bg removal) |
| `/game-asset:manage` | Browse all assets in management panel |
| `/game-asset:serve` | Start web management service |
| `/game-asset:version` | Version history, rollback, compare |
| `/game-asset:export` | Export for Unity/Godot/Cocos/Web |
| `/game-asset:atlas` | Pack into texture atlas |

## Workflows

### Generate from scratch (MUST follow this order)
```
/game-asset:init → /game-asset:generate → /game-asset:manage → /game-asset:refine → /game-asset:export
```

### Extract from design image (MUST follow this order)
```
/game-asset:init → /game-asset:analyze → /game-asset:extract → /game-asset:manage → /game-asset:refine → /game-asset:export
```

## Processing Pipeline Decision Table

Read `pipelines.csv` for full details. Quick reference:

| Asset Type | Pipeline | Key Rule |
|-----------|----------|----------|
| Character | crop → AI green screen (1次) → Python chromakey → trim | Max 1 AI edit |
| Icon (single) | crop → NanoBanana regenerate from description | Don't AI-edit, regenerate |
| Icon (batch) | Generate all in 1 image → split | Same context = same style |
| Icon border | crop → AI hollow center (magenta) → Python chromakey | Separate border from content |
| Button | crop → rembg directly | Simple shape, rembg works |
| HP/MP bar | crop only | No processing needed |
| Background | crop → AI inpaint foreground | Remove characters/UI |
| Card | One-shot generation (character+border+title) | Single AI call |
| Sprite | Generate ref → video → extract frames → rembg → assemble | Video preserves character |
| Tileset | Generate with "seamless" → assemble with --seamless | Edge blending |
| Nine-slice | crop → nine_slice with border width | 9 parts for scalable UI |

## Style Consistency

### Reference Image (Critical)
```yaml
# game-assets.yaml
style:
  reference_image: "path/to/effect_image.png"  # Global style reference
```

When generating ANY asset:
1. Read the reference image with Read tool
2. Analyze its visual style (color palette, lighting, detail level, art direction)
3. Incorporate those style characteristics into the generation prompt
4. Use matching NanoBanana style param from `styles.csv`

### Batch Consistency
For multiple same-type assets (icon sets, character series):
- **Generate in one image then split** (best consistency)
- Use identical prompt template from `prompt_templates.csv`
- Same NanoBanana `style` parameter for all

## Critical Rules (from rules.csv)

**Priority 1 — Quality:**
- Never AI-edit more than once
- Icons: regenerate, don't edit
- Icon sets: generate in one image for consistency

**Priority 2 — Background Removal:**
- Characters: chroma key (green/magenta) + Python, NOT rembg
- Buttons: rembg only (simple shapes)
- Never white chroma key (blends with highlights)
- Select chroma by contrast: warm→green, cool→magenta

**Priority 3 — Bbox:**
- Generous bbox, bigger is better
- Claude estimates have 20-50px error, always calibrate
- Pixel scanning for dense elements

## MCP Tools

- `mcp__gemini-image__generate_image` — Gemini image generation
- `mcp__gemini-image__edit_image` — Gemini image editing (chroma key, inpaint)
- `mcp__grsai-nanobanana__generate_image` — NanoBanana generation (anime/ghibli/pixel styles)
- `mcp__grsai-nanobanana__blend_images` — Style-consistent blending

## Python Toolkit

```bash
python3 -m game_asset_tools --help
```

19 commands: resize, remove_bg, trim, chromakey, sprite_sheet, card_composer, video_to_frames, tileset, annotate, extract, pipeline, version, manager, atlas, export, preview, auto_detect, nine_slice, style_unify
