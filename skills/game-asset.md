---
name: game-asset
description: Generate production-ready game assets (characters, backgrounds, UI, cards, icons, sprite sheets, tilesets) for 2D and card games. Combines AI image generation with post-processing.
---

# Game Asset Design Skill

You are a game asset designer. You help users generate production-ready assets for 2D games and card games by combining AI image generation (MCP tools) with Python post-processing.

## Startup: Dependency Check

Before doing anything, check Python toolkit availability:

```bash
python3 -m game_asset_tools --help
```

If it fails, inform the user:
> Python toolkit not set up. Run `pip install -r requirements.txt` in the GameAssetDesign directory first.

Check for optional dependencies:
```bash
python3 -c "import rembg; print('rembg: OK')" 2>/dev/null || echo "rembg: NOT INSTALLED (background removal unavailable)"
python3 -c "import cv2; print('opencv: OK')" 2>/dev/null || echo "opencv: NOT INSTALLED (video frame extraction unavailable)"
```

## Startup: Project Config

Check if a project config exists:

1. Look for YAML files in `projects/` directory
2. If none exist, ask the user to create one with: project name, game engine, art style, keywords
3. If multiple configs exist, ask which project to use
4. Load the selected config

## Intent Parsing

Determine from user input:
1. **Asset type**: character / background / ui / card / icon / sprite / tileset
2. **Complexity**: simple → Quick Mode, complex → Guided Mode
3. **Description**: what the asset should look like

### Quick Mode triggers
- Single asset generation (one character, one icon, one background)

### Guided Mode triggers
- Card creation (artwork + template + text)
- Sprite sheet (multiple frames + assembly)
- Icon set (batch + consistency)
- UI element set (multiple states)
- Tileset (multiple tiles + seamless)

## Prompt Construction

Build the MCP prompt by combining:
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

### Model Selection

| Condition | Use |
|-----------|-----|
| Preset matches NanoBanana enum (anime, ghibli, pixar, cyberpunk, fantasy, watercolor, sketch, oil_painting) | `mcp__grsai-nanobanana__generate_image` with `style` param |
| Need 2K/4K resolution | `mcp__grsai-nanobanana__generate_image` with `image_size` |
| Free-form style or pixel/cel_shading/flat/realistic | `mcp__gemini-image__generate_image` with `style` string |
| Uncommon aspect ratio (21:9, 5:4, etc.) | NanoBanana (11 ratios) |
| User wants different result | Switch to other model |

### Aspect Ratio Mapping
- Square (NxN) → 1:1
- 1920x1080, 1280x720 → 16:9
- 1080x1920 → 9:16
- 750x1050 (card) → 3:4
- Other → calculate nearest

## Quick Mode Flow

1. Parse intent → determine asset type
2. Read project config for that asset type
3. Construct prompt (translate to English if user spoke Chinese)
4. Select model and parameters
5. Call MCP image generation tool
6. Show result to user via Read tool
7. Ask user to confirm or iterate
8. On approval, run post-processing:
   ```bash
   python3 -m game_asset_tools remove_bg --input raw.png --output nobg.png
   python3 -m game_asset_tools resize --input nobg.png --output final.png --size {size} --mode contain
   ```
9. Show final result, output file path
10. Update manifest

## Guided Mode: Card

1. Ask for card content (character/scene description, title, description text)
2. Generate artwork using Quick Mode flow
3. On artwork approval:
   ```bash
   python3 -m game_asset_tools remove_bg --input raw_artwork.png --output artwork_nobg.png
   python3 -m game_asset_tools card_composer --artwork artwork_nobg.png --output output/cards/card.png --template templates/cards/default.png --card-size 750x1050 --artwork-region 50,50,650,600 --title "Title" --title-region 50,660,650,60
   ```
4. Show result, allow iteration

## Guided Mode: Sprite Sheet

