"""Asset CRUD API endpoints."""

import os
import json
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from server.services.asset_service import AssetService

router = APIRouter(tags=["assets"])
service = AssetService()


class AssetUpdate(BaseModel):
    name: str | None = None
    type: str | None = None


@router.get("/assets")
async def list_assets(
    type: str | None = Query(None, description="Filter by asset type"),
    search: str | None = Query(None, description="Search by name"),
    sort: str = Query("time", description="Sort by: time, type, name"),
):
    """List all assets with optional filtering and sorting."""
    assets = service.list_assets()

    if type:
        assets = [a for a in assets if a["type"] == type]
    if search:
        q = search.lower()
        assets = [a for a in assets if q in a.get("filename", "").lower() or q in a.get("prompt", "").lower()]

    if sort == "type":
        assets.sort(key=lambda a: a.get("type", ""))
    elif sort == "name":
        assets.sort(key=lambda a: a.get("filename", ""))
    else:
        assets.sort(key=lambda a: a.get("generated_at", ""), reverse=True)

    return {"assets": assets, "total": len(assets)}


@router.get("/assets/{name}")
async def get_asset(name: str):
    """Get asset details including manifest metadata."""
    asset = service.get_asset(name)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset '{name}' not found")
    return asset


@router.get("/assets/{name}/image")
async def get_asset_image(name: str):
    """Get the asset image file."""
    path = service.get_asset_path(name)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Image not found for '{name}'")
    return FileResponse(path, media_type="image/png")


@router.put("/assets/{name}")
async def update_asset(name: str, update: AssetUpdate):
    """Update asset metadata (rename, reclassify)."""
    result = service.update_asset(name, update.model_dump(exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail=f"Asset '{name}' not found")
    return result


@router.delete("/assets/{name}")
async def delete_asset(name: str):
    """Delete an asset."""
    ok = service.delete_asset(name)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Asset '{name}' not found")
    return {"deleted": name}


@router.get("/assets/{name}/versions")
async def list_versions(name: str):
    """Get version history for an asset."""
    versions = service.list_versions(name)
    if versions is None:
        raise HTTPException(status_code=404, detail=f"Asset '{name}' not found")
    return {"versions": versions}


@router.post("/assets/{name}/versions/rollback")
async def rollback_version(name: str, version: int = Query(...)):
    """Rollback asset to a previous version."""
    ok = service.rollback(name, version)
    if not ok:
        raise HTTPException(status_code=400, detail=f"Cannot rollback '{name}' to v{version}")
    return {"rolled_back_to": version}


@router.post("/assets/{name}/versions/compare")
async def compare_versions(name: str, v1: int = Query(...), v2: int = Query(...)):
    """Generate side-by-side comparison of two versions."""
    path = service.compare_versions(name, v1, v2)
    if not path:
        raise HTTPException(status_code=400, detail="Cannot generate comparison")
    return FileResponse(path, media_type="image/png")
