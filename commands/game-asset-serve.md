---
name: game-asset-serve
description: Start/stop the asset manager web service — FastAPI backend + React frontend.
---

# Asset Manager Web Service

## Start

```bash
# Start backend (port 8080)
cd ${CLAUDE_PLUGIN_ROOT:-/Users/lanjinmin/Workspace/ClaudeCodeSpace/GameAssetDesign}
uvicorn server.main:app --reload --port 8080 &

# Start frontend (port 5173)
cd web && npm run dev &
```

Then open: http://localhost:5173

## Start with Gemini API (for AI features)

```bash
GEMINI_API_KEY=your_key uvicorn server.main:app --reload --port 8080 &
cd web && npm run dev &
```

## Stop

```bash
# Stop backend
pkill -f "uvicorn server.main:app"

# Stop frontend
pkill -f "vite"
```

## Status

```bash
# Check if services are running
curl -s http://localhost:8080/api/health 2>/dev/null && echo "Backend: running" || echo "Backend: stopped"
curl -s http://localhost:5173 >/dev/null 2>&1 && echo "Frontend: running" || echo "Frontend: stopped"
```

## URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | React asset manager UI |
| Backend API | http://localhost:8080/api | REST API |
| API Docs | http://localhost:8080/docs | Swagger interactive docs |
| WebSocket | ws://localhost:8080/ws | Real-time updates |
| Static Files | http://localhost:8080/output/ | Asset images |