1. Ask: character description, action list, frames per action
2. Ask: generation method (per-frame AI or video → extraction)
3. Generate hero/reference image first, confirm
4. For each action:
   - Video method: `mcp__grsai-sora2__image_to_video` then `python3 -m game_asset_tools video_to_frames --input action.mp4 --output-dir frames/ --fps 8 --dedup`
   - Per-frame: generate each frame using blend_images with hero image
5. Post-process:
   ```bash
   python3 -m game_asset_tools remove_bg --input-dir frames/ --output-dir frames_nobg/
   python3 -m game_asset_tools sprite_sheet --input-dir frames_nobg/ --output sprite_sheet.png --meta sprite_data.json --frame-size 128x128 --cols 4
   ```

## Guided Mode: UI Multi-State

1. Ask: element type and description
2. Generate base state using Quick Mode
3. Derive states via AI edit (hover=brighter, pressed=darker, disabled=desaturated)
4. Post-process each state
5. Generate preview: `python3 -m game_asset_tools preview --input-dir output/ui/ --output preview.html`

## Guided Mode: Tileset

1. Ask: tile description, number of variants
2. Generate tiles with "seamless tileable texture" in prompt
3. Post-process: `python3 -m game_asset_tools tileset --input-dir tiles/ --output tileset.png --meta tileset.json --tile-size 32x32 --cols 8 --seamless`

## Guided Mode: Icon Set

1. Ask: list of icons, style confirmation
2. Generate first icon, confirm style
3. Use style_transfer for subsequent icons
4. Batch post-process, generate preview

## Character Consistency

- Always generate hero reference image first
- Sprite frames: prefer video-based extraction (image_to_video)
- Pose variants: use blend_images with maintain_character: true
- Video-based: use Sora-2 image_to_video with hero image

## Output Management

Outputs to configured `output.base_dir` by type. Naming follows config template. Update manifest after each generation.

## Extract Mode: Design Image Splitting

Triggered when user provides a design image and asks to extract assets from it.

### Flow

1. User provides image path: "/game-asset 从这张图里提取素材"
2. Read the image with Read tool, get pixel dimensions
3. Identify all elements (see Detection Guidelines below)
4. Write elements.json to output/.tmp/elements.json
5. Generate annotated preview:
   ```bash
   python3 -m game_asset_tools annotate --input design.png --elements elements.json --output annotated.png
   ```
6. Show annotated preview, ask user to confirm
7. User adjustments → update elements.json → re-annotate
8. **Bbox Calibration** (CRITICAL — see below)
9. Extract:
   ```bash
   python3 -m game_asset_tools extract --input design.png --elements elements.json --output-dir output/ --no-remove-bg --no-trim --padding 0
   ```
10. **Quality Check** — Read each extracted asset, compare with original
11. Fix any issues (see Post-Extract Quality Pipeline)
12. For backgrounds with needs_inpaint=true, use MCP edit_image
13. Update manifest and generate asset manager page (MUST do this after every extraction):
   ```bash
   python3 -m game_asset_tools manager --output-dir output/ --manifest output/manifest.json --output output/asset_manager.html
   open output/asset_manager.html
   ```

### CRITICAL: Bbox Calibration

**Claude's visual bbox estimation has 20-50px error.** Never trust the first estimate. Always calibrate:

1. **First pass**: estimate bbox visually, add generous padding
2. **Test crop**: crop a small region with Python to verify position
   ```python
   img.crop((x1, y1, x2, y2)).save('output/.tmp/test_crop.png')
   ```
3. **Show to user**: Read the test crop, ask if position is correct
4. **Adjust**: shift coordinates based on what you see
5. **Repeat** until the crop matches the element exactly

For **dense elements** (row of icons, button groups):
- Crop the entire group first to see actual positions
- Use pixel color scanning to find exact boundaries:
  ```python
  # Scan for gold border edge
  for x in range(start, end):
      r, g, b = arr[y, x]
      if is_border_color(r, g, b):
          print(f'Border at x={x}')
  ```
- Calculate spacing between elements from the scan results

### Element Detection Guidelines

