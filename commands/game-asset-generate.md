---
name: game-asset-generate
description: Generate new game assets with AI — characters, icons, UI, cards, sprite sheets, tilesets.
---

# Generate Game Assets

## BEFORE generating

1. Load `game-assets.yaml` — get style preset, reference image, keywords
2. Read `data/asset_types.csv` — get sizes, aspect ratio, prompt suffix for the target type
3. Read `data/prompt_templates.csv` — get the prompt template + negative prompt for the target type
4. Read `data/styles.csv` — get NanoBanana/Gemini style params and chroma key color
5. Read `data/rules.csv` — priority 1 (quality) and priority 4 (style) rules
6. If `reference_image` is set → Read it, analyze visual style, incorporate into prompt

## Prompt Construction

```
Template from prompt_templates.csv
  + style keywords from styles.csv
  + project keywords from game-assets.yaml
  + prompt suffix from asset_types.csv
```

## Model Selection (from styles.csv)

- If `nanobanana_style` column has value → use `mcp__grsai-nanobanana__generate_image` with that style
- Otherwise → use `mcp__gemini-image__generate_image` with `gemini_style` value
- NanoBanana produces better style consistency for anime/ghibli/pixel/cyberpunk/fantasy

## Generation by Type

### Character
1. Use template: `character/full_body` from prompt_templates.csv
2. Fill: {name}, {description} from user, {style_keywords} from config
3. Generate with 3:4 aspect ratio
4. Show result → user confirms
5. Post-process per `pipelines.csv`: AI green screen → chromakey → trim

### Icon (Single)
1. Use template: `icon/single`
2. Generate with 1:1 aspect ratio
3. No post-processing needed (has dark bg plate, no border)

### Icon Set (Batch) — RECOMMENDED for consistency
1. Use template: `icon_set/batch`
2. Generate ALL icons in one image (16:9)
3. Split into individual icons with Python crop
4. Resize each to target sizes
5. **This is the best method for style consistency**

### Card
1. Use template: `card/complete`
2. One-shot generation (character + border + title in single image)
3. Resize to 750x1050

### Background
1. Use template: `background/scene` or `background/battle`
2. Generate with 16:9
3. No characters or UI in the prompt

### Sprite
1. Use template: `sprite/reference` for hero image
2. Then video → extract frames → assemble

### UI Button
1. Use template: `ui_button/states` to generate 4 states in one image
2. Split into normal/hover/pressed/disabled

### Tileset
1. Use template: `tileset/seamless`
2. Test by tiling 3x3 after generation

## After Generation

1. Show result via Read tool → user confirms
2. If confirmed → post-process per `pipelines.csv`
3. Save to `output/{type}/` per `asset_types.csv` output_dir column
4. Update manifest
5. Inform: "Use /game-asset:manage to view all assets"
