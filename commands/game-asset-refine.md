---
name: game-asset-refine
description: Refine and polish assets — edge fix, AI edit, inpaint missing parts, style unification.
---

# Refine Assets

## BEFORE refining

1. Read `data/rules.csv` — priority 1 (quality rules: max 1 AI edit, regenerate > edit)
2. Read `data/rules.csv` — priority 2 (bg removal: chroma key selection, rembg limits)
3. Read `data/pipelines.csv` — check if the asset type has a specific refinement pipeline
4. **Key rule: each AI edit degrades quality. Prefer regeneration for small assets (icons/UI).**

## Input

User specifies which assets to refine and what to fix:
```
/game-asset:refine #2 边缘有白边, #5 颜色改成红色, #7 补全右臂
```

Or refine a specific file:
```
/game-asset:refine output/characters/warrior.png 补全缺失的右脚
```

## Refinement Types

### edge_fix — Edge cleanup
Re-run background removal with adjusted parameters:
```bash
python3 -m game_asset_tools remove_bg --input asset.png --output fixed.png
python3 -m game_asset_tools trim --input fixed.png --output trimmed.png --padding 1
```

### ai_edit — AI content modification
Use `mcp__gemini-image__edit_image` with user's description as prompt.
Then re-run chroma key pipeline if the asset needs transparent background.

### ai_inpaint — Complete missing parts
Use `mcp__gemini-image__edit_image`:
```
"Complete the missing [part]. Keep same art style and details."
```
For truncated assets, use one-shot redraw on chroma key:
```
"Redraw this [character] as complete full-body on solid green (#00FF00).
 Entire figure fully visible. Keep exact same design: [all details]."
```

### style_unify — Match project style
Use `mcp__gemini-image__style_transfer` with project reference image.

## After Each Refinement

1. Save version before modifying:
   ```bash
   python3 -m game_asset_tools version save --asset path --action "before_refine"
   ```
2. Apply refinement
3. Show result via Read tool
4. User confirms:
   - Satisfied → save new version, update manifest
   - Not satisfied → rollback, try different approach
5. Regenerate asset manager
