"""Game Asset Design — FastAPI server."""

import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add project root to path so game_asset_tools is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from server.api.assets import router as assets_router
from server.api.operations import router as operations_router
from server.api.project import router as project_router
from server.api.ws import router as ws_router

app = FastAPI(
    title="Game Asset Design",
    description="API for managing 2D game assets",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assets_router, prefix="/api")
app.include_router(operations_router, prefix="/api")
app.include_router(project_router, prefix="/api")
app.include_router(ws_router)

# Serve output images as static files
output_dir = os.path.join(PROJECT_ROOT, "output")
if os.path.isdir(output_dir):
    app.mount("/output", StaticFiles(directory=output_dir), name="output")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
