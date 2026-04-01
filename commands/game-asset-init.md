---
name: game-asset-init
description: Initialize a game asset project — create project config with style, engine, sizes, and requirements.
---

# Initialize Game Asset Project

## Dependency Check

```bash
python3 -m game_asset_tools --help
```

If fails: `pip install -r requirements.txt`

## Flow

1. Ask user for:
   - Project name
   - Game engine (unity / godot / cocos / web / custom)
   - Art style preset (pixel / anime / cel_shading / watercolor / flat / realistic / ghibli / cyberpunk / fantasy)
   - Reference image path (a design mockup or effect image that defines the game's visual style)
   - Additional style keywords (optional)
   - Color palette (optional)

2. Create project config at `game-assets.yaml` in the current project root:

```yaml
project:
  name: "{name}"
  engine: "{engine}"

style:
  preset: "{preset}"
  reference_image: null
  keywords: "{keywords}"
  palette: []

assets:
  character:
    sizes: [512, 1024]
    format: "png"
    transparent: true
  background:
    sizes: ["1920x1080"]
    format: "png"
    transparent: false
  icon:
    sizes: [64, 128, 256]
    format: "png"
    transparent: true
  card:
    size: "750x1050"
    template: "templates/cards/default.png"
    layout:
      artwork: [50, 50, 650, 600]
      title: [50, 660, 650, 60]
      description: [50, 740, 650, 200]
  sprite:
    frame_size: [128, 128]
    format: "png"
    transparent: true
  tileset:
    tile_size: [32, 32]
    format: "png"
  ui:
    sizes: [64, 128]
    format: "png"
    transparent: true
    states: ["normal", "hover", "pressed", "disabled"]

output:
  base_dir: "output/"
  naming: "{type}_{name}_{size}_{variant}"
```

3. Ask if user wants to define requirements (asset checklist for progress tracking):

```yaml
requirements:
  characters:
    - name: "hero"
      description: "Main character"
  icons:
    - name: "fireball"
    - name: "healing"
```

4. Create output directories:
```bash
mkdir -p output/{characters,backgrounds,ui,cards,icons,sprites,tilesets}
```

5. Confirm: "Project '{name}' initialized. Use `/game-asset:generate` to create assets or `/game-asset:analyze` to extract from a design image."
