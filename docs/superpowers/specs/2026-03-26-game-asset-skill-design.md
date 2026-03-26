# Game Asset Design Skill - Design Spec

## Overview

A Claude Code skill (`/game-asset`) that generates production-ready game assets for 2D games and UI/card games. Combines AI image generation (via MCP tools) with a Python post-processing toolkit to bridge the gap between AI-generated images and game-engine-ready assets.

## Architecture

**Approach: Skill + Python Tool Library**

- **Skill file** (`game-asset.md`): Handles user interaction, intent parsing, mode selection, MCP tool orchestration, and quality control flow.
- **Python tool library** (`game_asset_tools/`): Handles deterministic image post-processing — background removal, resizing, sprite sheet assembly, card composition, video frame extraction.

### Project Structure

```
GameAssetDesign/
├── skills/
│   └── game-asset.md              # Claude Code skill file
├── game_asset_tools/              # Python tool library
│   ├── __init__.py
│   ├── cli.py                     # CLI entry: python3 -m game_asset_tools <command>
│   ├── remove_bg.py               # Background removal (rembg)
│   ├── resize.py                  # Resize / crop
│   ├── sprite_sheet.py            # Sprite sheet assembly + frame data export
│   ├── card_composer.py           # Card layout composition
│   ├── video_to_frames.py         # Video frame extraction
│   ├── tileset.py                 # Tileset assembly
│   └── preview.py                 # Batch asset preview HTML generator
├── templates/                     # Card borders, UI templates, fonts
│   ├── cards/
│   ├── ui/
│   └── fonts/                     # Default + custom fonts
├── projects/                      # Project config directory
│   └── example_project.yaml       # Example project config
├── output/                        # Default asset output directory
│   ├── characters/
│   ├── backgrounds/
│   ├── ui/
│   ├── cards/
│   ├── icons/
│   ├── sprites/
│   └── tilesets/
└── requirements.txt               # Python dependencies
```

### Flow Overview

```
User input → Skill parses intent → Select mode (quick / guided)
    → MCP tools generate raw image → Python toolkit post-processes → Output to typed directory
```

## Supported Asset Types

| Type | Description | Transparent | Typical Use |
|------|-------------|-------------|-------------|
| Character | Portraits, full-body art | Yes | RPG characters, visual novel |
| Background | Scene backgrounds | No | Battle scenes, menus |
| UI Element | Buttons, borders, bars | Yes | HUD, menus |
| Card | Full card with frame + art | No | Card games, gacha |
| Icon | Item / skill icons | Yes | Inventory, skill trees |
| Sprite Sheet | Multi-frame animation sheet | Yes | 2D character animation |
| Tileset | Tile grid for maps | Yes | Level design |

## Project Configuration

Each game project has a YAML config file controlling style, sizes, and output specs:

```yaml
# projects/my_game.yaml
project:
  name: "My RPG Game"
  engine: "unity"           # unity / godot / cocos / web / custom

style:
  preset: "anime"           # Built-in: pixel / anime / cel_shading / watercolor / flat / realistic
  reference_image: null     # Reference image path, overrides preset
  keywords: "vibrant colors, cel shading, fantasy theme"
  palette: ["#2C3E50", "#E74C3C", "#F39C12", "#27AE60"]

assets:
  character:
    sizes: [512, 1024]
    format: "png"
    transparent: true
  background:
    sizes: ["1920x1080", "1280x720"]
    format: "png"
    transparent: false
  icon:
    sizes: [64, 128, 256]
    format: "png"
    transparent: true
  card:
    size: "750x1050"
    template: "templates/cards/default.png"
    layout:
      artwork: [50, 50, 650, 600]    # [x, y, w, h]
      title: [50, 660, 650, 60]
      description: [50, 740, 650, 200]
  sprite:
    frame_size: [128, 128]
    format: "png"
    transparent: true
  tileset:
    tile_size: [32, 32]
    format: "png"

output:
  base_dir: "output/"
  naming: "{type}_{name}_{size}"
```

### Usage

- First-time use: skill guides project config creation
- Asset generation auto-reads config — no need to repeat parameters
- Supports multi-project switching

## Interaction Modes

### Quick Mode (Simple Requests)

```
User: /game-asset generate a fire mage character portrait
    → Skill parses intent → asset type: character
    → Read project config → get style / size / transparency params
    → Build prompt (user description + style keywords + preset)
    → Call MCP to generate image
    → Show user for confirmation (satisfied? regenerate? edit?)
    → Auto post-process (remove bg → resize → name → save to output/characters/)
    → Output final file path + preview
```

### Guided Mode (Complex Requests)

```
User: /game-asset I need a warrior character sprite sheet
    → Skill enters guided flow:
      1. Confirm character description (appearance, equipment)
      2. Confirm action list (idle / walk / attack / hurt / death)
      3. Confirm frames per action
      4. Choose generation method:
         a) Per-frame AI generation
         b) AI video generation → frame extraction
    → Generate per action → show for confirmation each step
    → User satisfied → Python post-process:
      - Remove background
      - Normalize frame sizes
      - Assemble sprite sheet
      - Export frame data JSON
    → Output sprite_sheet.png + sprite_data.json
```

### Mode Selection Logic

| User Input | Mode | Reason |
|-----------|------|--------|
| "generate a fire icon" | Quick | Single asset, no complex composition |
| "generate a warrior character" | Quick | Single portrait |
| "make a fire mage card" | Guided | Requires portrait + frame + layout |
| "make a walk animation" | Guided | Multi-frame + sprite sheet |
| "generate an RPG icon set" | Guided | Batch + style consistency |

## Python Tool Library

### CLI Interface

```bash
python3 -m game_asset_tools <command> [options]
```

### Modules

**`remove_bg` — Background Removal**
```bash
python3 -m game_asset_tools remove_bg --input a.png --output b.png
```
- Based on `rembg` library, supports batch processing
- Outputs PNG with alpha channel

