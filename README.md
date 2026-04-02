# Game Asset Design

A Claude Code plugin for generating, extracting, and managing 2D game assets. Combines AI image generation (Gemini) with a Python post-processing toolkit and a web-based asset manager.

## Install

```bash
claude plugin add github:lanjinmin/GameAssetDesign
```

Or manually:

```bash
git clone https://github.com/lanjinmin/GameAssetDesign.git
cd GameAssetDesign
pip3 install -r requirements.txt
```

## Requirements

- Python 3.10+
- Node.js 18+ (for web UI)
- Claude Code
- `gemini-image` MCP server (for AI generation/editing via Claude Code)
- `GEMINI_API_KEY` env var (for web service AI features)

## Commands

| Command | Description |
|---------|-------------|
| `/game-asset:init` | Initialize project config (style, engine, requirements) |
| `/game-asset:generate` | Generate new assets with AI (characters, icons, UI, cards, sprites, tilesets) |
| `/game-asset:analyze` | Analyze design image — identify elements, calibrate bounding boxes |
| `/game-asset:extract` | Extract assets — crop, AI chroma key refine, remove background |
| `/game-asset:manage` | Open asset manager (static HTML) |
| `/game-asset:serve` | Start/stop web service (FastAPI + React) |
| `/game-asset:refine` | Refine assets — edge fix, AI edit, inpaint, style unify |
| `/game-asset:version` | Version management — history, rollback, compare |
| `/game-asset:export` | Export for game engines — Unity, Godot, Cocos, Web |
| `/game-asset:atlas` | Texture atlas packing |

## Workflows

### Generate from scratch

```
/game-asset:init → /game-asset:generate → /game-asset:serve → /game-asset:refine → /game-asset:export
```

### Extract from design image

```
/game-asset:init → /game-asset:analyze → /game-asset:extract → /game-asset:serve → /game-asset:refine → /game-asset:export
```

## Web Asset Manager

Full-featured web UI for browsing, refining, and exporting assets.

```bash
# Start backend + frontend
GEMINI_API_KEY=your_key uvicorn server.main:app --reload --port 8080 &
cd web && npm install && npm run dev &

# Open http://localhost:5173
```

Features:
- Asset grid with thumbnails, filtering, sorting, search
- Detail panel with metadata, version history, rollback
- Batch operations: refine, delete, reclassify, export, atlas
- AI operations: generate, edit, inpaint (via Gemini API)
- Project progress dashboard
- Real-time updates via WebSocket

### API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/assets` | List assets (filter, sort, search) |
| GET | `/api/assets/:name` | Asset details |
| PUT | `/api/assets/:name` | Rename / reclassify |
| DELETE | `/api/assets/:name` | Delete asset |
| GET | `/api/assets/:name/versions` | Version history |
| POST | `/api/assets/:name/versions/rollback` | Rollback |
| POST | `/api/generate` | AI generate |
| POST | `/api/analyze` | Analyze design image |
| POST | `/api/extract` | Extract elements |
| POST | `/api/refine` | Refine asset |
| POST | `/api/export` | Engine export |
| POST | `/api/atlas` | Atlas packing |
| GET | `/api/progress` | Project progress |
| WS | `/ws` | Real-time updates |

Full Swagger docs at http://localhost:8080/docs

## Python CLI

```bash
python3 -m game_asset_tools --help
```

19 commands:

| Command | Description |
|---------|-------------|
| `resize` | Resize/crop (contain, cover, stretch) |
| `remove_bg` | Background removal (rembg) |
| `trim` | Trim transparent edges |
| `sprite_sheet` | Sprite sheet assembly + metadata |
| `card_composer` | Card composition + text rendering |
| `video_to_frames` | Video frame extraction + dedup |
| `tileset` | Tileset assembly + seamless blending |
| `annotate` | Draw element detection boxes |
| `extract` | Batch extract from design image |
| `version` | Version management (save/list/rollback/compare) |
| `manager` | Generate asset manager HTML |
| `atlas` | Texture atlas packing |
| `export` | Engine export (Unity/Godot/Cocos/Web) |
| `preview` | Asset preview page |
| `chromakey` | Remove chroma key background (green/magenta) |
| `pipeline` | One-step: auto-detect → extract → chromakey → trim |
| `nine_slice` | 9-slice an image for scalable UI |
| `style_unify` | Show project style keywords for batch consistency |
| `auto_detect` | Auto-detect UI elements in a design image |

## Knowledge Base

Structured data in `skills/game-asset/data/` drives all generation and processing decisions:

| File | Description |
|------|-------------|
| `asset_types.csv` | 7 asset types: sizes, aspect ratios, transparency, output dirs, prompt suffixes |
| `pipelines.csv` | 30+ step-by-step processing rules per asset type with priority levels |
| `styles.csv` | 9 style presets: NanoBanana/Gemini params, chroma key color selection |
| `rules.csv` | 18 decision rules (priority 1-8): quality, bg removal, bbox, style, workflow |
| `prompt_templates.csv` | 14 reusable prompt templates with negative prompts and usage notes |

## Reference Image

Set a global style reference in `game-assets.yaml`:

```yaml
style:
  reference_image: "path/to/design_mockup.png"
```

All generated assets will match the visual style of this reference image. Use a complete design mockup (like a game screenshot with UI) to define the art direction.

## Architecture

```
┌─────────────────────┐     ┌──────────────────┐
│  React Frontend     │────→│  FastAPI Backend  │────→ game_asset_tools (Python)
│  localhost:5173     │←────│  localhost:8080   │────→ Gemini API
│  (Vite + React TS)  │ WS  │  (22 API routes)  │────→ output/
└─────────────────────┘     └──────────────────┘

┌─────────────────────┐
│  Claude Code        │────→ game_asset_tools (Python)
│  /game-asset:*      │────→ MCP gemini-image
│  (10 commands)      │
└─────────────────────┘
```

## Key Design Decisions

**Chroma key background removal**: AI replaces background with green (#00FF00) or magenta (#FF00FF) — never white (blends with highlights). Python removes the chroma key color by distance calculation + despill correction. rembg only for simple shapes (buttons).

**Design image extraction pipeline**: `Analyze (bbox calibration) → Crop → AI refine (chroma key bg) → Remove background`. Claude's visual bbox estimation has 20-50px error — pixel-level color scanning calibrates boundaries.

**Icon border/content separation**: Shared borders extracted once (AI fills center with magenta → Python removes). Content keeps its background plate (AI removes border, extends fill). Game engine composites at runtime.

## Project Structure

```
.claude-plugin/          — Plugin metadata
commands/                — 10 slash commands
skills/game-asset/       — Skill routing entry
server/                  — FastAPI backend
  api/                   — REST API routes
  services/              — Business logic + AI service
web/                     — React frontend (Vite + TypeScript)
  src/components/        — UI components
  src/hooks/             — WebSocket hook
game_asset_tools/        — Python toolkit (19 commands, 16 modules)
game-assets.yaml         — Project config (created by /game-asset:init)
templates/               — Card templates, fonts
output/                  — Asset output
tests/                   — 160+ tests
```

## License

MIT