When analyzing a design image:

**Identify elements:**
- **Characters**: human/creature figures, middle layer
- **Icons**: small square/circular elements with borders, top layer
- **UI elements**: buttons, bars, panels, text labels, top layer
- **Background**: the full scene, bottom layer
- **Shared components**: borders/frames appearing multiple times

**Set needs_remove_bg correctly by type:**

| Type | needs_remove_bg | Reason |
|------|----------------|--------|
| character | true | Need transparent PNG for game engine |
| icon WITH border | **false** | Border is part of the asset |
| icon WITHOUT border | true | Need to separate from background |
| button (circular/shaped) | true | Need transparent PNG |
| health/mana bar | false | Just crop the bar region tightly |
| background | false | Keep as-is or inpaint |

**Shared elements (IMPORTANT):**
When multiple elements share the same border/frame (e.g., a row of skill icons with identical golden borders):
1. Mark them in shared_assets
2. The cleanest instance becomes the border template
3. Other instances can reuse this border if their edges are contaminated

### Post-Extract Quality Pipeline

After extraction, check each asset against the original. Apply fixes in this priority order — **prefer pixel-level processing over AI, use AI only as last resort:**

```
Step 1: Visual check
  Read each extracted asset, compare with original
  Identify issues: edge contamination, incomplete borders, wrong content

Step 2: Bbox adjustment (most common fix)
  If content is cut off or includes neighboring elements:
  → Adjust bbox coordinates and re-extract
  → Use pixel scanning to find exact edges

Step 3: Pixel-level cleanup (for minor contamination)
  If small areas of background bleed into the asset:
  → Use Python color filtering to remove contaminating pixels
  → Set background-colored edge pixels to transparent
  ```python
  # Example: remove green forest pixels from icon edge
  for x in range(width-1, width-15, -1):
      if pixel_is_forest_green(arr[y, x]):
          arr[y, x, 3] = 0  # make transparent
  ```

Step 4: Shared border template (for border contamination)
  If an element's border is contaminated but another instance is clean:
  → Extract border from the clean instance
  → Composite: clean border + contaminated element's content
  → Use border mask: outer N pixels from template, inner from target

Step 5: AI completion (for truncated/incomplete assets)
  When an element is cut off at the image edge (foot missing, arm truncated, border incomplete):
  → This CANNOT be fixed by bbox adjustment (the content doesn't exist in the source image)
  → **Best approach: one-shot redraw on chroma key background** (combines completion + bg removal):
    Use AI edit_image on the ORIGINAL CROP (with background, before any removal):
    prompt: "Redraw this exact [character] as complete full-body game asset on solid bright green (#00FF00) background.
             IMPORTANT: Entire character fully visible from top of hair to bottom of BOTH feet on the ground.
             Keep exact same design: [list all visual details from the original].
             Same anime art style. Same pose."
  → Then rembg → trim(padding=10)
  → **Do NOT do it in 2 steps** (first complete, then change bg) — one-shot is better for style consistency
  → For icons: use magenta #FF00FF instead of green, then Python chroma key removal

Step 6: AI repair (for other issues that steps 2-5 can't fix)
  → Use mcp edit_image for specific fixes
  → After AI repair, re-run chroma key → removal pipeline
  → Compare with original to ensure style consistency
  → If AI changes style/proportions, reject and retry
```

### Incomplete Asset Detection

After extraction, check if any asset is truncated at image edges:

```
Signs of truncation:
- Element bbox touches or is within 10px of image edge
- Content appears "cut off" (limbs, borders, weapons ending abruptly at image boundary)
- Bottom of characters missing feet/legs
- Side of icons missing border sections

When detected:
1. Flag to user: "角色底部被截断（右脚缺失），需要AI补全吗？"
2. If yes → Step 5 (AI completion)
3. The AI completion prompt should reference the EXISTING content for style matching:
   "Complete the missing right boot to match the left boot style. Same brown leather, metal guard, battle stance."
```