**`resize` — Resize / Crop**
```bash
python3 -m game_asset_tools resize --input a.png --size 128x128 --mode contain --output b.png
```
- Modes: `contain` (keep ratio, transparent padding), `cover` (crop to fill), `stretch`
- Batch: `--input-dir ./raw/ --output-dir ./resized/ --size 64x64`

**`sprite_sheet` — Sprite Sheet Assembly**
```bash
python3 -m game_asset_tools sprite_sheet --input-dir ./frames/ --cols 4 --frame-size 128x128 --output sheet.png --meta sheet.json
```
- Sorts by filename, assembles into grid
- Exports JSON frame data (compatible with Phaser / Unity / Godot formats)

**`card_composer` — Card Composition**
```bash
python3 -m game_asset_tools card_composer --template card_border.png --artwork char.png --title "Fire Mage" --output card.png --layout layout.yaml
```
- Places artwork into designated area, overlays border template
- Supports text rendering (title, description)

**`video_to_frames` — Video Frame Extraction**
```bash
python3 -m game_asset_tools video_to_frames --input anim.mp4 --fps 8 --output-dir ./frames/
```
- Extracts frames from AI-generated video at specified FPS
- Optional duplicate frame removal

**`tileset` — Tileset Assembly**
```bash
python3 -m game_asset_tools tileset --input-dir ./tiles/ --tile-size 32x32 --cols 8 --output tileset.png --seamless
```
- Assembles individual tiles into standard tileset image
- Outputs tile index information
- `--seamless` flag: enables edge blending to ensure tiles connect smoothly (see Seamless Tiling section)

### Dependencies (requirements.txt)

```
Pillow>=10.0
rembg>=2.0
opencv-python-headless>=4.8
numpy>=1.24
pyyaml>=6.0
```

## Style Consistency Management

### Three-Layer Style Control

```
Preset (base) → Reference Image (override) → Project Keywords (fine-tune)
```

**Layer 1: Built-in Presets**

| Preset | Prompt Keywords | Suitable For |
|--------|----------------|-------------|
| `pixel` | `pixel art, 16-bit style, clean pixels, no anti-aliasing` | Pixel art games |
| `anime` | `anime style, cel shading, vibrant colors, clean lines` | JRPG |
| `cel_shading` | `cel shaded, flat colors, bold outlines, cartoon style` | Cartoon style |
| `watercolor` | `watercolor painting, soft edges, muted colors` | Artistic games |
| `flat` | `flat design, minimal shading, solid colors, vector style` | UI / casual games |
| `realistic` | `semi-realistic, detailed rendering, painterly style` | Realistic card games |

**Layer 2: Reference Image Driven**

When `reference_image` is set in project config:
1. Use `blend_images` or `style_transfer` to infuse reference style into generated assets
2. Or append style description extracted by Claude from analyzing the reference image

**Layer 3: Project Keywords**

`keywords` and `palette` from project config are appended to every generation prompt.

### Prompt Construction

```
Final prompt = User description + Preset keywords + Project keywords + "color palette: #xxx, #xxx"
```

Example — user says "generate a healer character":
```
"A healer character holding a staff with glowing light,
 anime style, cel shading, vibrant colors, clean lines,
 fantasy theme, vibrant colors,
 color palette: #2C3E50, #E74C3C, #F39C12, #27AE60"
```

## Error Handling & Quality Assurance

### AI Generation Quality Control

```
Generate image → Show to user
    ├── Satisfied → Enter post-processing
    ├── Not satisfied → Options:
    │   ├── Regenerate (different seed)
    │   ├── Refine prompt (user adds description)
    │   ├── AI edit (local modification, e.g. "change sword to staff")
    │   └── Switch model (Gemini ↔ NanoBanana)
    └── Batch mode → Generate 2-3 options to choose from
```

### Post-Processing Error Handling

| Stage | Possible Issue | Solution |
|-------|---------------|----------|
| Background removal | Residual edges | Provide `--threshold` param; show result for user confirmation |
| Video frame extraction | Frames too similar or motion incoherent | Auto dedup + user can manually select frames to keep |
| Sprite sheet | Inconsistent frame sizes | Force normalize to config size, `contain` mode centered |
| Card composition | Artwork ratio doesn't match template area | Auto `cover` crop + user can adjust offset |

### Dependency Checking

Skill checks Python environment and dependencies on startup:
- Missing `rembg` → prompt user to `pip install`, or fallback to AI edit for background removal
- Missing `opencv` → video frame extraction unavailable, prompt to install

Missing dependencies do not block the entire skill — only disable the corresponding feature and inform the user.

## Character Consistency Strategy

Maintaining visual consistency across multiple AI generations is the hardest problem in game asset pipelines. The following strategies apply by asset workflow:

### Sprite Sheets (same character, multiple frames)

1. **Reference image first** — generate a single "hero" image of the character and get user approval
2. **Video-based frames** — use `image_to_video` with the hero image to generate motion, then extract frames. This naturally preserves character appearance
3. **Blend-based frames** — for per-frame generation, use `blend_images` with `maintain_character: true` (Gemini) to keep the hero image as reference for each frame
4. **Video continuation** — for long animations needing more than 10-15 seconds, use `continue_video` (Sora-2) to chain video segments seamlessly

### Icon Sets (multiple items, unified style)

1. Generate the first icon, confirm style with user
2. Use `style_transfer` from the approved icon to each subsequent generation
3. Apply palette enforcement in post-processing (see below)

### Card Sets (same character across cards)

1. Generate a character reference image first
2. Use `generate_with_character` (Sora-2) or `blend_images` with `maintain_character: true` for variant poses
3. Each variant goes through the card composition pipeline

### Batch Assets (e.g., full UI set)

1. Generate one reference asset per category, confirm with user
2. Use `style_transfer` to maintain consistency
3. Optional: post-processing palette enforcement maps generated colors to nearest project palette color

## Model Selection Strategy

### When to Use Which Model

