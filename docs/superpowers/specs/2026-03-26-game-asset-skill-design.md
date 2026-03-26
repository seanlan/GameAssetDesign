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
