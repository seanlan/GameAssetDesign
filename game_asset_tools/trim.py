"""Transparent area trimming for game assets."""

import os
from PIL import Image


def get_content_bbox(image_path: str) -> tuple[int, int, int, int] | None:
    img = Image.open(image_path).convert("RGBA")
    alpha = img.split()[3]
    bbox = alpha.getbbox()
    return bbox


def trim_transparent(input_path: str, output_path: str, padding: int = 0) -> str | None:
    img = Image.open(input_path)
    if img.mode != "RGBA":
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        img.save(output_path, "PNG")
        return output_path

    alpha = img.split()[3]
    bbox = alpha.getbbox()
    if bbox is None:
        return None

    left, top, right, bottom = bbox
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(img.width, right + padding)
    bottom = min(img.height, bottom + padding)

    trimmed = img.crop((left, top, right, bottom))
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    trimmed.save(output_path, "PNG")
    return output_path