| Scenario | Recommended Model | Reason |
|----------|------------------|--------|
| Style matches NanoBanana enum (`anime`, `ghibli`, `pixar`, `cyberpunk`, `fantasy`, `watercolor`, `sketch`, `oil_painting`) | NanoBanana | Native style support produces better results than prompt-only |
| High resolution needed (2K/4K) | NanoBanana | Supports up to 4K; Gemini does not |
| Free-form or unusual style (e.g., `pixel`, `cel_shading`, custom) | Gemini | Accepts free-text style parameter |
| Need uncommon aspect ratio (e.g., `21:9`, `5:4`) | NanoBanana | Supports 11 aspect ratios vs. Gemini's 5 |
| Character consistency via blending | Gemini | `maintain_character` flag in blend_images |
| User dissatisfied with first result | Switch to other | Different models produce different interpretations |

### Preset-to-Style Parameter Mapping

| Project Preset | NanoBanana `style` param | Gemini `style` param | Fallback |
|---------------|------------------------|---------------------|----------|
| `pixel` | — (not available) | `"pixel art"` | Prompt keywords only |
| `anime` | `"anime"` | `"anime"` | Either works |
| `cel_shading` | — (not available) | `"cel shading"` | Prompt keywords only |
| `watercolor` | `"watercolor"` | `"watercolor"` | Either works |
| `flat` | — (not available) | `"flat design"` | Prompt keywords only |
| `realistic` | — (not available) | `"semi-realistic"` | Prompt keywords only |

## Aspect Ratio & Size Mapping

MCP tools require aspect ratio parameters, not pixel dimensions. The skill derives the appropriate aspect ratio from the project config sizes, then resizes to exact dimensions in post-processing.

### Mapping Logic

1. Parse target size from config (e.g., `1920x1080` → `16:9`, `512` → `1:1`)
2. Find nearest supported aspect ratio for the chosen MCP tool
3. Generate at that aspect ratio
4. Python `resize` module crops/scales to exact target pixel dimensions

### Common Mappings

| Target Size | Derived Ratio | Nearest MCP Ratio |
|------------|--------------|-------------------|
| `NxN` (square) | 1:1 | 1:1 |
| `1920x1080` | 16:9 | 16:9 |
| `1280x720` | 16:9 | 16:9 |
| `750x1050` (card) | ~5:7 | 3:4 (closest) |
| `1080x1920` | 9:16 | 9:16 |

## Card Composition Details

### Text Rendering Configuration

Card text rendering is configured in the project YAML:

```yaml
assets:
  card:
    size: "750x1050"
    template: "templates/cards/default.png"
    layout:
      artwork: [50, 50, 650, 600]
      title: [50, 660, 650, 60]
      description: [50, 740, 650, 200]
    text:
      font: "templates/fonts/default.ttf"    # Font file path
      title_size: 28                          # Title font size (px)
      title_color: "#FFFFFF"                  # Title color
      desc_size: 16                           # Description font size (px)
      desc_color: "#CCCCCC"                   # Description color
      align: "center"                         # Text alignment: left / center / right
      overflow: "truncate"                    # Overflow handling: truncate / shrink / wrap
```

- Font files stored in `templates/fonts/`
- Supports TTF/OTF fonts
- `overflow: shrink` auto-reduces font size to fit; `wrap` wraps text to multiple lines

## Prompt Language Handling

The user interacts in Chinese, but some MCP tools (Veo) require English-only prompts. The skill handles this transparently:

1. User provides description in Chinese
2. Skill (Claude) translates to English internally when constructing the MCP prompt
3. Style preset keywords are always in English
4. Translation is automatic — user never needs to write English

## Temp File & Cleanup Management

### Intermediate File Storage

```
output/.tmp/                    # Temporary working directory
    ├── raw/                    # Raw AI-generated images (pre-processing)
    ├── frames/                 # Extracted video frames
    └── work/                   # In-progress compositions
```

### Cleanup Policy

- After successful pipeline completion: prompt user whether to keep or delete intermediate files
- Default: keep raw AI output (useful for re-processing), delete extracted frames and work files
- `--keep-temp` flag on Python CLI to override and keep everything
- `--clean` flag to force delete all temp files

## Output Naming

### Extended Naming Template

```yaml
output:
  naming: "{type}_{name}_{size}_{variant}"
```

Supported variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{type}` | Asset type | `char`, `bg`, `icon`, `card`, `sprite`, `tile` |
| `{name}` | Asset name (from user) | `fire_mage` |
| `{size}` | Output dimensions | `512`, `128x128` |
| `{variant}` | Auto-increment for variants | `v1`, `v2`, `v3` |
| `{timestamp}` | Generation timestamp | `20260326_143022` |
| `{action}` | Sprite action name | `idle`, `walk`, `attack` |

Examples:
- `char_fire_mage_512_v1.png`
- `icon_health_potion_64_v1.png`
- `sprite_warrior_walk_128x128.png` (sprite sheet)
- `card_fire_mage_750x1050_v1.png`

## Seamless Tiling

AI-generated tiles typically have edge discontinuities. The following strategies ensure seamless tiling:

### Generation Strategy

1. **Prompt engineering** — always include "seamless tileable texture, repeating pattern" in tile generation prompts
2. **Generate larger, crop center** — generate a 2x2 arrangement of the desired tile, then crop the center region where all four copies meet. This guarantees the edges match.

### Post-Processing (Python `tileset` module)

When `--seamless` is enabled:
1. **Edge mirror blending** — for each tile, blend a mirrored strip (configurable width, default 8px) along all four edges using alpha gradient
2. **Wrap-around validation** — tile the image 3x3 and present to user for visual confirmation of seamlessness
3. **Color correction** — ensure edge pixels match in hue/brightness to avoid visible seams

## UI Element Multi-State Generation

UI elements (buttons, toggles, sliders) require multiple visual states. The skill handles this as a guided sub-flow:

### Supported States

| Element | States |
|---------|--------|
| Button | `normal`, `hover`, `pressed`, `disabled` |
| Toggle | `on`, `off`, `on_hover`, `off_hover` |
| Checkbox | `unchecked`, `checked`, `unchecked_hover`, `checked_hover` |
| Tab | `active`, `inactive`, `hover` |

### Generation Flow

1. Generate the `normal` / base state first, confirm with user
2. Use AI edit to derive other states from the base:
   - `hover` — lighten colors, add subtle glow
   - `pressed` — darken colors, reduce size slightly or add inset shadow
   - `disabled` — desaturate, reduce opacity
3. Each state goes through the same post-processing pipeline (remove bg → resize)
4. Output all states with naming convention: `{name}_{state}.png` (e.g., `btn_attack_normal.png`, `btn_attack_hover.png`)

### Project Config Extension

```yaml
assets:
  ui:
    sizes: [64, 128]
    format: "png"
    transparent: true
    states: ["normal", "hover", "pressed", "disabled"]   # Which states to generate
