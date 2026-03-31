"""Project config and progress API."""

import os
import glob
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from server.services.asset_service import AssetService

router = APIRouter(tags=["project"])
service = AssetService()


@router.get("/project")
async def get_project():
    """Get current project config."""
    config = service.get_project_config()
    if not config:
        return {"configured": False, "message": "No project config found. Use /game-asset:init"}
    return {"configured": True, "config": config}


@router.get("/project/list")
async def list_projects():
    """List all available project configs."""
    projects_dir = os.path.join(service.project_root, "projects")
    if not os.path.isdir(projects_dir):
        return {"projects": []}
    files = glob.glob(os.path.join(projects_dir, "*.yaml")) + glob.glob(os.path.join(projects_dir, "*.yml"))
    names = [os.path.splitext(os.path.basename(f))[0] for f in files]
    return {"projects": names}


@router.get("/progress")
async def get_progress():
    """Get project completion progress."""
    config = service.get_project_config()
    if not config:
        return {"configured": False}

    from game_asset_tools.config import get_requirements, check_progress
    reqs = get_requirements(config)
    if not reqs:
        return {"configured": True, "has_requirements": False}

    progress = check_progress(reqs, service.output_dir)
    return {"configured": True, "has_requirements": True, "progress": progress}


@router.get("/templates")
async def get_templates():
    """Get asset generation templates from project config."""
    config = service.get_project_config()
    if not config:
        return {"templates": []}
    from game_asset_tools.config import get_templates
    return {"templates": get_templates(config)}
