---
name: game-asset
description: Generate and extract 2D game assets. Three commands — generate, extract, manage.
---

# Game Asset Design

Help users create production-ready 2D game assets.

## Commands

| Command | When to use |
|---------|------------|
| `/game-asset:generate` | Create new assets — characters, icons, UI, cards, backgrounds |
| `/game-asset:extract` | Extract assets from a design image |
| `/game-asset:manage` | Browse assets, export, atlas, version history |

## First Time Setup

If no `game-assets.yaml` exists, ask:
1. Art style (anime / pixel / ghibli / cyberpunk / fantasy / watercolor / flat / realistic)
2. Reference image path (optional — a design mockup that defines the visual direction)
3. Create `game-assets.yaml` and output directories

## /game-asset:generate

**One command, one asset, ready to use.**

### Character
```
User: "生成一个暗黑战士角色"

1. Read styles.csv → anime preset → NanoBanana style=anime
2. Build prompt from prompt_templates.csv character/full_body
3. Add to prompt: "on solid bright green #00FF00 background"
4. Generate with NanoBanana (failover to Gemini)
5. Auto: chromakey green → trim → save
6. Done: output/characters/char_{name}_v1.png (transparent)
```

### Icon Set (ALWAYS generate as a set)
```
User: "生成火球、冰晶、闪电三个技能图标"

1. Build prompt from prompt_templates.csv icon_set/batch
2. Generate ALL icons in ONE image (16:9)
3. Auto: smart-split by detecting bright regions → resize each to 128x128
4. Done: output/icons/icon_{name}_v1.png × N
```

### Single Icon
```
Same as icon set but count=1. Still use dark background, no border.
```

### Background
```
Generate with 16:9, no post-processing needed.
```

### Card
```
One-shot generation: character + border + title in single image.
Resize to 750x1050.
```

### Key Rules
- **Generate on colored background** — green for warm content, magenta for cool
- **NanoBanana first, Gemini fallback** — NanoBanana has better style consistency
- **Icon sets in one image** — never generate icons individually
- **Max 1 AI call per asset** — no editing, no refinement passes

## /game-asset:extract

**Upload design image → get all assets.**

```
User: "从这张图提取所有素材" + image path

1. Read image, get dimensions
2. Claude visually identifies elements (type, bbox)
3. For each element, decide the best approach:
   - Character → crop generous bbox, recommend regenerating with NanoBanana instead
   - Icons → recommend regenerating from description (better quality than extraction)
   - Buttons → crop + rembg (simple shapes)
   - HP/MP bars → crop only
   - Background → crop + AI inpaint if needed
4. Ask user to confirm before processing
5. Execute and save to output/
```

**Critical insight: for characters and icons, REGENERATING produces better results than EXTRACTING.** The extract command should recommend regeneration when possible, only falling back to crop+process for simple elements (buttons, bars).

## /game-asset:manage

**Everything else.**

```
/game-asset:manage                    → list all assets
/game-asset:manage export unity       → export for Unity
/game-asset:manage atlas icons        → pack icons into atlas
/game-asset:manage version list hero  → version history
/game-asset:manage serve              → start web UI
```

## Data Files

`data/` directory contains reference tables:

| File | Purpose |
|------|---------|
| `styles.csv` | Style presets: prompt keywords, model params, chroma key colors |
| `prompt_templates.csv` | Prompt templates with negative prompts |
| `asset_types.csv` | Asset type specs: sizes, ratios, output dirs |
| `pipelines.csv` | Processing steps per asset type |
| `rules.csv` | Decision rules (priority 1-8) |

## Style Consistency

If `game-assets.yaml` has `reference_image`:
1. Read it before generating
2. Describe its visual characteristics in the prompt
3. Match color palette, lighting, detail level

## MCP Tools

- `mcp__grsai-nanobanana__generate_image` — Primary: style presets, consistency
- `mcp__gemini-image__generate_image` — Fallback: flexible, reliable
- `mcp__gemini-image__edit_image` — Only for: green screen swap, inpaint background

## Python Toolkit

```bash
python3 -m game_asset_tools --help
```

Used internally by commands. Users don't need to call directly.