```

## Generation Manifest (Traceability)

Every generation session produces a `manifest.json` in the output directory, recording full provenance for each asset:

```json
{
  "project": "my_game",
  "generated_at": "2026-03-26T14:30:22+08:00",
  "assets": [
    {
      "file": "characters/char_fire_mage_512_v1.png",
      "type": "character",
      "prompt": "A fire mage character with flowing red robes and a flame staff, anime style, cel shading, vibrant colors",
      "model": "mcp__grsai-nanobanana__generate_image",
      "style": "anime",
      "aspect_ratio": "1:1",
      "raw_file": ".tmp/raw/fire_mage_raw.png",
      "post_processing": ["remove_bg", "resize:512x512"],
      "project_config": "projects/my_game.yaml",
      "preset": "anime",
      "reference_image": null
    }
  ]
}
```

### Usage

- **Reproduce** — re-run the same prompt + model + params to generate a similar asset
- **Iterate** — tweak the recorded prompt and regenerate
- **Audit** — track which model and settings produced each asset
- Manifest is append-only within a session; each new session creates a new manifest or appends to the existing one

## Asset Preview

### In-Terminal Preview

After generating assets, the skill uses Claude Code's `Read` tool to display images directly in the terminal (Claude Code supports image rendering). For single assets this works well.

### Batch Preview via Browser

For batch generation (icon sets, UI state sets, sprite frames), a single-asset-at-a-time preview is impractical. The skill generates an HTML preview page:

```bash
python3 -m game_asset_tools preview --input-dir output/icons/ --output preview.html
```

The `preview` module:
1. Generates a self-contained HTML file with a grid layout of all generated assets
2. Shows filename, dimensions, and file size under each image
3. Groups by asset type or by generation batch
4. Opens in browser via `open preview.html` (macOS) for user review

### Preview in Guided Mode

In guided (step-by-step) mode, each asset is shown via `Read` tool immediately after generation, before proceeding to the next step. User confirms or requests changes before moving on.

## Default Font

The project includes a default free-for-commercial-use font for card text rendering:

### Bundled Font

- **Noto Sans SC** (Google Noto family) — supports CJK characters, free commercial license (OFL)
- Stored at `templates/fonts/NotoSansSC-Regular.ttf` and `templates/fonts/NotoSansSC-Bold.ttf`
- Used as fallback when project config does not specify a custom font

### Font Setup

```
templates/
└── fonts/
    ├── NotoSansSC-Regular.ttf    # Default font (bundled)
    ├── NotoSansSC-Bold.ttf       # Default bold font (bundled)
    └── custom/                    # User-provided fonts
```

The `card_composer` module resolves fonts in order:
1. Project config `text.font` path (if specified)
2. `templates/fonts/custom/` directory (user-provided)
3. `templates/fonts/NotoSansSC-Regular.ttf` (bundled default)

## Available MCP Tools

### Image Generation
- `mcp__gemini-image__generate_image` — Gemini AI, supports 5 aspect ratios and free-text styles
- `mcp__grsai-nanobanana__generate_image` — NanoBanana, 8 style enums, 11 aspect ratios, up to 4K

### Image Editing
- `mcp__gemini-image__edit_image` — Edit existing image with text instructions
- `mcp__grsai-nanobanana__edit_image` — NanoBanana edit

### Style Transfer
- `mcp__gemini-image__style_transfer` — Transfer style from reference image
- `mcp__grsai-nanobanana__style_transfer` — NanoBanana style transfer

### Image Blending
- `mcp__gemini-image__blend_images` — Blend 2-8 images, `maintain_character` flag for consistency
- `mcp__grsai-nanobanana__blend_images` — Blend 1-10 images

### Video Generation (for Sprite Sheet frame extraction)
- `mcp__grsai-sora2__generate_video` — Text to video (10-15s)
- `mcp__grsai-sora2__image_to_video` — Image to video, preserves character from source image
- `mcp__grsai-sora2__continue_video` — Extend existing video seamlessly via PID
- `mcp__grsai-sora2__generate_with_character` — Generate video with consistent character from reference
- `mcp__grsai-sora2__create_character` / `upload_character` — Create reusable character ID
- `mcp__grsai-veo__generate_video` — Veo text to video (English prompts only)

### Image Upload
- `mcp__imgbb__upload_image` — Upload to ImgBB for sharing

---

## Extract Mode: Design Image Layer Splitting & Slicing

### Overview

Extract Mode allows users to provide a design image (AI-generated UI mockup, designer PSD/PNG export, game screenshot, or reference image) and automatically split it into individual game-ready assets. Claude analyzes the image, identifies elements with layer relationships and shared components, then the Python toolkit slices and post-processes each element.

### Supported Input Sources

- AI-generated composite images (e.g., full UI screen mockup)
- Designer exports (Figma/Photoshop PNG exports)
- Game screenshots / reference images
- Any PNG/JPG image

### Layer Model

Design images have a natural layer hierarchy:

```
top:     UI elements (buttons, health bars, text labels, HUD)
middle:  Characters, items, effects
bottom:  Background scene
```

### Element Detection

Claude (multimodal) directly analyzes the image via Read tool and outputs a structured element list:

```json
{
  "source": "battle_ui_design.png",
  "source_size": [1920, 1080],
  "layers": {
    "bottom": [
      {
        "name": "battle_bg",
        "type": "background",
        "bbox": [0, 0, 1920, 1080],
        "description": "Forest battle scene background",
        "needs_inpaint": true,
        "inpaint_prompt": "Remove all UI elements and characters, fill with natural forest background"
      }
    ],
    "middle": [
      {
        "name": "player_char",
        "type": "character",
        "bbox": [100, 200, 500, 800],
        "description": "Player character warrior",
        "needs_remove_bg": true,
        "needs_trim": true,
        "trim_padding": 4
      }
    ],
    "top": [
      {
        "name": "skill_fireball",
        "type": "icon",
        "bbox": [100, 50, 164, 114],
        "needs_remove_bg": true,
        "needs_trim": true,
        "uses_shared": ["icon_frame"]
      },
      {
        "name": "skill_ice",
        "type": "icon",
        "bbox": [180, 50, 244, 114],
        "needs_remove_bg": true,
        "needs_trim": true,
        "uses_shared": ["icon_frame"]
      },
      {
        "name": "btn_attack",
        "type": "ui",
        "bbox": [200, 700, 400, 760],
        "needs_remove_bg": true,
        "uses_shared": ["btn_base"]
      }
    ]
  },
  "shared_assets": [
    {
      "name": "icon_frame",
      "type": "ui",
      "description": "Rounded square icon border frame, shared by all skill icons",
      "bbox": [100, 50, 164, 114],
      "extract_from": "skill_fireball",
      "reuse_count": 3
    },
    {
      "name": "btn_base",
      "type": "ui",
      "description": "Button base shape",
      "bbox": [200, 700, 400, 760],
      "extract_from": "btn_attack",
      "reuse_count": 2
    }
  ]
}
```

### Shared Asset Identification

| Type | Example | Handling |
|------|---------|----------|
| Shared border/frame | Skill icons all use same rounded frame | Extract once → `output/{type}/shared/` |
| Repeated component | Multiple buttons with same shape, different text | Extract base once, content separately |
| Nine-patch asset | Dialog box border, stretchable panel | Extract once, mark as nine-patch |
| Shared decoration | Dividers, badges, star icons | Extract once |

Shared assets are extracted only once and stored in `output/{type}/shared/`.

### Visual Confirmation Flow

After AI analysis, the skill generates an annotated preview image:

**Color coding:**
- Character → red solid border
- Icon → yellow solid border
- UI → blue solid border
- Background → green solid border
- Shared asset → purple dashed border + "shared x3" label

**Annotated preview shows:**
- Numbered colored rectangles on each detected element
- Label with: `#number type: name`
- Shared assets marked with dashed border and reuse count
- Overlapping regions shown with semi-transparent overlay

