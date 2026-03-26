"""Card composer module for composing game card assets."""

import os
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont


def _find_project_root() -> str:
    """Find project root by walking up from this module's location."""
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        if os.path.exists(os.path.join(current, "pyproject.toml")) or os.path.exists(
            os.path.join(current, "templates")
        ):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.abspath(__file__))


def _load_font(font_size: int, config_font_path: Optional[str] = None) -> ImageFont.FreeTypeFont:
    """Load font with fallback chain: config path -> bundled font -> Pillow default."""
    # Try config-specified font path first
    if config_font_path and os.path.exists(config_font_path):
        try:
            return ImageFont.truetype(config_font_path, font_size)
        except Exception:
            pass

    # Try bundled NotoSansSC font
    project_root = _find_project_root()
    bundled_font = os.path.join(project_root, "templates", "fonts", "NotoSansSC-Regular.ttf")
    if os.path.exists(bundled_font):
        try:
            return ImageFont.truetype(bundled_font, font_size)
        except Exception:
            pass

    # Fallback to Pillow default
    return ImageFont.load_default()


def _draw_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    region: Tuple[int, int, int, int],
    font_size: int,
    color: str,
    overflow: str = "truncate",
    config_font_path: Optional[str] = None,
) -> None:
    """Draw text within region with overflow handling.

    Args:
        draw: ImageDraw object to draw on
        text: Text string to render
        region: (x, y, width, height) tuple defining the text region
        font_size: Font size in points
        color: Text color as hex string (e.g. "#FFFFFF")
        overflow: One of 'truncate', 'shrink', 'wrap'
        config_font_path: Optional path to a custom font file
    """
    x, y, width, height = region

    if overflow == "wrap":
        font = _load_font(font_size, config_font_path)
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = (current_line + " " + word).strip() if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            if line_width <= width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        # Draw each line at incremental y positions
        line_bbox = draw.textbbox((0, 0), "Ay", font=font)
        line_height = line_bbox[3] - line_bbox[1] + 4  # small padding
        current_y = y
        for line in lines:
            if current_y + line_height > y + height:
                break
            draw.text((x, current_y), line, font=font, fill=color)
            current_y += line_height
        # wrap handles its own drawing - return early
        return

    elif overflow == "shrink":
        # Reduce font_size until text fits within region width
        current_size = font_size
        font = _load_font(current_size, config_font_path)
        while current_size > 6:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            if text_width <= width:
                break
            current_size -= 1
            font = _load_font(current_size, config_font_path)
        draw.text((x, y), text, font=font, fill=color)

    else:
        # truncate mode (default)
        font = _load_font(font_size, config_font_path)
        original_len = len(text)  # save original length BEFORE the loop
        while len(text) > 0:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            if text_width <= width:
                break
            text = text[:-1]

        # Append ellipsis if text was truncated
        if len(text) < original_len:
            text = text.rstrip() + "..."

        draw.text((x, y), text, font=font, fill=color)


def compose_card(
    artwork_path: str,
    output_path: str,
    card_size: Tuple[int, int],
    artwork_region: Tuple[int, int, int, int],
    template_path: Optional[str] = None,
    title: Optional[str] = None,
    title_region: Optional[Tuple[int, int, int, int]] = None,
    title_color: str = "#000000",
    title_size: int = 24,
    description: Optional[str] = None,
    desc_region: Optional[Tuple[int, int, int, int]] = None,
    desc_color: str = "#000000",
    desc_size: int = 16,
    overflow: str = "truncate",
    config_font_path: Optional[str] = None,
) -> None:
    """Compose a game card by placing artwork into a template with optional text.

    Args:
        artwork_path: Path to the artwork image file
        output_path: Path to save the composed card
        card_size: (width, height) of the output card
        artwork_region: (x, y, width, height) region to place artwork
        template_path: Optional path to an RGBA border/template image
        title: Optional title text to render
        title_region: (x, y, width, height) region for title text
        title_color: Title text color as hex string
        title_size: Title font size
        description: Optional description text to render
        desc_region: (x, y, width, height) region for description text
        desc_color: Description text color as hex string
        desc_size: Description font size
        overflow: Text overflow mode: 'truncate', 'shrink', or 'wrap'
        config_font_path: Optional path to a custom font file
    """
    # Create card base as RGBA
    card = Image.new("RGBA", card_size, (30, 30, 30, 255))

    # Place artwork into artwork_region using cover mode (scale to fill, center crop)
    artwork = Image.open(artwork_path).convert("RGBA")
    art_x, art_y, art_w, art_h = artwork_region

    # Cover mode: scale to fill the region, then center crop
    art_ratio = artwork.width / artwork.height
    region_ratio = art_w / art_h

    if art_ratio > region_ratio:
        # Artwork is wider than region - scale by height
        scale_h = art_h
        scale_w = int(artwork.width * art_h / artwork.height)
    else:
        # Artwork is taller than region - scale by width
        scale_w = art_w
        scale_h = int(artwork.height * art_w / artwork.width)

    artwork_scaled = artwork.resize((scale_w, scale_h), Image.LANCZOS)

    # Center crop
    crop_x = (scale_w - art_w) // 2
    crop_y = (scale_h - art_h) // 2
    artwork_cropped = artwork_scaled.crop((crop_x, crop_y, crop_x + art_w, crop_y + art_h))

    # Paste artwork onto card
    card.paste(artwork_cropped, (art_x, art_y))

    # Overlay template on top if provided
    if template_path and os.path.exists(template_path):
        template = Image.open(template_path).convert("RGBA")
        if template.size != card_size:
            template = template.resize(card_size, Image.LANCZOS)
        card = Image.alpha_composite(card, template)

    # Draw title text if provided
    if title and title_region:
        draw = ImageDraw.Draw(card)
        _draw_text(
            draw=draw,
            text=title,
            region=title_region,
            font_size=title_size,
            color=title_color,
            overflow=overflow,
            config_font_path=config_font_path,
        )

    # Draw description text if provided
    if description and desc_region:
        draw = ImageDraw.Draw(card)
        _draw_text(
            draw=draw,
            text=description,
            region=desc_region,
            font_size=desc_size,
            color=desc_color,
            overflow=overflow,
            config_font_path=config_font_path,
        )

    # Save output - convert to RGB if output is not PNG with alpha
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    card.save(output_path)
