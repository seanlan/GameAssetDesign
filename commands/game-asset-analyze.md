---
name: game-asset-analyze
description: Analyze a design image — identify elements, calibrate bounding boxes, generate annotated preview.
---

# Analyze Design Image

Input: a design image (UI mockup, screenshot, reference image)
Output: elements.json + annotated preview image

## Flow

1. Read image with Read tool, get pixel dimensions
2. Visually identify all elements:
   - Characters (middle layer)
   - Icons with/without borders (top layer)
   - UI elements: buttons, bars, panels (top layer)
   - Background scene (bottom layer)
   - Shared components (borders/frames appearing multiple times)

3. For each element, determine:
   - `name` — descriptive name
   - `type` — character / icon / ui / background / sprite / tileset
   - `bbox` — [left, top, right, bottom] in pixels
   - `layer` — bottom / middle / top
   - `needs_remove_bg` — true/false
   - `uses_shared` — list of shared asset names (if applicable)

4. **Bbox Calibration (CRITICAL)**

   Claude's visual estimation has 20-50px error. Always calibrate:

   a. Test crop key regions to verify positions:
   ```python
   img.crop((x1, y1, x2, y2)).save('output/.tmp/test_crop.png')
   ```

   b. For dense elements (icon rows), use pixel color scanning:
   ```python
   for x in range(start, end):
       r, g, b = arr[y, x]
       if is_border_color(r, g, b):
           print(f'Border at x={x}')
   ```

   c. **bbox must be generous** — include extra space, even UI elements. Truncated content cannot be recovered.

5. Write `output/.tmp/elements.json`

6. Generate annotated preview:
   ```bash
   python3 -m game_asset_tools annotate --input design.png --elements output/.tmp/elements.json --output output/.tmp/annotated.png
   ```

7. Show annotated preview → user confirms or adjusts

8. User adjustments:
   - "删掉 3 号" → remove element
   - "2 号改名 ice_arrow" → rename
   - "1 号往右扩 20px" → adjust bbox
   - "这三个图标共用边框" → add shared_assets

9. Re-annotate after each change, repeat until confirmed

## Output

After user confirms, inform:
```
"分析完成，共识别 N 个元素。Use /game-asset:extract to extract assets."
```

elements.json stays at `output/.tmp/elements.json` for the extract command to use.

## Elements JSON Format

```json
{
  "source": "/path/to/design.png",
  "source_size": [1024, 1024],
  "layers": {
    "bottom": [
      {"name": "forest_bg", "type": "background", "bbox": [0,0,1024,1024],
       "needs_inpaint": true, "inpaint_prompt": "Remove characters and UI..."}
    ],
    "middle": [
      {"name": "warrior", "type": "character", "bbox": [100,200,700,1000],
       "needs_remove_bg": true}
    ],
    "top": [
      {"name": "icon_fire", "type": "icon", "bbox": [28,26,155,150],
       "needs_remove_bg": false, "uses_shared": ["icon_border"]}
    ]
  },
  "shared_assets": [
    {"name": "icon_border", "type": "ui", "bbox": [28,26,155,150], "reuse_count": 3}
  ]
}
```