**User can then:**
- "删掉 3 号" — remove element
- "2 号名字改成 ice_arrow" — rename
- "1 号区域往右扩大 20px" — adjust bbox
- "4 号类型改成 ui" — reclassify
- "这三个图标共用一个边框" — add shared asset relationship
- "确认" — proceed to extraction

### Extraction Pipeline (Per Layer)

**Bottom layer (background):**
```
Option A: Direct crop (if no foreground obstruction)
Option B: AI inpaint — use mcp__gemini-image__edit_image to remove
          foreground elements and fill with background
```

**Middle layer (characters, items):**
```
Crop bbox (with padding) → rembg remove background → trim transparent edges → resize to project config sizes
```

**Top layer (UI, icons):**
```
Crop bbox (with padding) → rembg remove background → trim transparent edges → resize to project config sizes
```

**Shared assets:**
```
Extract once from first occurrence → same pipeline as its layer
→ store in output/{type}/shared/
```

### Irregular Shape Handling

Elements are NOT simply rectangular crops. The pipeline handles irregular shapes:

```
1. Rectangular crop with bbox + padding (extra margin around element)
2. rembg removes background → produces irregular alpha mask following actual element contour
3. trim removes surrounding transparent pixels → minimal bounding rectangle
4. Result: irregularly-shaped transparent PNG, not a simple rectangle
```

### New Python Modules

**`trim.py` — Transparent area trimming**
```bash
python3 -m game_asset_tools trim --input icon.png --output trimmed.png --padding 2
```
- Detect alpha channel, find minimal bounding rect of non-transparent pixels
- Crop surrounding fully-transparent area
- `--padding N` keeps N pixels of margin

**`annotate.py` — Annotated preview generation**
```bash
python3 -m game_asset_tools annotate --input design.png --elements elements.json --output annotated.png
```
- Draw colored bounding boxes on original image
- Color by type: character=red, icon=yellow, ui=blue, background=green, shared=purple dashed
- Label each with number, type, name
- Show shared asset reuse count

**`extract.py` — Batch element extraction**
```bash
python3 -m game_asset_tools extract \
  --input design.png \
  --elements elements.json \
  --output-dir output/ \
  --remove-bg \
  --trim \
  --project projects/my_game.yaml
```
- Read elements.json, process by layer
- Bottom: crop or flag for inpaint (inpaint done by skill via MCP)
- Middle/Top: crop → rembg → trim → resize per project config
- Shared assets: extract once → `output/{type}/shared/`
- Update manifest with all extracted assets
- Generate preview.html

### Updated Project Structure

```
game_asset_tools/
├── ... (existing modules)
├── trim.py              # Transparent area trimming
├── annotate.py          # Annotated preview generation
└── extract.py           # Batch element extraction

tests/
├── ... (existing tests)
├── test_trim.py
├── test_annotate.py
└── test_extract.py
```

### Skill Interaction Flow

```
1. User: "/game-asset 从这张图里提取素材" (provides image path)
2. Skill: Read image with Read tool (Claude analyzes visually)
3. Skill: Claude identifies elements, layers, shared assets → writes elements.json
4. Skill: Call `python3 -m game_asset_tools annotate` → generates annotated preview
5. Skill: Show annotated preview via Read tool, ask user to confirm
6. User: Adjusts (rename, delete, modify bbox, add shared relationships) or confirms
7. Skill: Update elements.json with user changes, re-annotate if needed
8. User: Confirms final element list
9. Skill: Call `python3 -m game_asset_tools extract` for middle/top layers
10. Skill: For bottom layer with needs_inpaint, call MCP edit_image
11. Skill: Show results via preview.html
12. User: Reviews extracted assets
```

