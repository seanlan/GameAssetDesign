---
name: game-asset-serve
description: Start the asset manager web service — browse, filter, and manage assets in browser.
---

# Asset Manager Web Service

## Start

Start the web service from the user's project directory. The server manages assets in the **current working directory**.

```bash
# Set Python path to plugin root
export PYTHONPATH="${CLAUDE_PLUGIN_ROOT}:$PYTHONPATH"

# Build frontend if not built yet
if [ ! -d "${CLAUDE_PLUGIN_ROOT}/web/dist" ]; then
    cd "${CLAUDE_PLUGIN_ROOT}/web" && npm install && npm run build
    cd -
fi

# Start server (serves API + React frontend)
python3 -m uvicorn server.main:app --port 8080 --app-dir "${CLAUDE_PLUGIN_ROOT}"
```

Then open: http://localhost:8080

## Stop

```bash
pkill -f "uvicorn server.main:app"
```

## What the service provides

- Browse all assets in `output/` with thumbnails
- Filter by type, search by name, sort
- View asset details: prompt, model, dimensions, version history
- Select assets for batch operations (export, atlas, delete)
- Upload design images for analysis (if GEMINI_API_KEY is set)
- Project progress dashboard

## URLs

| URL | Description |
|-----|-------------|
| http://localhost:8080 | Asset manager UI |
| http://localhost:8080/docs | Swagger API docs |
| http://localhost:8080/api/health | Health check |
