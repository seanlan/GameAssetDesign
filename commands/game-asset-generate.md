---
name: game-asset-generate
description: Generate game assets — characters, icons, UI, cards, backgrounds. Auto post-processing included.
---

# Generate Game Assets

## Before Starting

1. If no `game-assets.yaml` → ask user for style preset and create it
2. Read `data/styles.csv` → get model params and chroma key color
3. Read `data/prompt_templates.csv` → get template for the asset type
4. If reference_image set → analyze it, incorporate style into prompt

## Character

Generate on green background → auto chromakey → done.

```
Prompt template: character/full_body from prompt_templates.csv
Add: "on solid bright green #00FF00 background"
Model: NanoBanana style=anime (failover Gemini)
Aspect: 3:4
Post: chromakey green → trim padding=8
Output: output/characters/char_{name}_v1.png
```

## Icon Set

ALWAYS generate all icons in ONE image for style consistency.

```
Prompt template: icon_set/batch from prompt_templates.csv
Model: NanoBanana or Gemini
Aspect: 16:9
Post: detect bright regions → split → resize to 128x128
Output: output/icons/icon_{name}_v1.png × N
```

## Background

```
Prompt template: background/scene
Aspect: 16:9
Post: none (or resize)
Output: output/backgrounds/bg_{name}_v1.png
```

## Card

One-shot: character + border + title in single generation.

```
Prompt template: card/complete
Aspect: 3:4
Post: resize to 750x1050
Output: output/cards/card_{name}_v1.png
```

## UI Button

```
Prompt template: ui_button/states (4 states in 2x2 grid)
Post: split into 4 → rembg each → trim
Output: output/ui/btn_{name}_{state}.png
```

## Rules

- **1 AI call per asset** — no editing passes
- **NanoBanana first** — better style consistency, failover to Gemini
- **Green bg for characters** — chromakey removal preserves all details
- **Icon sets as batch** — never generate individually
- **Show result** — always show to user before saving