### Error Handling

| Situation | Handling |
|-----------|----------|
| Missed element | User tells skill, Claude adds to elements.json |
| False detection | User says "delete #5", removed from list |
| Inaccurate bbox | User says "expand #3 left by 20px", skill adjusts coordinates and re-annotates |
| Wrong type | User says "#2 is icon not button", skill reclassifies |
| Undetected shared asset | User says "these 3 icons share same border", skill adds to shared_assets |
| rembg cut quality poor | Show individual result for confirmation, retry with adjusted bbox padding |
| Inpaint quality poor | Retry with different prompt or manual adjustment |
| Heavy overlap between elements | Show semi-transparent overlay in annotated preview, warn user |
| Low resolution element (<64x64) | Warn user extraction quality may be poor |

### Input Validation

- Supported formats: PNG, JPG, JPEG
- elements.json validation: bbox within image bounds, required fields present, valid type values
- Auto-create output directories if missing

## Asset Refinement (Post-Extraction Polish)

### Overview

After extraction, individual assets may need refinement: edge cleanup, content modification, missing part completion, or style unification. The skill supports two interaction modes for selecting which assets to refine.

### Refinement Types

| Type | Description | Method |
|------|-------------|--------|
| `edge_fix` | Edge artifacts, white fringe, jagged borders from rembg | Re-run rembg with adjusted parameters + trim with tighter padding |
| `ai_edit` | Content changes (color, details, modifications) | `mcp__gemini-image__edit_image` or `mcp__grsai-nanobanana__edit_image` with user description as prompt |
| `ai_inpaint` | Fill missing/occluded parts of an asset | `mcp__gemini-image__edit_image` with completion prompt: "Complete the missing [part]: [user note]" |
| `style_unify` | Make asset match project style | `mcp__gemini-image__style_transfer` or `mcp__grsai-nanobanana__style_transfer` with project reference image |

### Interaction Mode A: Terminal Dialog (Default)

The simpler and more reliable mode. Preview HTML shows all extracted assets with numbered labels. User tells skill what to refine in natural language:

```
Skill: 提取完成，共 12 个素材。请查看 preview.html，告诉我哪些需要精修。
User: #2 边缘有白边残留，#5 颜色改成红色，#7 右侧手臂被遮挡需要补全
Skill: 收到，开始精修 3 个素材...
  → #2: edge_fix (re-run rembg + trim)
  → #5: ai_edit ("change color to red")
  → #7: ai_inpaint ("complete the right arm that was occluded")
```

Each refinement result is shown via Read tool for user confirmation before saving.

### Interaction Mode B: Browser Interactive (For Large Batches)

Uses Chrome automation tools (`mcp__claude-in-chrome__*`) for richer interaction when there are many assets:

1. Skill generates interactive preview HTML with:
   - Clickable asset cards (click to select/deselect, highlighted border)
   - Refinement type selector (edge_fix / ai_edit / ai_inpaint / style_unify)
   - Notes input field per selected asset
   - "Submit" button that stores selections in a hidden DOM element

2. Skill opens the page in browser via Chrome tools

3. User interacts: selects assets, chooses refinement types, adds notes

4. Skill reads selections using `mcp__claude-in-chrome__javascript_tool` or `mcp__claude-in-chrome__get_page_text`:
   ```javascript
   // Read refinement tasks from page
   document.getElementById('refine-tasks-data').textContent
   ```

5. Skill parses the result and executes refinements

### Refinement Task Format

```json
{
  "tasks": [
    {
      "asset_id": 2,
      "file": "output/icons/icon_ice_128_v1.png",
      "name": "icon_ice",
      "type": "edge_fix",
      "note": "White fringe on edges"
    },
    {
      "asset_id": 5,
      "file": "output/ui/btn_attack_128_v1.png",
      "name": "btn_attack",
      "type": "ai_edit",
      "note": "Change color to red"
    },
    {
      "asset_id": 7,
      "file": "output/characters/char_warrior_512_v1.png",
      "name": "char_warrior",
      "type": "ai_inpaint",
      "note": "Complete the right arm that was occluded"
    }
  ]
}
```

### Refinement Pipeline

```
For each task:
    ├── Backup original → {filename}_backup.png
    ├── Execute refinement by type:
    │   ├── edge_fix:    rembg (higher threshold) → trim (tighter padding)
    │   ├── ai_edit:     MCP edit_image (user note as prompt)
    │   ├── ai_inpaint:  MCP edit_image ("complete/fill: {note}")
    │   └── style_unify: MCP style_transfer (project reference image)
    ├── Show result via Read tool
    ├── User confirms:
    │   ├── Satisfied → save, replace original
    │   └── Not satisfied → retry with adjusted params or different approach
    └── Update manifest (record refinement step)
```

### Mode Selection Logic

| Condition | Mode |
|-----------|------|
| Extracted assets ≤ 10 | Terminal dialog (Mode A) |
| Extracted assets > 10 | Offer browser interactive (Mode B via Asset Manager) |
| User preference | User can request either mode |
| Chrome tools unavailable | Fall back to Terminal dialog |

## Unified Asset Manager

### Overview

All asset viewing, refinement, and management operations are consolidated into a single `asset_manager.html` page. This replaces the previous separate `preview.html` and `interactive preview`. The Asset Manager is the central hub for all post-generation operations.

### Replaces

| Before | After |
|--------|-------|
| `preview.html` (static preview) | Merged into Asset Manager |
| `preview --interactive` (refinement selection) | Merged into Asset Manager |
| None | `asset_manager.html` — unified management panel |

### CLI

```bash
# Primary command
python3 -m game_asset_tools manager \
  --output-dir output/ \
  --manifest output/manifest.json \
  --output asset_manager.html

# Backward-compatible alias
python3 -m game_asset_tools preview --input-dir output/ --output preview.html
# internally redirects to manager
```

### Page Layout

