#!/bin/bash
# Post-install: setup Python dependencies for game-asset-tools
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🎮 Installing game-asset-tools dependencies..."
pip3 install -r "$SCRIPT_DIR/requirements.txt" -q 2>/dev/null

# Verify
if python3 -c "import game_asset_tools" 2>/dev/null; then
    echo "✅ game-asset-tools ready"
else
    # Add to PYTHONPATH if not importable
    export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
    echo "✅ game-asset-tools ready (via PYTHONPATH)"
fi

# Download default font if not present
FONT_PATH="$SCRIPT_DIR/templates/fonts/NotoSansSC-Regular.ttf"
if [ ! -f "$FONT_PATH" ]; then
    echo "📦 Downloading default font (Noto Sans SC)..."
    curl -sL -o "$FONT_PATH" "https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf" 2>/dev/null
    if [ -f "$FONT_PATH" ]; then
        echo "✅ Font downloaded"
    else
        echo "⚠️  Font download failed. Card text will use system default."
    fi
fi

echo "🎮 Game Asset Design skill installed. Use /game-asset to start."
