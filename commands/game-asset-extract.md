---
name: game-asset-extract
description: Extract assets from a design image — crop, AI refine with chroma key background, remove background.
---

# Extract Assets from Design Image

Prerequisite: run `/game-asset:analyze` first to generate `output/.tmp/elements.json`

## Core Flow

```
裁切 → AI精修重绘(纯色背景) → 去除背景 → 输出
```

## Step 1: Crop

```bash
python3 -m game_asset_tools extract --input design.png --elements output/.tmp/elements.json --output-dir output/ --no-remove-bg --no-trim --padding 0
```

## Step 2: AI Refine (Chroma Key Background)

For each cropped asset, AI replaces background with chroma key color.

**Chroma key color selection — must contrast with asset colors:**

| Asset dominant color | Chroma key | Reason |
|---------------------|-----------|--------|
| Warm (red/orange/brown/gold) | Green #00FF00 | Maximum contrast |
| Cool (blue/cyan/purple) | Magenta #FF00FF | Maximum contrast |
| Green | Magenta #FF00FF | Avoid same hue |
| Mixed/unsure | Magenta #FF00FF | Safe default |

**NEVER use white** — blends with highlights, sword glints, light effects.

### AI prompts by asset type:

**Character (needs transparent bg):**
```
"Change the background to solid bright green (#00FF00).
 Remove [UI elements: HP bar, damage numbers, etc].
 Keep the character EXACTLY as is with ALL details: [list visual features].
 If any part is cut off (feet, weapons), complete it."
```

**Icon border (needs transparent center):**
```
"Remove the [content] inside this icon, keep ONLY the border frame.
 Center area should become solid magenta (#FF00FF)."
```

**Icon content (keep background plate, no border):**
```
"Remove the decorative border frame from around this icon.
 Extend the dark background to fill where the border was.
 Keep the content exactly the same."
```

**Background (remove foreground):**
```
"Remove all characters, UI elements, icons.
 Fill with the surrounding background."
```

## Step 3: Remove Background

### Character — Python green chroma key + despill (NOT rembg):
```python
r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
dist = np.sqrt(r**2 + (g-255)**2 + b**2)
arr[dist < 180, 3] = 0
edge = (dist >= 180) & (dist < 220)
arr[edge, 3] = ((dist[edge]-180)/40*255).clip(0,255)

# Despill
mask = (g > r*1.3) & (g > b*1.3) & (g > 120) & (arr[:,:,3] > 128)
arr[mask, 1] = (r[mask] + b[mask]) / 2
very_green = (g > 200) & (r < 100) & (b < 100)
arr[very_green, 3] = 0
```

### Icon border — Python magenta key:
```python
magenta_score = (r + b) / 2 - g
arr[magenta_score > 60, 3] = 0
```

### Icon content — NO removal (keep background plate)

### Simple shapes (buttons) — rembg directly

### Health/mana bars — NO removal, crop only

## Step 4: Output

```bash
python3 -m game_asset_tools trim --input asset.png --output asset.png --padding 6
```

Update manifest, then inform:
```
"提取完成，共 N 个素材。Use /game-asset:manage to view and manage assets."
```

## NEVER do:
- rembg on characters with weapons/glow → loses details
- rembg on icons with borders → destroys borders
- White as chroma key → blends with highlights
- Tight bbox → missing feet, sword tips