```
┌─ Asset Manager: [Project Name] ──────────────────────────────────┐
│                                                                    │
│  ── 项目进度 ─────────────────────────────────────────            │
│  角色: 3/5 ██████░░░░ | 图标: 12/20 ████████████░░░░             │
│  UI: 2/8 █████░░░░░░ | 卡牌: 1/10 ██░░░░░░░░░░░░                │
│                                                                    │
│  筛选: [全部▾] [character] [icon] [ui] [card] [sprite] [tile]     │
│  排序: [时间▾] [类型] [名称]    搜索: [____________]              │
│                                                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │  🔥      │ │  ❄️  ☑  │ │  💚      │ │  ⚔️  ☑  │            │
│  │          │ │          │ │          │ │          │            │
│  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤            │
│  │ icon     │ │ icon     │ │ icon     │ │ char     │            │
│  │ fireball │ │ ice      │ │ healing  │ │ warrior  │            │
│  │ 128x128  │ │ 128x128  │ │ 128x128  │ │ 512x512  │            │
│  │ v2 (精修)│ │ v1       │ │ v1       │ │ v3       │            │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
│                                                                    │
│  ── 已选 2 个素材 ──────────────────────────                      │
│  操作:                                                             │
│  [边缘修复] [AI编辑] [AI补全] [风格统一] [删除] [重新分类]        │
│  备注: _______________________________________________             │
│  [提交操作]                    [导出选中] [全选] [取消]            │
│                                                                    │
│  ── 素材详情（点击卡片展开）──────────────                        │
│  文件: output/icons/icon_ice_128_v1.png                           │
│  Prompt: "An ice arrow spell icon..."                              │
│  模型: gemini  风格: anime  生成时间: 2026-03-26                  │
│  后处理: remove_bg → resize:128x128                               │
│  版本历史: v1(原始) → v2(边缘修复) → v3(调色)                    │
│  派生自: fire_mage_raw.png                                        │
│  被引用: card_fire_mage.png                                       │
│                                                                    │
│  <pre id="manager-tasks-data" style="display:none"></pre>         │
└────────────────────────────────────────────────────────────────────┘
```

### Features

| Feature | Description |
|---------|-------------|
| Filter | By asset type, keyword search |
| Sort | By time, type, name |
| Select | Click cards to select, multi-select supported |
| Detail view | Click to expand manifest provenance info + version history + relationships |
| Refinement | Select assets → choose refinement type → add notes → submit |
| Delete | Mark assets for deletion |
| Reclassify | Change asset type (e.g., icon → ui) |
| Export | Export selected assets to specified directory |
| Progress | Project completion overview at top |
| Version history | View/compare/rollback asset versions |
| Relationship | Show derivation chain and usage references |

### Skill Integration

```
Every asset operation → update manifest → regenerate asset_manager.html
```

- Quick Mode generates asset → update → regenerate
- Extract Mode extracts assets → update → regenerate
- Refinement completes → update → regenerate
- User opens asset_manager.html at any time → sees latest state

### Reading User Actions

Skill reads user submissions via Chrome automation:
```javascript
document.getElementById('manager-tasks-data').textContent
```

Or in Terminal mode, user describes actions in natural language.

## Asset Version History

### Overview

Every asset maintains a version chain. Refinements create new versions rather than overwriting. Users can compare versions and rollback.

### Version Storage

```
output/characters/
├── char_fire_mage_512_v1.png          # Current (latest)
├── .versions/
│   └── char_fire_mage_512/
│       ├── v1.png                      # Original
│       ├── v2.png                      # After edge_fix
│       ├── v3.png                      # After color edit (current)
│       └── history.json                # Version metadata
```

### history.json

```json
{
  "asset": "char_fire_mage_512",
  "current_version": 3,
  "versions": [
    {
      "version": 1,
      "timestamp": "2026-03-26T14:30:00+08:00",
      "action": "generated",
      "prompt": "A fire mage character...",
      "model": "gemini"
    },
    {
      "version": 2,
      "timestamp": "2026-03-26T14:35:00+08:00",
      "action": "edge_fix",
      "note": "Remove white fringe"
    },
    {
      "version": 3,
      "timestamp": "2026-03-26T14:40:00+08:00",
      "action": "ai_edit",
      "note": "Make robes darker red"
    }
  ]
}
```

### Operations

| Operation | Description |
|-----------|-------------|
| Compare | Show two versions side-by-side in manager page |
| Rollback | Restore a previous version as current |
| Branch | Create alternative refinement from an older version |

### Python Module

**`version.py`** — asset version management:
```bash
python3 -m game_asset_tools version save --asset output/characters/char_mage_512.png --action "edge_fix" --note "Remove fringe"
python3 -m game_asset_tools version list --asset output/characters/char_mage_512.png
python3 -m game_asset_tools version rollback --asset output/characters/char_mage_512.png --to 1
python3 -m game_asset_tools version compare --asset output/characters/char_mage_512.png --v1 1 --v2 3 --output compare.png
```

## Asset Relationship Graph

### Overview

Assets have derivation and usage relationships. The manifest tracks these for traceability and impact analysis.

### Relationship Types

| Relationship | Example |
|-------------|---------|
| `derived_from` | `char_fire_mage_512.png` derived from `fire_mage_raw.png` |
| `used_by` | `char_fire_mage_512.png` used by `card_fire_mage.png` |
| `extracted_from` | `icon_fireball.png` extracted from `battle_ui_design.png` |
| `shares_asset` | `icon_fireball.png` shares `icon_frame.png` with `icon_ice.png` |

### Manifest Extension

```json
{
  "file": "characters/char_fire_mage_512_v1.png",
  "type": "character",
  "relationships": {
    "derived_from": ".tmp/raw/fire_mage_raw.png",
    "used_by": ["cards/card_fire_mage.png", "sprites/sprite_fire_mage.png"]
  }
}
```

### Manager Display

In the asset detail panel, show:
- **来源**: click to navigate to parent asset
- **被引用**: list of assets that use this one
- **影响分析**: if this asset is modified, which downstream assets are affected

## Engine Export

### Overview

One-command export restructures assets into the target game engine's standard resource layout.

