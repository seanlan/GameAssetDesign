#!/bin/bash
# game-asset-design init — Setup commands and skills in current project
# Usage: bash /path/to/GameAssetDesign/scripts/init.sh [project_dir]

set -e

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_DIR="${1:-.}"
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"

echo "🎮 Game Asset Design — Initializing project"
echo "   Plugin: $PLUGIN_ROOT"
echo "   Project: $PROJECT_DIR"
echo ""

# 1. Create .claude/commands/ and copy command files
echo "📋 Installing commands..."
mkdir -p "$PROJECT_DIR/.claude/commands"
cp "$PLUGIN_ROOT/commands/"*.md "$PROJECT_DIR/.claude/commands/"
echo "   Copied $(ls "$PROJECT_DIR/.claude/commands/" | wc -l | tr -d ' ') commands to .claude/commands/"

# 2. Create .claude/skills/ and copy skill files + data
echo "📋 Installing skills..."
mkdir -p "$PROJECT_DIR/.claude/skills/game-asset/data"
cp "$PLUGIN_ROOT/skills/game-asset/SKILL.md" "$PROJECT_DIR/.claude/skills/game-asset/"
cp "$PLUGIN_ROOT/skills/game-asset/data/"*.csv "$PROJECT_DIR/.claude/skills/game-asset/data/"
echo "   Copied skill + $(ls "$PROJECT_DIR/.claude/skills/game-asset/data/" | wc -l | tr -d ' ') data files"

# 3. Create output directories
echo "📁 Creating output directories..."
mkdir -p "$PROJECT_DIR/output"/{characters,backgrounds,ui,cards,icons,sprites,tilesets}

# 4. Create templates directory
mkdir -p "$PROJECT_DIR/templates"/{cards,ui,fonts/custom}

# 5. Install Python dependencies
echo "📦 Checking Python dependencies..."
if ! python3 -c "from PIL import Image" 2>/dev/null; then
    echo "   Installing dependencies..."
    pip3 install -q -r "$PLUGIN_ROOT/requirements.txt"
else
    echo "   Dependencies OK"
fi

# 6. Setup PYTHONPATH in .claude/settings.json (so game_asset_tools is importable)
SETTINGS_FILE="$PROJECT_DIR/.claude/settings.json"
if [ ! -f "$SETTINGS_FILE" ]; then
    echo "{}" > "$SETTINGS_FILE"
fi
python3 -c "
import json, os
settings_path = '$SETTINGS_FILE'
plugin_root = '$PLUGIN_ROOT'
with open(settings_path) as f:
    settings = json.load(f)
env = settings.get('env', {})
pythonpath = env.get('PYTHONPATH', '')
if plugin_root not in pythonpath:
    env['PYTHONPATH'] = f'{plugin_root}:{pythonpath}' if pythonpath else plugin_root
    settings['env'] = env
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)
    print('   PYTHONPATH configured in .claude/settings.json')
else:
    print('   PYTHONPATH already configured')
"

# 7. Download default font if not present
FONT_PATH="$PROJECT_DIR/templates/fonts/NotoSansSC-Regular.ttf"
if [ ! -f "$FONT_PATH" ]; then
    echo "📦 Downloading default font..."
    curl -sL -o "$FONT_PATH" "https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf" 2>/dev/null
    [ -f "$FONT_PATH" ] && echo "   Font downloaded" || echo "   ⚠️ Font download failed (optional)"
fi

echo ""
echo "✅ Game Asset Design initialized!"
echo ""
echo "Available commands:"
echo "   /game-asset:init      — Create project config (style, engine)"
echo "   /game-asset:generate  — Generate new assets with AI"
echo "   /game-asset:analyze   — Analyze design image"
echo "   /game-asset:extract   — Extract assets from design"
echo "   /game-asset:refine    — Refine/polish assets"
echo "   /game-asset:manage    — Open asset manager"
echo "   /game-asset:serve     — Start web management service"
echo "   /game-asset:version   — Version management"
echo "   /game-asset:export    — Export for game engines"
echo "   /game-asset:atlas     — Texture atlas packing"
echo ""
echo "Start with: /game-asset:init"
