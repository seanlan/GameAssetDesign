---
name: game-asset-extract
description: Extract assets from a design image — crop, AI refine with chroma key background, remove background.
---

# Extract Assets from Design Image

Prerequisite: run `/game-asset:analyze` first to generate `output/.tmp/elements.json`

## BEFORE extracting

1. Read `data/pipelines.csv` — find the correct pipeline for each element type
2. Read `data/styles.csv` — get chroma key color for each element's color tone
3. Read `data/rules.csv` — priority 2 (bg removal) and priority 3 (bbox) rules

## Core Flow

```
裁切 → AI精修重绘(纯色背景) → 去除背景 → 输出
```

## Step 1: Crop

```bash
python3 -m game_asset_tools extract --input design.png --elements output/.tmp/elements.json --output-dir output/ --no-remove-bg --no-trim --padding 0
```

## Step 2: Per-Type Processing (from pipelines.csv)

For each extracted element, look up its type in `pipelines.csv` and follow the steps:

### Character (pipelines.csv: type=character)
```
crop → ai_greenscreen (green #00FF00) → chromakey → trim(padding=10)
```
- Chroma key color: from `styles.csv` chroma_key column based on content color tone
- AI prompt: "Change background to solid bright green #00FF00. Remove UI elements. Keep ALL character details."

### Icon Content (pipelines.csv: type=icon_content)
```
crop → nanobanana_regenerate (from description, not edit!) → resize
```
- **Do NOT AI-edit the crop** — regenerate from description for better quality
- Use prompt template from `prompt_templates.csv` icon/single

### Icon Border (pipelines.csv: type=icon_border)
```
crop → ai_hollow (magenta #FF00FF) → chromakey → cleanup
```

### Button (pipelines.csv: type=ui_button)
```
crop → rembg → trim(padding=4)
```

### HP/MP Bar (pipelines.csv: type=ui_bar)
```
crop only — no background removal
```

### Background (pipelines.csv: type=background)
```
crop → ai_inpaint (remove foreground)
```

## Step 3: Output

```bash
python3 -m game_asset_tools trim --input asset.png --output asset.png --padding 6
```

Update manifest, then:
```bash
python3 -m game_asset_tools manager --output-dir output/ --manifest output/manifest.json --output output/asset_manager.html
```

## One-Step Alternative

For quick extraction without manual per-type processing:

```bash
python3 -m game_asset_tools pipeline --input design.png --output-dir output/
```

This runs: auto-detect → annotate → extract → chromakey → trim in one step.
