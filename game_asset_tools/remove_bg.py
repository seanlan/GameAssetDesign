"""Background removal using rembg."""

import os
from PIL import Image


def is_rembg_available() -> bool:
    try:
        import rembg
        return True
    except ImportError:
        return False


def remove_background(input_path: str, output_path: str) -> None:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Image not found: {input_path}")
    if not is_rembg_available():
        raise RuntimeError("rembg is not installed. Install with: pip install rembg")

    from rembg import remove
    img = Image.open(input_path)
    result = remove(img)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    result.save(output_path, "PNG")


def remove_background_batch(input_dir: str, output_dir: str) -> list[str]:
    os.makedirs(output_dir, exist_ok=True)
    results = []
    for fname in sorted(os.listdir(input_dir)):
        if fname.lower().endswith((".png", ".jpg", ".jpeg")):
            in_path = os.path.join(input_dir, fname)
            out_path = os.path.join(output_dir, fname)
            remove_background(in_path, out_path)
            results.append(out_path)
    return results
