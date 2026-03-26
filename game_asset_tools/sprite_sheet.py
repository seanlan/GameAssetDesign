"""Sprite sheet assembly and frame metadata export."""

import json
import math
import os
import tempfile
from PIL import Image

from game_asset_tools.resize import resize_image


def assemble_sprite_sheet(input_dir, output_path, meta_path, frame_size, cols=None):
    frame_files = sorted(f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg")))
    if not frame_files:
        raise ValueError(f"No image files found in {input_dir}")

    num_frames = len(frame_files)
    fw, fh = frame_size
    if cols is None:
        cols = math.ceil(math.sqrt(num_frames))
    rows = math.ceil(num_frames / cols)

    sheet = Image.new("RGBA", (cols * fw, rows * fh), (0, 0, 0, 0))
    frames_meta = []

    for idx, fname in enumerate(frame_files):
        src_path = os.path.join(input_dir, fname)
        img = Image.open(src_path).convert("RGBA")

        if img.size != frame_size:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            resize_image(src_path, tmp_path, frame_size, mode="contain")
            img = Image.open(tmp_path).convert("RGBA")
            os.unlink(tmp_path)

        col = idx % cols
        row = idx // cols
        x = col * fw
        y = row * fh
        sheet.paste(img, (x, y), img)

        frames_meta.append({
            "filename": fname,
            "frame": {"x": x, "y": y, "w": fw, "h": fh},
            "sourceSize": {"w": fw, "h": fh},
            "spriteSourceSize": {"x": 0, "y": 0, "w": fw, "h": fh},
        })

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    sheet.save(output_path, "PNG")

    meta = {
        "frames": frames_meta,
        "meta": {
            "image": os.path.basename(output_path),
            "size": {"w": cols * fw, "h": rows * fh},
            "format": "RGBA8888",
            "scale": 1,
        },
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
