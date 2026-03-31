"""Nine-slice (9-patch) image slicing for scalable UI elements."""

import json
import os
from dataclasses import dataclass, field
from PIL import Image


@dataclass
class NineSliceData:
    """Result of a nine-slice operation."""
    original_path: str
    original_size: tuple
    border_left: int
    border_right: int
    border_top: int
    border_bottom: int
    slices: dict  # name -> file path

    @property
    def border(self) -> int:
        """Uniform border if all sides are equal."""
        if self.border_left == self.border_right == self.border_top == self.border_bottom:
            return self.border_left
        return self.border_left  # fallback

    def save_meta(self, path: str) -> None:
        """Save metadata JSON with engine-specific configs."""
        w, h = self.original_size
        data = {
            "original_size": list(self.original_size),
            "border": {
                "left": self.border_left,
                "right": self.border_right,
                "top": self.border_top,
                "bottom": self.border_bottom,
            },
            "slices": {k: os.path.basename(v) for k, v in self.slices.items()},
            "engine_configs": {
                "unity": {
                    "sprite_border": f"{self.border_left} {self.border_bottom} {self.border_right} {self.border_top}",
                },
                "godot": {
                    "region_rect": f"Rect2(0, 0, {w}, {h})",
                    "patch_margin_left": self.border_left,
                    "patch_margin_right": self.border_right,
                    "patch_margin_top": self.border_top,
                    "patch_margin_bottom": self.border_bottom,
                },
            },
        }
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)


def slice_nine(
    input_path: str,
    output_dir: str,
    border: int = None,
    border_x: int = None,
    border_y: int = None,
) -> NineSliceData:
    """Slice an image into 9 parts for scalable UI.

    Args:
        input_path: source image
        output_dir: directory for sliced output files
        border: uniform border width (all sides)
        border_x: horizontal border (left and right)
        border_y: vertical border (top and bottom)
    """
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size

    bx = border_x or border or 0
    by = border_y or border or 0

    if bx * 2 >= w or by * 2 >= h:
        raise ValueError(
            f"Border ({bx}x{by}) too large for image ({w}x{h}). "
            f"Must be less than half the image size."
        )

    bl, br, bt, bb = bx, bx, by, by
    os.makedirs(output_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(input_path))[0]

    # Cut regions: (left, top, right, bottom)
    regions = {
        "top_left":     (0,      0,      bl,    bt),
        "top_center":   (bl,     0,      w-br,  bt),
        "top_right":    (w-br,   0,      w,     bt),
        "middle_left":  (0,      bt,     bl,    h-bb),
        "center":       (bl,     bt,     w-br,  h-bb),
        "middle_right": (w-br,   bt,     w,     h-bb),
        "bottom_left":  (0,      h-bb,   bl,    h),
        "bottom_center":(bl,     h-bb,   w-br,  h),
        "bottom_right": (w-br,   h-bb,   w,     h),
    }

    slices = {}
    for name, box in regions.items():
        out_path = os.path.join(output_dir, f"{stem}_{name}.png")
        cropped = img.crop(box)
        cropped.save(out_path, "PNG")
        slices[name] = out_path

    return NineSliceData(
        original_path=input_path,
        original_size=(w, h),
        border_left=bl,
        border_right=br,
        border_top=bt,
        border_bottom=bb,
        slices=slices,
    )


def generate_nine_slice_preview(
    data: NineSliceData,
    output_path: str,
    target_size: tuple = (300, 200),
) -> None:
    """Generate a preview image showing the 9-slice stretched to target size."""
    tw, th = target_size
    bl, br, bt, bb = data.border_left, data.border_right, data.border_top, data.border_bottom

    canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))

    # Load slices
    s = {k: Image.open(v).convert("RGBA") for k, v in data.slices.items()}

    # Corners (no stretch)
    canvas.paste(s["top_left"], (0, 0))
    canvas.paste(s["top_right"], (tw - br, 0))
    canvas.paste(s["bottom_left"], (0, th - bb))
    canvas.paste(s["bottom_right"], (tw - br, th - bb))

    # Edges (single-axis stretch)
    mid_w = tw - bl - br
    mid_h = th - bt - bb

    if mid_w > 0:
        canvas.paste(s["top_center"].resize((mid_w, bt), Image.LANCZOS), (bl, 0))
        canvas.paste(s["bottom_center"].resize((mid_w, bb), Image.LANCZOS), (bl, th - bb))
    if mid_h > 0:
        canvas.paste(s["middle_left"].resize((bl, mid_h), Image.LANCZOS), (0, bt))
        canvas.paste(s["middle_right"].resize((br, mid_h), Image.LANCZOS), (tw - br, bt))

    # Center (dual-axis stretch)
    if mid_w > 0 and mid_h > 0:
        canvas.paste(s["center"].resize((mid_w, mid_h), Image.LANCZOS), (bl, bt))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    canvas.save(output_path, "PNG")
