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

### Model

Use `mcp__gemini-image__generate_image` for all image generation.
Use `mcp__gemini-image__edit_image` for all image editing (chroma key, inpaint, border removal).

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

### Core Flow

```
设计图 → 分析(bbox校准) → 裁切 → AI精修重绘(纯色背景) → 去除背景
```

### Step 1: 分析

1. Read image, get pixel dimensions
2. Claude visually identifies all elements → elements.json
3. **Bbox calibration** (Claude估算有20-50px误差):
   - Test crop 关键区域验证位置
   - 对密集元素（图标行）用像素颜色扫描找精确边界
   - 反复调整直到裁切与元素完全吻合
4. Generate annotated preview → 用户确认

### Step 2: 裁切

```bash
python3 -m game_asset_tools extract --input design.png --elements elements.json --output-dir output/ --no-remove-bg --no-trim --padding 0
```

**bbox 宁大勿小** — 包含 UI 元素没关系（AI 精修时去除），截断的内容找不回来。

### Step 3: AI 精修重绘（纯色背景）

对每个裁切结果，用 AI 重绘到纯色背景上。**纯色必须与素材颜色差异最大**：

| 素材主色调 | 纯色背景 | 原因 |
|-----------|---------|------|
| 暖色（红/橙/棕/金） | 绿色 #00FF00 | 绿与暖色差异最大 |
| 冷色（蓝/青/紫） | 品红 #FF00FF | 品红与冷色差异最大 |
| 混色/不确定 | 品红 #FF00FF | 安全默认 |

**不能用白色** — 白色与高光、剑刃光效混淆。

**按素材类型的 AI prompt：**

**角色（需要透明背景）：**
```
"Change the background to solid bright green (#00FF00).
 Remove [UI elements: HP bar, damage numbers, etc].
 Keep the character EXACTLY as is with ALL details: [列出所有视觉特征].
 If any part is cut off (feet, weapons), complete it."
```

**图标边框（需要中间透明）：**
```
"Remove the [fire] content inside this icon, keep ONLY the golden border frame.
 Center area should become solid magenta (#FF00FF)."
```

**图标内容（保留底板，无边框）：**
```
"Remove the golden decorative border frame from around this icon.
 Extend the dark [brown/blue] background to fill where the border was.
 Keep the [fire/ice/lightning] content exactly the same."
```

**背景（去除前景）：**
```
"Remove all characters, UI elements, icons. Fill with the surrounding background."
```

### Step 4: 去除背景

AI 精修后图像有纯色背景，用 Python 精确去除：

**角色/需透明背景的素材 — Python 绿色键去除 + despill：**
```python
r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
dist = np.sqrt(r**2 + (g-255)**2 + b**2)
arr[dist < 180, 3] = 0  # 纯绿 → 透明
edge = (dist >= 180) & (dist < 220)
arr[edge, 3] = ((dist[edge]-180)/40*255).clip(0,255)  # 边缘渐变

# Despill: 校正绿色溢出
mask = (g > r*1.3) & (g > b*1.3) & (g > 120) & (alpha > 128)
arr[mask, 1] = (r[mask] + b[mask]) / 2  # G = avg(R,B)
```

**图标边框 — Python 品红键去除：**
```python
magenta_score = (r + b) / 2 - g
arr[magenta_score > 60, 3] = 0
```

**图标内容 — 不去背景**（保留底板颜色，游戏引擎中叠在边框下层）

**圆形按钮等简单形状 — rembg 直接去背**（唯一适用 rembg 的场景）

**血条/蓝条 — 不去背景**，直接裁切即可

### Step 5: 输出

```bash
python3 -m game_asset_tools trim --input asset.png --output asset.png --padding 6
python3 -m game_asset_tools manager --output-dir output/ --manifest output/manifest.json --output output/asset_manager.html
open output/asset_manager.html
```

### 共享边框分离

当多个图标共享同一边框时，分离为独立素材：

| 素材 | 说明 | 去背景 |
|------|------|--------|
| `icon_border.png` | 纯边框，中间+外围透明 | AI填品红 → Python色键去除 |
| `icon_fire.png` 等 | 纯内容+底板，无边框 | AI去边框延伸底板，不去背景 |

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
| Character (any) | **Green (#00FF00)** | AI → green bg → **Python chroma key + despill** | rembg destroys swords/glow effects; Python preserves all details |
| Icon with border | **Magenta (#FF00FF)** | AI → magenta bg → **Python chroma key** | rembg damages icons; Python is precise |
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

### For Characters (Python chroma key, NOT rembg)

rembg destroys semi-transparent/glowing elements (sword blades, magic effects, light particles). Always use Python chroma key for characters.

```bash
# Step 1: Crop with generous bbox (include full sword, both feet, even if UI elements are included)
# bbox must cover ALL parts — better too large than too small

# Step 2: AI replaces background with green chroma key + removes UI elements
# MCP edit_image prompt:
# "Replace ONLY the forest/background with solid bright green (#00FF00).
#  Also remove [UI elements like HP bar, damage numbers].
#  Keep the character EXACTLY as is — do not change ANY detail including
#  the complete sword blade with glow effects, both feet, all armor."

# Step 3: Python chroma key removal (green → transparent)
python3 -c "
import numpy as np
from PIL import Image
img = Image.open('greenscreen.png').convert('RGBA')
arr = np.array(img, dtype=np.float32)
r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]

# Remove green screen pixels
dist = np.sqrt(r**2 + (g-255)**2 + b**2)
arr[dist < 180, 3] = 0  # fully transparent
edge = (dist >= 180) & (dist < 220)
arr[edge, 3] = ((dist[edge]-180)/40*255).clip(0,255)  # edge blend

# Green spill correction (despill)
mask = (g > r*1.3) & (g > b*1.3) & (g > 120) & (arr[:,:,3] > 128)
arr[mask, 1] = (r[mask] + b[mask]) / 2  # G = avg(R,B)
very_green = (g > 200) & (r < 100) & (b < 100)
arr[very_green, 3] = 0

Image.fromarray(arr.astype(np.uint8)).save('nobg.png')
"

# Step 4: trim
python3 -m game_asset_tools trim --input nobg.png --output final.png --padding 6
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
- `rembg` on characters with weapons/glow effects → loses sword blades, magic particles
- `rembg` on icons with borders → destroys the border and content
- AI edit "remove background" without follow-up → no true transparency
- Use white as chroma key → blends with highlights
- Crop bbox too tight → missing feet, sword tips. Always crop generous, AI will clean up UI elements

## Model Failover

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
