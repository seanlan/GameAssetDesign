---
name: game-asset-extract
description: Extract assets from a design image. Recommends regeneration for complex elements.
---

# Extract Assets from Design Image

## Flow

1. User provides design image path
2. Claude reads and analyzes the image visually
3. For each detected element, recommend the BEST approach:

| Element | Recommended Approach | Why |
|---------|---------------------|-----|
| Character | **Regenerate** with `/game-asset:generate` using description | Extraction + post-processing degrades quality |
| Icons | **Regenerate** as a set with `/game-asset:generate` | One-shot batch is cleaner than crop+edit |
| Buttons | **Crop + rembg** | Simple shapes, rembg works well |
| HP/MP bars | **Crop only** | No processing needed |
| Background | **Crop** (+ AI inpaint if foreground blocking) | Direct extraction works |

4. Ask user to confirm approach for each element
5. Execute: crop what can be cropped, regenerate what should be regenerated

## For Crop-based Elements

```bash
# Buttons: crop + rembg
python3 -m game_asset_tools extract --input design.png --elements elements.json --output-dir output/

# Then for each button:
python3 -m game_asset_tools remove_bg --input btn.png --output btn.png
python3 -m game_asset_tools trim --input btn.png --output btn.png --padding 4
```

## For Regeneration-based Elements

Tell user:
> "I detected a warrior character and 3 skill icons. For best quality, I recommend regenerating them with AI rather than extracting. Should I proceed?"

Then use `/game-asset:generate` with descriptions matching the design image.

## Key Insight

**Regeneration > Extraction for quality.** Every AI edit degrades the image.
Crop from design → AI edit → more AI edits = quality loss at each step.
Fresh generation from a good prompt = clean, high-quality result.

Only extract simple elements (buttons, bars) that don't need AI processing.
