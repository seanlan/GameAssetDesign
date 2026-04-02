#!/bin/bash
# Session start hook — setup Python environment for game-asset-tools
PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Add plugin to PYTHONPATH so game_asset_tools is importable
export PYTHONPATH="${PLUGIN_ROOT}:${PYTHONPATH}"

# Check if dependencies are installed
if ! python3 -c "from PIL import Image" 2>/dev/null; then
    pip3 install -q -r "${PLUGIN_ROOT}/requirements.txt" 2>/dev/null
fi