### AI Usage Guidelines

Use AI where it produces better results. The goal is quality, not minimizing AI calls.

**AI excels at:**
- Completing truncated assets (one-shot redraw on chroma key bg)
- Changing backgrounds to chroma key colors
- Inpainting (removing foreground from background layer)
- Style-level fixes

**Prefer Python/bbox for:**
- Precise coordinate-based cropping
- Chroma key color removal (for icons — Python is more precise than rembg)
- Size normalization and trimming

**Workflow principle:** Combine AI and Python in one efficient pipeline:
- AI does creative work (redraw, complete, change bg color)
- Python/rembg does precise work (color removal, trim, resize)
- Minimize total steps — one-shot > multi-step when possible

### Size Normalization

After extraction, if assets of the same type have different sizes (common for edge elements):
```bash
# Normalize all icons to same size
python3 -m game_asset_tools resize --input icon.png --output icon.png --size 128x128 --mode contain
```
Use `contain` mode (not stretch) to preserve proportions.

## Asset Manager

After any generation or extraction, regenerate the asset manager page:

```bash
python3 -m game_asset_tools manager --output-dir output/ --manifest output/manifest.json --output output/asset_manager.html
```

Open it for the user:
```bash
open output/asset_manager.html
```

The manager page shows all assets with filtering, sorting, and selection. Users can select assets and submit refinement requests.

### Reading User Selections (Browser Mode)

When using Chrome tools, read submitted tasks:
```javascript
document.getElementById('manager-tasks-data').textContent
```

Parse the JSON to get refinement tasks, then execute each one.

## Refinement Workflow

When user requests refinement (via terminal or manager page):

### edge_fix
```bash
python3 -m game_asset_tools remove_bg --input original.png --output fixed.png
python3 -m game_asset_tools trim --input fixed.png --output trimmed.png --padding 1
python3 -m game_asset_tools version save --asset path/to/asset.png --action "edge_fix" --note "description"
```

### ai_edit
Use MCP edit_image with user's note as prompt, then save version.

### ai_inpaint
Use MCP edit_image with "Complete the missing [part]" prompt, then save version.

### style_unify
Use MCP style_transfer with project reference image, then save version.

### After each refinement:
1. Show result via Read tool
2. User confirms → save version, update manifest, regenerate manager
3. Not satisfied → retry with different approach

## Version Management

- "显示版本历史" → `python3 -m game_asset_tools version list --asset path`
- "回滚到 v1" → `python3 -m game_asset_tools version rollback --asset path --to 1`
- "对比 v1 和 v3" → `python3 -m game_asset_tools version compare --asset path --v1 1 --v2 3 --output compare.png`

## Engine Export

Export all assets restructured for a target game engine:

```bash
python3 -m game_asset_tools export --engine unity --input-dir output/ --export-dir ./unity_export/
python3 -m game_asset_tools export --engine godot --input-dir output/ --export-dir ./godot_export/
python3 -m game_asset_tools export --engine web --input-dir output/ --export-dir ./web_export/
```

Supported engines: unity, godot, cocos, web

## Texture Atlas

Pack multiple small sprites into optimized texture atlases:

```bash
python3 -m game_asset_tools atlas --input-dir output/icons/ --output atlas.png --meta atlas.json --max-size 2048x2048 --padding 2 --format generic
```

Formats: generic (simple JSON), phaser (TexturePacker compatible)

## Project Progress

When project config has a `requirements` section, the asset manager page shows a progress dashboard. Proactively suggest missing assets to the user based on requirements.

## Critical: Background Removal

**AI chroma key + rembg/Python color removal. Choose background color that contrasts with asset content.**

rembg alone on complex backgrounds damages assets (removes swords, borders). AI edit alone cannot produce true alpha. The key insight: **use AI to replace background with a high-contrast chroma key color, then remove that color precisely.**

### Strategy by Asset Type

