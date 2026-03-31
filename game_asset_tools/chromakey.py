"""Chroma key background removal with despill correction.

Supports green (#00FF00) and magenta (#FF00FF) chroma keys.
Auto-selects the chroma color that contrasts most with the image content.
"""

import os
import numpy as np
from PIL import Image


def select_chroma_color(image_path: str) -> str:
    """Auto-select the best chroma key color based on image content.

    Picks the chroma key that contrasts with dominant content hue.
    Returns "green" or "magenta".
    """
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img, dtype=np.float32)

    # Calculate average color
    avg_r = arr[:, :, 0].mean()
    avg_g = arr[:, :, 1].mean()
    avg_b = arr[:, :, 2].mean()

    # If content is green-ish (G dominant with balanced R and B), use magenta
    # Balanced R and B means R ≈ B (both contribute equally, no warm/cool skew)
    if avg_g > avg_r and avg_g > avg_b:
        r_b_ratio = avg_r / (avg_b + 1e-6)
        if 0.5 <= r_b_ratio <= 2.0:
            # Balanced green content -> avoid green for chromakey
            return "magenta"
        # Unbalanced: one channel much larger, likely mixed content with green bg
        if avg_r > avg_b:
            return "green"
        return "magenta"

    # If content is warm (R dominant), use green
    if avg_r > avg_b:
        return "green"

    # Cool content (B dominant), use magenta
    return "magenta"


def despill_green(arr: np.ndarray) -> np.ndarray:
    """Remove green color spill from edges.

    Where G dominates R and B, reduce G to avg(R, B).
    Applies to all pixels regardless of alpha so that semi-transparent
    edge pixels also have their color corrected.
    """
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    mask = (g > r * 1.3) & (g > b * 1.3) & (g > 120)
    arr[mask, 1] = (r[mask] + b[mask]) / 2

    # Very green pixels (almost pure green) -> transparent
    very_green = (g > 200) & (r < 100) & (b < 100)
    if arr.shape[2] == 4:
        arr[very_green, 3] = 0

    return arr


def despill_magenta(arr: np.ndarray) -> np.ndarray:
    """Remove magenta color spill from edges.

    Where R+B dominate G, reduce R and B toward G.
    Applies to all pixels regardless of alpha so that semi-transparent
    edge pixels also have their color corrected.
    """
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    mask = (r > g * 1.3) & (b > g * 1.3) & (r > 120) & (b > 120)
    avg_g = g[mask]
    arr[mask, 0] = np.minimum(r[mask], avg_g + 30)
    arr[mask, 2] = np.minimum(b[mask], avg_g + 30)

    return arr


def remove_chromakey(
    input_path: str,
    output_path: str,
    color: str = "auto",
    threshold: float = 180,
    edge_width: float = 40,
    despill: bool = True,
) -> str:
    """Remove chroma key background from an image.

    Args:
        input_path: input image path
        output_path: output image path (RGBA PNG)
        color: "green", "magenta", or "auto" (auto-detect)
        threshold: distance threshold for full transparency
        edge_width: width of the edge blend zone
        despill: apply color spill correction

    Returns:
        output_path
    """
    if color == "auto":
        color = select_chroma_color(input_path)

    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img, dtype=np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    if color == "green":
        # Distance to pure green (0, 255, 0)
        dist = np.sqrt(r ** 2 + (g - 255) ** 2 + b ** 2)
    elif color == "magenta":
        # Distance to pure magenta (255, 0, 255)
        dist = np.sqrt((r - 255) ** 2 + g ** 2 + (b - 255) ** 2)
    else:
        raise ValueError(
            f"Unknown chroma color: {color}. Use 'green', 'magenta', or 'auto'."
        )

    # Full transparency where close to chroma color
    arr[dist < threshold, 3] = 0

    # Edge blend
    edge = (dist >= threshold) & (dist < threshold + edge_width)
    arr[edge, 3] = ((dist[edge] - threshold) / edge_width * 255).clip(0, 255)

    # Despill
    if despill:
        if color == "green":
            arr = despill_green(arr)
        elif color == "magenta":
            arr = despill_magenta(arr)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    Image.fromarray(arr.astype(np.uint8)).save(output_path, "PNG")
    return output_path