```bash
python3 -m game_asset_tools export \
  --engine unity \
  --input-dir output/ \
  --export-dir ./unity_export/
```

### Supported Engines

**Unity:**
```
unity_export/
├── Assets/
│   ├── Sprites/
│   │   ├── Characters/
│   │   └── Icons/
│   ├── UI/
│   ├── Backgrounds/
│   └── Tilesets/
```
- Generates `.meta` stub files for each asset
- Sprite sheets get TexturePacker-compatible import settings

**Godot:**
```
godot_export/
├── assets/
│   ├── characters/
│   ├── icons/
│   ├── ui/
│   └── tilesets/
├── .import/
```
- Generates `.import` files for each asset
- Tilesets formatted for Godot TileMap

**Cocos:**
```
cocos_export/
├── assets/
│   ├── sprites/
│   ├── ui/
│   └── backgrounds/
```
- Generates `.meta` files per Cocos Creator convention

**Web (Generic):**
```
web_export/
├── images/
│   ├── characters/
│   ├── icons/
│   └── ui/
├── spritesheets/
│   ├── sheet.png
│   └── sheet.json
└── manifest.json
```

### Python Module

**`export.py`**:
```bash
python3 -m game_asset_tools export --engine unity --input-dir output/ --export-dir ./build/
python3 -m game_asset_tools export --engine godot --input-dir output/ --export-dir ./build/
python3 -m game_asset_tools export --engine web --input-dir output/ --export-dir ./build/
```

## Texture Atlas Packing

### Overview

Pack multiple small assets into optimized texture atlases to reduce draw calls at runtime.

```bash
python3 -m game_asset_tools atlas \
  --input-dir output/icons/ \
  --output atlas.png \
  --meta atlas.json \
  --max-size 2048x2048 \
  --padding 2 \
  --format phaser
```

### Packing Algorithm

- Rectangle bin-packing (shelf or maxrects algorithm via Pillow)
- Respects `--max-size` constraint
- `--padding` adds pixel spacing between packed assets (prevents texture bleeding)
- If assets don't fit in one atlas, generates multiple: `atlas_0.png`, `atlas_1.png`, ...

### Output Metadata Formats

| Format | Engine |
|--------|--------|
| `phaser` | Phaser TexturePacker JSON |
| `unity` | Unity sprite atlas manifest |
| `godot` | Godot AtlasTexture resource |
| `generic` | Simple JSON with coordinates |

### Example Output (generic format)

```json
{
  "atlases": [
    {
      "image": "atlas_0.png",
      "size": {"w": 2048, "h": 1024},
      "sprites": [
        {"name": "icon_fireball", "x": 0, "y": 0, "w": 128, "h": 128},
        {"name": "icon_ice", "x": 130, "y": 0, "w": 128, "h": 128},
        {"name": "icon_healing", "x": 260, "y": 0, "w": 128, "h": 128}
      ]
    }
  ]
}
```

### Python Module

**`atlas.py`**:
- Bin-packing implementation using shelf-first-fit algorithm
- Supports multiple atlas pages
- Metadata export in multiple formats

## Project Progress Dashboard

### Overview

Track asset completion status against a requirements checklist defined in the project config.

### Project Config Extension

```yaml
# projects/my_game.yaml (add requirements section)
requirements:
  characters:
    - name: "fire_mage"
      description: "Fire mage hero character"
      sizes: [512, 1024]
    - name: "ice_archer"
      description: "Ice archer character"
      sizes: [512, 1024]
    - name: "healer"
      description: "Healer support character"
      sizes: [512, 1024]
  icons:
    - name: "fireball"
    - name: "ice_arrow"
    - name: "healing"
    - name: "shield"
    - name: "poison"
  ui:
    - name: "btn_attack"
      states: ["normal", "hover", "pressed", "disabled"]
    - name: "btn_defend"
      states: ["normal", "hover", "pressed", "disabled"]
    - name: "health_bar"
    - name: "mana_bar"
  cards:
    - name: "fire_mage_card"
    - name: "ice_archer_card"
```

### Matching Logic

The manager scans existing assets in `output/` and matches against requirements:
- Match by name substring (e.g., `char_fire_mage_512_v1.png` matches requirement `fire_mage`)
- Track which sizes/states are complete
- Missing assets highlighted in the dashboard

### Dashboard Display (top of Asset Manager)

```
── 项目进度: Example RPG ──────────────────────────
角色:  3/3 ████████████████████ 100%  ✅
图标:  3/5 ████████████░░░░░░░░  60%
UI:    2/8 █████░░░░░░░░░░░░░░░  25%
卡牌:  1/2 ██████████░░░░░░░░░░  50%
精灵图: 0/1 ░░░░░░░░░░░░░░░░░░░░   0%

缺失清单:
  - icon: shield, poison
  - ui: btn_defend (4 states), health_bar, mana_bar
  - card: ice_archer_card
  - sprite: fire_mage_walk
```

### Skill Integration

Skill can proactively suggest next steps:
```
"项目还缺 2 个图标（shield, poison）、6 个 UI 元素、1 张卡牌。要继续生成吗？"
```

## Updated Project Structure (Final)

```
game_asset_tools/
├── __init__.py
├── __main__.py
├── cli.py                # CLI dispatcher (updated with new commands)
├── config.py             # Project config loader
├── naming.py             # Output naming engine
├── manifest.py           # Generation manifest (extended with relationships)
├── remove_bg.py          # Background removal
├── resize.py             # Resize / crop / pad
├── trim.py               # NEW: Transparent area trimming
├── sprite_sheet.py       # Sprite sheet assembly
├── card_composer.py      # Card composition
├── video_to_frames.py    # Video frame extraction
├── tileset.py            # Tileset assembly
├── annotate.py           # NEW: Annotated preview generation
├── extract.py            # NEW: Batch element extraction
├── version.py            # NEW: Asset version management
├── export.py             # NEW: Engine-specific export
├── atlas.py              # NEW: Texture atlas packing
├── manager.py            # NEW: Asset manager HTML generation (replaces preview.py)
└── preview.py            # Deprecated: redirects to manager.py
```
