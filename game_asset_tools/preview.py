"""Batch asset preview HTML generator."""

import base64
import os
from PIL import Image


def generate_preview_html(input_dir, output_path, title="Game Asset Preview"):
    image_files = sorted(f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif")))

    cards_html = ""
    if not image_files:
        cards_html = '<p style="color:#888; text-align:center;">No assets found</p>'
    else:
        for fname in image_files:
            fpath = os.path.join(input_dir, fname)
            img = Image.open(fpath)
            w, h = img.size
            file_size = os.path.getsize(fpath)
            size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} B"
            with open(fpath, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            ext = fname.rsplit(".", 1)[-1].lower()
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif"}.get(ext, "image/png")
            cards_html += f'''
        <div class="card">
            <img src="data:{mime};base64,{b64}" alt="{fname}">
            <div class="info">
                <div class="filename">{fname}</div>
                <div class="meta">{w} x {h} &middot; {size_str}</div>
            </div>
        </div>'''

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
h1 {{ text-align: center; color: #e94560; margin-bottom: 30px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; max-width: 1200px; margin: 0 auto; }}
.card {{ background: #16213e; border-radius: 8px; overflow: hidden; border: 1px solid #0f3460; }}
.card img {{ width: 100%; height: 180px; object-fit: contain; background: repeating-conic-gradient(#333 0% 25%, #444 0% 50%) 50% / 16px 16px; }}
.info {{ padding: 8px 12px; }}
.filename {{ font-size: 12px; font-weight: 600; word-break: break-all; }}
.meta {{ font-size: 11px; color: #888; margin-top: 4px; }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="grid">{cards_html}
</div>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
