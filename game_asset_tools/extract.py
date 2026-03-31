"""Extract individual elements from a design image based on elements.json definition."""

import json
import os
from typing import Any

from PIL import Image


# Layer processing order: bottom first, then middle, then top
LAYER_ORDER = ["bottom", "middle", "top"]

# Map asset type to standard output subdirectory (plural form)
TYPE_TO_SUBDIR = {
    "character": "characters",
    "icon": "icons",
    "ui": "ui",
    "background": "backgrounds",
    "sprite": "sprites",
    "tileset": "tilesets",
    "card": "cards",
}


def _type_subdir(asset_type: str) -> str:
    """Get the standard output subdirectory for an asset type."""
    return TYPE_TO_SUBDIR.get(asset_type, asset_type)


def load_elements(path: str) -> dict:
    """Load elements definition from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_elements(elements: dict, image_size: tuple[int, int]) -> list[str]:
    """Validate element definitions against the image size.

    Returns a list of error messages; empty list means valid.
    """
    errors = []
    img_w, img_h = image_size

    layers = elements.get("layers", {})
    for layer_name, layer_items in layers.items():
        for idx, item in enumerate(layer_items):
            item_id = item.get("name", f"layer={layer_name} idx={idx}")

            # Required fields check
            if "name" not in item:
                errors.append(f"Element at layer={layer_name} idx={idx} is missing required field 'name'")
            if "bbox" not in item:
                errors.append(f"Element '{item_id}' is missing required field 'bbox'")
                continue

            bbox = item["bbox"]
            if len(bbox) != 4:
                errors.append(f"Element '{item_id}' bbox must have 4 values [x1, y1, x2, y2]")
                continue

            x1, y1, x2, y2 = bbox
            if x1 < 0 or y1 < 0:
                errors.append(f"Element '{item_id}' bbox has negative origin ({x1}, {y1})")
            if x2 > img_w or y2 > img_h:
                errors.append(
                    f"Element '{item_id}' bbox ({x2}, {y2}) exceeds image size ({img_w}, {img_h})"
                )
            if x2 <= x1 or y2 <= y1:
                errors.append(
                    f"Element '{item_id}' bbox is invalid: x2 must be > x1 and y2 must be > y1"
                )

    shared_assets = elements.get("shared_assets", [])
    for idx, item in enumerate(shared_assets):
        item_id = item.get("name", f"shared idx={idx}")
        if "name" not in item:
            errors.append(f"Shared asset at idx={idx} is missing required field 'name'")
        if "bbox" not in item:
            errors.append(f"Shared asset '{item_id}' is missing required field 'bbox'")
            continue

        bbox = item["bbox"]
        if len(bbox) != 4:
            errors.append(f"Shared asset '{item_id}' bbox must have 4 values")
            continue

        x1, y1, x2, y2 = bbox
        if x2 > img_w or y2 > img_h:
            errors.append(
                f"Shared asset '{item_id}' bbox ({x2}, {y2}) exceeds image size ({img_w}, {img_h})"
            )

    return errors


def crop_element(
    source_path: str,
    output_path: str,
    bbox: list[int],
    padding: int = 0,
) -> str:
    """Crop a region from source image with optional padding, clamped to image bounds.

    bbox: [x1, y1, x2, y2]
    Returns the output_path.
    """
    img = Image.open(source_path)
    img_w, img_h = img.size

    x1, y1, x2, y2 = bbox
    # Apply padding, clamped to image bounds
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(img_w, x2 + padding)
    y2 = min(img_h, y2 + padding)

    cropped = img.crop((x1, y1, x2, y2))
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    cropped.save(output_path, "PNG")
    return output_path


def _process_element(
    source_path: str,
    item: dict,
    output_path: str,
    remove_bg: bool,
    trim: bool,
    crop_padding: int,
    chromakey: bool = False,
) -> None:
    """Crop, optionally remove background (rembg or chromakey), optionally trim."""
    bbox = item["bbox"]
    element_type = item.get("type", "")

    # Step 1: crop
    crop_element(source_path, output_path, bbox=bbox, padding=crop_padding)

    # Step 2: remove background (skip for background type)
    needs_remove_bg = item.get("needs_remove_bg", remove_bg)
    if needs_remove_bg and element_type != "background":
        if chromakey:
            # Use chromakey removal (better for complex assets)
            from game_asset_tools.chromakey import remove_chromakey
            chroma_color = item.get("chromakey_color", "auto")
            remove_chromakey(output_path, output_path, color=chroma_color, despill=True)
        else:
            from game_asset_tools.remove_bg import remove_background
            remove_background(output_path, output_path)

    # Step 3: trim transparent
    needs_trim = item.get("needs_trim", trim)
    if needs_trim:
        from game_asset_tools.trim import trim_transparent
        trim_padding = item.get("trim_padding", 0)
        trim_transparent(output_path, output_path, padding=trim_padding)


def extract_elements(
    source_path: str,
    elements: dict,
    output_dir: str,
    remove_bg: bool = False,
    trim: bool = False,
    crop_padding: int = 0,
    chromakey: bool = False,
) -> list[dict[str, Any]]:
    """Extract all elements defined in the elements dict from the source image.

    Processing order:
      1. shared_assets (extracted once, saved to output_dir/{type}/shared/)
      2. layers in order: bottom → middle → top
         - background type elements: flagged with needs_inpaint if set, no rembg
         - regular elements: crop → rembg (optional) → trim (optional)

    Returns a list of result dicts with keys:
      name, type, output_path, is_shared (for shared), needs_inpaint (for bg elements)
    """
    results = []

    # --- Process shared assets first ---
    shared_assets = elements.get("shared_assets", [])
    for item in shared_assets:
        asset_type = item.get("type", "misc")
        name = item["name"]
        shared_dir = os.path.join(output_dir, _type_subdir(asset_type), "shared")
        os.makedirs(shared_dir, exist_ok=True)
        out_path = os.path.join(shared_dir, f"{name}.png")

        _process_element(
            source_path=source_path,
            item=item,
            output_path=out_path,
            remove_bg=remove_bg,
            trim=trim,
            crop_padding=crop_padding,
            chromakey=chromakey,
        )

        results.append({
            "name": name,
            "type": asset_type,
            "output_path": out_path,
            "is_shared": True,
        })

    # --- Process layers in order: bottom → middle → top ---
    layers = elements.get("layers", {})
    for layer_name in LAYER_ORDER:
        if layer_name not in layers:
            continue
        for item in layers[layer_name]:
            element_type = item.get("type", "misc")
            name = item["name"]
            type_dir = os.path.join(output_dir, _type_subdir(element_type))
            os.makedirs(type_dir, exist_ok=True)
            out_path = os.path.join(type_dir, f"{name}.png")

            _process_element(
                source_path=source_path,
                item=item,
                output_path=out_path,
                remove_bg=remove_bg,
                trim=trim,
                crop_padding=crop_padding,
                chromakey=chromakey,
            )

            result: dict[str, Any] = {
                "name": name,
                "type": element_type,
                "output_path": out_path,
            }

            # Flag inpaint for background elements
            if item.get("needs_inpaint"):
                result["needs_inpaint"] = True
                result["inpaint_prompt"] = item.get("inpaint_prompt", "")

            results.append(result)

    return results


def full_pipeline(
    source_path: str,
    output_dir: str,
    elements: dict | None = None,
    min_size: int = 30,
    max_elements: int = 20,
    chromakey: bool = True,
    trim: bool = True,
    trim_padding: int = 6,
    crop_padding: int = 4,
) -> dict:
    """One-step extraction pipeline: detect → annotate → extract → chromakey → trim.

    If elements is None, auto-detects using OpenCV.
    Returns dict with elements, annotated preview path, and extraction results.
    """
    tmp_dir = os.path.join(output_dir, ".tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    # Step 1: Detect elements (auto or provided)
    if elements is None:
        from game_asset_tools.auto_detect import detect_elements
        elements = detect_elements(source_path, min_size=min_size, max_elements=max_elements)
        elements["source"] = source_path

    # Save elements.json
    elements_path = os.path.join(tmp_dir, "elements.json")
    with open(elements_path, "w", encoding="utf-8") as f:
        json.dump(elements, f, indent=2, ensure_ascii=False)

    # Step 2: Annotate
    from game_asset_tools.annotate import annotate_image
    annotated_path = os.path.join(tmp_dir, "annotated.png")
    annotate_image(source_path, elements, annotated_path)

    # Step 3: Extract with chromakey + trim
    # Set trim_padding on all elements that don't have it
    for layer_name in ["bottom", "middle", "top"]:
        for item in elements.get("layers", {}).get(layer_name, []):
            if "trim_padding" not in item:
                item["trim_padding"] = trim_padding

    results = extract_elements(
        source_path=source_path,
        elements=elements,
        output_dir=output_dir,
        remove_bg=True,
        trim=trim,
        crop_padding=crop_padding,
        chromakey=chromakey,
    )

    return {
        "elements": elements,
        "elements_path": elements_path,
        "annotated_path": annotated_path,
        "results": results,
        "total": len(results),
    }
