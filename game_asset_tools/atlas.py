# game_asset_tools/atlas.py
"""Texture atlas packing using shelf-first-fit algorithm."""

import json
import os
from PIL import Image


def _shelf_pack(sprites: list[dict], max_w: int, max_h: int, padding: int) -> list[list[dict]]:
    """Pack sprites into pages using shelf-first-fit algorithm.

    Returns list of pages, each page is a list of placed sprites with x, y positions.
    """
    # Sort by height descending for better shelf packing
    sprites_sorted = sorted(sprites, key=lambda s: s["h"], reverse=True)

    pages = []
    remaining = list(sprites_sorted)

    while remaining:
        page = []
        shelf_y = 0
        shelf_h = 0
        cursor_x = 0

        to_place = list(remaining)
        remaining = []

        for sprite in to_place:
            sw = sprite["w"] + padding
            sh = sprite["h"] + padding

            # Try to fit on current shelf
            if cursor_x + sw <= max_w and shelf_y + sh <= max_h:
                page.append({**sprite, "x": cursor_x, "y": shelf_y})
                cursor_x += sw
                shelf_h = max(shelf_h, sh)
            # Try new shelf
            elif sw <= max_w and shelf_y + shelf_h + sh <= max_h:
                shelf_y += shelf_h
                shelf_h = sh
                cursor_x = sw
                page.append({**sprite, "x": 0, "y": shelf_y})
            else:
                # Doesn't fit on this page
                remaining.append(sprite)

        if page:
            pages.append(page)
        elif remaining:
            # Single sprite too large — force it on its own page
            s = remaining.pop(0)
            pages.append([{**s, "x": 0, "y": 0}])

    return pages


def _format_generic(pages: list[list[dict]], atlas_images: list[str], atlas_sizes: list[tuple]) -> dict:
    atlases = []
    for i, (page, img_name, size) in enumerate(zip(pages, atlas_images, atlas_sizes)):
        atlases.append({
            "image": img_name,
            "size": {"w": size[0], "h": size[1]},
            "sprites": [{"name": s["name"], "x": s["x"], "y": s["y"], "w": s["w"], "h": s["h"]} for s in page],
        })
    return {"atlases": atlases}


def _format_phaser(pages: list[list[dict]], atlas_images: list[str], atlas_sizes: list[tuple]) -> dict:
    """Phaser/TexturePacker format (single atlas only, first page)."""
    frames = {}
    page = pages[0] if pages else []
    for s in page:
        frames[s["name"]] = {
            "frame": {"x": s["x"], "y": s["y"], "w": s["w"], "h": s["h"]},
            "sourceSize": {"w": s["w"], "h": s["h"]},
            "spriteSourceSize": {"x": 0, "y": 0, "w": s["w"], "h": s["h"]},
        }
    return {
        "frames": frames,
        "meta": {
            "image": atlas_images[0] if atlas_images else "atlas.png",
            "size": {"w": atlas_sizes[0][0], "h": atlas_sizes[0][1]} if atlas_sizes else {"w": 0, "h": 0},
            "format": "RGBA8888",
            "scale": 1,
        },
    }


def pack_atlas(
    input_dir: str,
    output_path: str,
    meta_path: str,
    max_size: tuple[int, int] = (2048, 2048),
    padding: int = 2,
    meta_format: str = "generic",
) -> None:
    """Pack sprites from input_dir into texture atlas(es).

    Args:
        input_dir: directory with sprite images
        output_path: base output path for atlas images (e.g., atlas.png -> atlas_0.png, atlas_1.png)
        meta_path: output metadata JSON path
        max_size: maximum atlas size (width, height)
        padding: pixel spacing between sprites
        meta_format: "generic" or "phaser"
    """
    max_w, max_h = max_size

    # Collect sprites
    sprite_files = sorted(
        f for f in os.listdir(input_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    )
    if not sprite_files:
        raise ValueError(f"No sprite images found in {input_dir}")

    sprites = []
    for fname in sprite_files:
        path = os.path.join(input_dir, fname)
        img = Image.open(path)
        name = os.path.splitext(fname)[0]
        sprites.append({"name": name, "w": img.width, "h": img.height, "path": path, "fname": fname})

    # Pack
    pages = _shelf_pack(sprites, max_w, max_h, padding)

    # Render atlas images
    base, ext = os.path.splitext(output_path)
    if not ext:
        ext = ".png"

    atlas_images = []
    atlas_sizes = []
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    for i, page in enumerate(pages):
        # Calculate actual atlas size (tight fit)
        actual_w = max((s["x"] + s["w"] for s in page), default=0)
        actual_h = max((s["y"] + s["h"] for s in page), default=0)
        actual_w = min(actual_w, max_w)
        actual_h = min(actual_h, max_h)

        atlas = Image.new("RGBA", (actual_w, actual_h), (0, 0, 0, 0))
        for s in page:
            sprite_img = Image.open(s["path"]).convert("RGBA")
            atlas.paste(sprite_img, (s["x"], s["y"]), sprite_img)

        if len(pages) == 1:
            img_path = output_path
            img_name = os.path.basename(output_path)
        else:
            img_path = f"{base}_{i}{ext}"
            img_name = os.path.basename(img_path)

        atlas.save(img_path, "PNG")
        atlas_images.append(img_name)
        atlas_sizes.append((actual_w, actual_h))

    # Write metadata
    if meta_format == "phaser":
        meta_data = _format_phaser(pages, atlas_images, atlas_sizes)
    else:
        meta_data = _format_generic(pages, atlas_images, atlas_sizes)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=2)
