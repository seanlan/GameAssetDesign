"""Image resize, crop, and pad utilities."""

import os
from PIL import Image


def resize_image(input_path: str, output_path: str, size: tuple[int, int], mode: str = "contain") -> None:
    img = Image.open(input_path).convert("RGBA")
    target_w, target_h = size

    if mode == "stretch":
        result = img.resize((target_w, target_h), Image.LANCZOS)
    elif mode == "contain":
        ratio = min(target_w / img.width, target_h / img.height)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        resized = img.resize((new_w, new_h), Image.LANCZOS)
        result = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        offset_x = (target_w - new_w) // 2
        offset_y = (target_h - new_h) // 2
        result.paste(resized, (offset_x, offset_y), resized)
    elif mode == "cover":
        ratio = max(target_w / img.width, target_h / img.height)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        resized = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        result = resized.crop((left, top, left + target_w, top + target_h))
    else:
        raise ValueError(f"Unknown resize mode: {mode}")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    result.save(output_path, "PNG")


def resize_batch(input_dir: str, output_dir: str, size: tuple[int, int], mode: str = "contain") -> list[str]:
    os.makedirs(output_dir, exist_ok=True)
    results = []
    for fname in sorted(os.listdir(input_dir)):
        if fname.lower().endswith((".png", ".jpg", ".jpeg")):
            in_path = os.path.join(input_dir, fname)
            out_path = os.path.join(output_dir, fname)
            resize_image(in_path, out_path, size, mode)
            results.append(out_path)
    return results
