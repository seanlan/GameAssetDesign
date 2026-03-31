"""Auto-detect game UI elements in design images using OpenCV edge detection."""

import os
import json
import cv2
import numpy as np
from PIL import Image


def detect_elements(image_path: str, min_size: int = 30, max_elements: int = 20) -> dict:
    """Auto-detect UI elements in a design image using contour detection.

    Returns elements dict in the standard format compatible with extract pipeline.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot open image: {image_path}")

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Edge detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Dilate to connect nearby edges
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(edges, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and sort by area (largest first)
    elements = []
    for contour in contours:
        x, y, cw, ch = cv2.boundingRect(contour)
        area = cw * ch

        # Filter: minimum size, not the full image
        if cw < min_size or ch < min_size:
            continue
        if cw > w * 0.95 and ch > h * 0.95:
            continue  # Skip full-image contour

        elements.append({
            "bbox": [x, y, x + cw, y + ch],
            "area": area,
            "aspect": round(cw / ch, 2) if ch > 0 else 1,
            "width": cw,
            "height": ch,
        })

    # Sort by area descending, limit count
    elements.sort(key=lambda e: e["area"], reverse=True)
    elements = elements[:max_elements]

    # Classify elements by size and position
    result_layers = {"bottom": [], "middle": [], "top": []}

    for i, elem in enumerate(elements):
        bbox = elem["bbox"]
        rel_area = elem["area"] / (w * h)
        aspect = elem["aspect"]

        # Guess type and layer based on heuristics
        if rel_area > 0.3:
            elem_type = "background"
            layer = "bottom"
        elif rel_area > 0.05:
            elem_type = "character"
            layer = "middle"
        elif aspect > 2 or aspect < 0.5:
            elem_type = "ui"  # bars, wide/tall elements
            layer = "top"
        elif elem["width"] < 150 and elem["height"] < 150:
            elem_type = "icon"
            layer = "top"
        else:
            elem_type = "ui"
            layer = "top"

        entry = {
            "name": f"{elem_type}_{i+1}",
            "type": elem_type,
            "bbox": bbox,
            "needs_remove_bg": elem_type not in ("background", "ui"),
        }

        result_layers[layer].append(entry)

    return {
        "source": image_path,
        "source_size": [w, h],
        "layers": result_layers,
        "shared_assets": [],
        "_auto_detected": True,
    }
