"""AI operations API — generate, analyze, extract, refine, export, atlas."""

import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from server.services.asset_service import AssetService
from server.services.ai_service import AIService
from server.services.ws_manager import manager as ws_manager

router = APIRouter(tags=["operations"])
asset_service = AssetService()
ai_service = AIService()


class GenerateRequest(BaseModel):
    description: str
    type: str = "character"
    style: str | None = None


class RefineRequest(BaseModel):
    asset_name: str
    refine_type: str  # edge_fix, ai_edit, ai_inpaint, style_unify
    note: str = ""


class ExportRequest(BaseModel):
    engine: str  # unity, godot, cocos, web


class AtlasRequest(BaseModel):
    input_type: str = "icons"  # which asset type to pack
    max_size: str = "2048x2048"
    padding: int = 2
    format: str = "generic"


@router.post("/generate")
async def generate_asset(req: GenerateRequest):
    """Generate a new asset with AI."""
    try:
        await ws_manager.broadcast({"event": "task_start", "task": "generate", "description": req.description})

        result = await ai_service.generate_image(
            description=req.description,
            asset_type=req.type,
            style=req.style,
        )

        await ws_manager.broadcast({"event": "task_complete", "task": "generate", "result": result})
        return result

    except Exception as e:
        await ws_manager.broadcast({"event": "task_error", "task": "generate", "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_image(
    image: UploadFile = File(...),
):
    """Analyze a design image — identify elements, generate annotated preview."""
    try:
        await ws_manager.broadcast({"event": "task_start", "task": "analyze"})

        # Save uploaded file
        upload_dir = asset_service.tmp_dir
        os.makedirs(upload_dir, exist_ok=True)
        upload_path = os.path.join(upload_dir, image.filename or "design.png")
        content = await image.read()
        with open(upload_path, "wb") as f:
            f.write(content)

        result = await ai_service.analyze_design(upload_path)
        await ws_manager.broadcast({"event": "task_complete", "task": "analyze", "result": result})
        return result

    except Exception as e:
        await ws_manager.broadcast({"event": "task_error", "task": "analyze", "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract")
async def extract_assets(
    elements_path: str = Form(None),
):
    """Extract assets from design image using elements.json."""
    try:
        await ws_manager.broadcast({"event": "task_start", "task": "extract"})

        path = elements_path or os.path.join(asset_service.tmp_dir, "elements.json")
        result = asset_service.extract_from_elements(path)

        await ws_manager.broadcast({"event": "task_complete", "task": "extract", "result": result})
        return result

    except Exception as e:
        await ws_manager.broadcast({"event": "task_error", "task": "extract", "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refine")
async def refine_asset(req: RefineRequest):
    """Refine an asset — edge fix, AI edit, inpaint, style unify."""
    try:
        await ws_manager.broadcast({"event": "task_start", "task": "refine", "asset": req.asset_name})

        result = await ai_service.refine_asset(
            asset_name=req.asset_name,
            refine_type=req.refine_type,
            note=req.note,
        )

        await ws_manager.broadcast({"event": "task_complete", "task": "refine", "result": result})
        return result

    except Exception as e:
        await ws_manager.broadcast({"event": "task_error", "task": "refine", "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_assets(req: ExportRequest):
    """Export assets for a game engine."""
    try:
        from game_asset_tools.export import export_for_engine
        result = export_for_engine(req.engine, asset_service.output_dir, f"./{req.engine}_export/")
        return {"engine": req.engine, "total": result["total"], "export_dir": f"./{req.engine}_export/"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/atlas")
async def pack_atlas(req: AtlasRequest):
    """Pack assets into a texture atlas."""
    try:
        from game_asset_tools.atlas import pack_atlas

        type_to_dir = {
            "icons": "icons", "characters": "characters", "ui": "ui",
            "sprites": "sprites", "tilesets": "tilesets",
        }
        subdir = type_to_dir.get(req.input_type, req.input_type)
        input_dir = os.path.join(asset_service.output_dir, subdir)

        if not os.path.isdir(input_dir):
            raise HTTPException(status_code=400, detail=f"Directory not found: {subdir}")

        output_path = os.path.join(asset_service.output_dir, "sprites", f"{req.input_type}_atlas.png")
        meta_path = os.path.join(asset_service.output_dir, "sprites", f"{req.input_type}_atlas.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        w, h = req.max_size.split("x")
        pack_atlas(input_dir, output_path, meta_path, max_size=(int(w), int(h)),
                   padding=req.padding, meta_format=req.format)

        return {"atlas": output_path, "meta": meta_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