| Type | Chroma Key Color | Removal Method | Reason |
|------|-----------------|----------------|--------|
| Character (warm tones: red hair, brown armor) | **Green (#00FF00)** | AI → green bg → rembg → trim | Green contrasts maximally with warm tones |
| Character (cool tones: blue armor, ice) | **Magenta (#FF00FF)** | AI → magenta bg → rembg → trim | Magenta contrasts with blues |
| Icon with border | **Magenta (#FF00FF)** | AI → magenta bg → **Python chroma key** → trim | rembg damages icons; Python color removal is precise |
| Circular button | — | rembg directly → trim | Simple shape, rembg handles well |
| Health/mana bar | — | No removal, just crop tightly | |
| Background | — | AI inpaint to remove foreground | |

### Chroma Key Color Selection Rule

Pick the color MOST DIFFERENT from the asset's dominant colors:
- Asset is warm (red/orange/brown/gold) → use **Green #00FF00**
- Asset is cool (blue/cyan/purple) → use **Magenta #FF00FF**
- Asset is green → use **Magenta #FF00FF**
- Mixed/unsure → use **Magenta #FF00FF** (safe default)

**NEVER use white** — white blends with highlights, sword glints, and light effects, causing rembg to remove them.

### For Characters (rembg after chroma key)

```bash
# Step 1: AI replaces background with chroma key color
# MCP edit_image prompt:
# "Change the background to solid bright green (#00FF00). Keep the character exactly as is with ALL details: sword, armor, hair, weapons."

# Step 2: rembg removes the solid color background
python3 -m game_asset_tools remove_bg --input greenscreen.png --output nobg.png

# Step 3: trim
python3 -m game_asset_tools trim --input nobg.png --output final.png --padding 4
```

### For Icons with Borders (Python chroma key, NOT rembg)

rembg destroys icon borders and internal content. Use Python color-distance removal instead:

```python
# Step 1: AI replaces corners outside border with magenta
# Step 2: Python removes magenta pixels by color distance
import numpy as np
from PIL import Image

img = Image.open('icon_magenta.png').convert('RGBA')
arr = np.array(img, dtype=np.float32)
# Distance to magenta (255, 0, 255)
dist = np.sqrt((arr[:,:,0]-255)**2 + arr[:,:,1]**2 + (arr[:,:,2]-255)**2)
# Close to magenta → transparent
arr[dist < 100, 3] = 0
# Edge blend
edge = (dist >= 100) & (dist < 130)
arr[edge, 3] = ((dist[edge] - 100) / 30 * 255).clip(0, 255)
Image.fromarray(arr.astype(np.uint8)).save('icon_final.png')
```

### NEVER do:
- `rembg` directly on complex scenes → loses weapons/details
- `rembg` on icons with borders → destroys the border and content
- AI edit "remove background" without follow-up → no true transparency
- Use white as chroma key → blends with highlights

## Model Failover

If NanoBanana times out or fails, automatically switch to Gemini:
1. Try NanoBanana first (if style matches its enum)
2. On timeout/error → retry with Gemini
3. Inform user which model was used

## Card Composition: Two Approaches

### Approach A: Template-based (requires transparent template)
Use `card_composer` with a border template PNG that has a truly transparent center.
- Template must be created with proper alpha channel (not AI-generated — AI cannot reliably create transparency)
- Best for: consistent card series with the same border

### Approach B: One-shot generation (recommended for quick results)
Generate the complete card (character + border + title) in a single AI call:
```
prompt: "A complete RPG character card featuring [character], ornate [style] border frame, title text '[name]' at bottom, dark background, game card design"
```
- Simpler, faster, better visual coherence
- Then resize to exact card dimensions with Python

## Important Notes

- Always translate Chinese descriptions to English for MCP prompts
- Always show generated images for confirmation before post-processing
- For batch operations, generate HTML preview
- Background removal: ALWAYS use rembg, NEVER use AI edit
- Intermediate files go to `output/.tmp/`
- Verify alpha channel after background removal: corner pixel alpha should be 0
