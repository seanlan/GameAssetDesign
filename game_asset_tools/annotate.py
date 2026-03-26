"""Annotate design images with colored bounding boxes and labels for detected elements."""

import json
import os
from PIL import Image, ImageDraw, ImageFont

# Color mapping by element type: (R, G, B)
TYPE_COLORS = {
    "character": (220, 50, 50),
    "icon": (240, 200, 40),
    "ui": (50, 120, 220),
    "background": (50, 180, 80),
    "shared": (160, 80, 220),
}

# Alpha value for semi-transparent fill overlay
_FILL_ALPHA = 40
# Border line width
_BORDER_WIDTH = 2
# Dash segment length for shared asset dashed borders
_DASH_LENGTH = 8


def _load_elements(elements):
    """Load elements data from a file path or return dict directly."""
    if isinstance(elements, str):
        with open(elements, "r", encoding="utf-8") as f:
            return json.load(f)
    return elements


def _get_color(element_type):
    """Return the RGB color tuple for a given element type."""
    return TYPE_COLORS.get(element_type, (180, 180, 180))


def _draw_dashed_rect(draw, bbox, color, width=_BORDER_WIDTH, dash=_DASH_LENGTH):
    """Draw a dashed rectangle border on the draw surface."""
    x0, y0, x1, y1 = bbox
    # Draw dashes along each edge
    segments = [
        # top edge: left to right
        [(x, y0) for x in range(x0, x1, dash * 2)],
        # bottom edge: left to right
        [(x, y1) for x in range(x0, x1, dash * 2)],
        # left edge: top to bottom
        [(x0, y) for y in range(y0, y1, dash * 2)],
        # right edge: top to bottom
        [(x1, y) for y in range(y0, y1, dash * 2)],
    ]
    ends = [
        # top edge end offsets
        lambda x, y: (min(x + dash, x1), y),
        # bottom edge end offsets
        lambda x, y: (min(x + dash, x1), y),
        # left edge end offsets
        lambda x, y: (x, min(y + dash, y1)),
        # right edge end offsets
        lambda x, y: (x, min(y + dash, y1)),
    ]
    for seg_starts, end_fn in zip(segments, ends):
        for sx, sy in seg_starts:
            ex, ey = end_fn(sx, sy)
            draw.line([(sx, sy), (ex, ey)], fill=color, width=width)


def _draw_solid_rect(draw, bbox, color, width=_BORDER_WIDTH):
    """Draw a solid rectangle border on the draw surface."""
    x0, y0, x1, y1 = bbox
    draw.rectangle([x0, y0, x1, y1], outline=color, width=width)


def _draw_label(draw, bbox, label, color, index):
    """Draw a label text near the top-left of the bounding box."""
    x0, y0 = bbox[0], bbox[1]
    text = f"#{index} {label}"
    # Try to use a default font; fall back to PIL default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    except (IOError, OSError):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except (IOError, OSError):
            font = ImageFont.load_default()

    # Get text size for background box
    bbox_text = draw.textbbox((0, 0), text, font=font)
    tw = bbox_text[2] - bbox_text[0]
    th = bbox_text[3] - bbox_text[1]

    # Position label above the box if possible, else inside
    label_y = y0 - th - 4 if y0 > th + 4 else y0 + 2
    label_x = x0

    # Draw semi-transparent background for label
    draw.rectangle(
        [label_x, label_y, label_x + tw + 4, label_y + th + 2],
        fill=(*color, 180),
    )
    draw.text((label_x + 2, label_y + 1), text, fill=(255, 255, 255, 255), font=font)


def annotate_image(src_path, elements, out_path):
    """Draw colored bounding boxes and labels on a design image.

    Args:
        src_path: Path to the source PNG image.
        elements: Path to the elements JSON file, or a dict with element data.
        out_path: Path to save the annotated output image.
    """
    # Load source image
    src = Image.open(src_path).convert("RGBA")
    width, height = src.size

    # Load elements data
    data = _load_elements(elements)
    layers = data.get("layers", {})
    shared_assets = data.get("shared_assets", [])

    # Create RGBA overlay for drawing
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    element_index = 1

    # Draw layer elements
    for layer_name in layers:
        for elem in layers[layer_name]:
            etype = elem.get("type", "ui")
            color = _get_color(etype)
            bbox = elem.get("bbox", [0, 0, 10, 10])
            x0, y0, x1, y1 = bbox

            # Semi-transparent fill
            draw.rectangle([x0, y0, x1, y1], fill=(*color, _FILL_ALPHA))
            # Solid border
            _draw_solid_rect(draw, bbox, (*color, 220))
            # Label: "#N type: name"
            label = f"{etype}: {elem.get('name', '')}"
            _draw_label(draw, bbox, label, color, element_index)
            element_index += 1

    # Draw shared assets with dashed border
    for asset in shared_assets:
        color = _get_color("shared")
        bbox = asset.get("bbox", [0, 0, 10, 10])
        x0, y0, x1, y1 = bbox

        # Semi-transparent fill
        draw.rectangle([x0, y0, x1, y1], fill=(*color, _FILL_ALPHA))
        # Dashed border
        _draw_dashed_rect(draw, bbox, (*color, 220))
        # Label: "#N shared: name xN"
        reuse = asset.get("reuse_count", 1)
        label = f"shared: {asset.get('name', '')} x{reuse}"
        _draw_label(draw, bbox, label, color, element_index)
        element_index += 1

    # Composite overlay onto original
    result = Image.alpha_composite(src, overlay)

    # Save as RGB PNG
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    result.convert("RGB").save(out_path)
