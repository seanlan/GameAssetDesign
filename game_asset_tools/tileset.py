"""Tileset assembly with optional seamless edge blending."""

import json
import math
import os
import tempfile
from PIL import Image
import numpy as np

from game_asset_tools.resize import resize_image


def make_seamless(input_path, output_path, blend_width=8):
    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape[:2]
    bw = min(blend_width, w // 4, h // 4)
    if bw < 1:
        img.save(output_path)
        return

    result = arr.copy()
    for i in range(bw):
        alpha = i / bw
        result[:, i] = arr[:, i] * alpha + arr[:, w - bw + i] * (1 - alpha)
        result[:, w - bw + i] = arr[:, w - bw + i] * alpha + arr[:, i] * (1 - alpha)
    for i in range(bw):
        alpha = i / bw
        result[i, :] = result[i, :] * alpha + arr[h - bw + i, :] * (1 - alpha)
        result[h - bw + i, :] = result[h - bw + i, :] * alpha + arr[i, :] * (1 - alpha)

    Image.fromarray(result.astype(np.uint8)).save(output_path, "PNG")


def assemble_tileset(input_dir, output_path, meta_path, tile_size, cols=None, seamless=False, blend_width=8):
    tile_files = sorted(f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg")))
    if not tile_files:
        raise ValueError(f"No tile images found in {input_dir}")

    num_tiles = len(tile_files)
    tw, th = tile_size
    if cols is None:
        cols = math.ceil(math.sqrt(num_tiles))
    rows = math.ceil(num_tiles / cols)

    sheet = Image.new("RGBA", (cols * tw, rows * th), (0, 0, 0, 0))
    tiles_meta = []

    for idx, fname in enumerate(tile_files):
        src_path = os.path.join(input_dir, fname)
        img = Image.open(src_path).convert("RGBA")

        if img.size != tile_size:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            resize_image(src_path, tmp_path, tile_size, mode="cover")
            img = Image.open(tmp_path).convert("RGBA")
            os.unlink(tmp_path)

        if seamless:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_in = tmp.name
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_out = tmp.name
            img.save(tmp_in)
            make_seamless(tmp_in, tmp_out, blend_width)
            img = Image.open(tmp_out).convert("RGBA")
            os.unlink(tmp_in)
            os.unlink(tmp_out)

        col = idx % cols
        row = idx // cols
        x = col * tw
        y = row * th
        sheet.paste(img, (x, y), img)
        tiles_meta.append({"filename": fname, "index": idx, "x": x, "y": y, "w": tw, "h": th})

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    sheet.save(output_path, "PNG")

    meta = {
        "tiles": tiles_meta,
        "meta": {"image": os.path.basename(output_path), "tile_size": {"w": tw, "h": th}, "columns": cols, "rows": rows, "total": num_tiles},
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
