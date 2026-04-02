"""game-asset CLI — install commands and skills into a project directory."""

import argparse
import json
import os
import shutil
import subprocess
import sys


def _find_package_root() -> str:
    """Find the installed package root (where commands/, skills/ etc. live)."""
    # Walk up from this file to find the package root
    current = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(current)  # game_asset_tools -> package root

    # Verify it has the expected directories
    if os.path.isdir(os.path.join(root, "commands")) and os.path.isdir(os.path.join(root, "skills")):
        return root

    # Fallback: check common pip install locations
    for candidate in [
        os.path.join(sys.prefix, "share", "game-asset-design"),
        os.path.join(os.path.expanduser("~"), ".game-asset-design"),
    ]:
        if os.path.isdir(os.path.join(candidate, "commands")):
            return candidate

    return root


def init_project(project_dir: str) -> None:
    """Initialize game asset commands and skills in a project directory."""
    package_root = _find_package_root()
    project_dir = os.path.abspath(project_dir)

    print("🎮 Game Asset Design — Initializing project")
    print(f"   Source: {package_root}")
    print(f"   Project: {project_dir}")
    print()

    # 1. Copy commands
    commands_src = os.path.join(package_root, "commands")
    commands_dst = os.path.join(project_dir, ".claude", "commands")
    if os.path.isdir(commands_src):
        os.makedirs(commands_dst, exist_ok=True)
        count = 0
        for f in os.listdir(commands_src):
            if f.endswith(".md"):
                shutil.copy2(os.path.join(commands_src, f), os.path.join(commands_dst, f))
                count += 1
        print(f"📋 Installed {count} commands → .claude/commands/")
    else:
        print("⚠️  Commands directory not found")

    # 2. Copy skills + data
    skills_src = os.path.join(package_root, "skills", "game-asset")
    skills_dst = os.path.join(project_dir, ".claude", "skills", "game-asset")
    if os.path.isdir(skills_src):
        os.makedirs(os.path.join(skills_dst, "data"), exist_ok=True)
        # Copy SKILL.md
        skill_file = os.path.join(skills_src, "SKILL.md")
        if os.path.exists(skill_file):
            shutil.copy2(skill_file, os.path.join(skills_dst, "SKILL.md"))
        # Copy data/*.csv
        data_src = os.path.join(skills_src, "data")
        if os.path.isdir(data_src):
            data_count = 0
            for f in os.listdir(data_src):
                if f.endswith(".csv"):
                    shutil.copy2(os.path.join(data_src, f), os.path.join(skills_dst, "data", f))
                    data_count += 1
            print(f"📋 Installed skill + {data_count} data files → .claude/skills/game-asset/")
    else:
        print("⚠️  Skills directory not found")

    # 3. Create output directories
    for subdir in ["characters", "backgrounds", "ui", "cards", "icons", "sprites", "tilesets"]:
        os.makedirs(os.path.join(project_dir, "output", subdir), exist_ok=True)
    print("📁 Created output directories")

    # 4. Create templates directories
    for subdir in ["cards", "ui", "fonts/custom"]:
        os.makedirs(os.path.join(project_dir, "templates", subdir), exist_ok=True)

    # 5. Configure PYTHONPATH in .claude/settings.json
    settings_path = os.path.join(project_dir, ".claude", "settings.json")
    settings = {}
    if os.path.exists(settings_path):
        with open(settings_path) as f:
            settings = json.load(f)

    env = settings.get("env", {})
    pythonpath = env.get("PYTHONPATH", "")
    if package_root not in pythonpath:
        env["PYTHONPATH"] = f"{package_root}:{pythonpath}" if pythonpath else package_root
        settings["env"] = env
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)
        print("🔧 Configured PYTHONPATH in .claude/settings.json")

    # 6. Download font
    font_path = os.path.join(project_dir, "templates", "fonts", "NotoSansSC-Regular.ttf")
    if not os.path.exists(font_path):
        try:
            subprocess.run(
                ["curl", "-sL", "-o", font_path,
                 "https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"],
                timeout=30, check=False,
            )
            if os.path.exists(font_path) and os.path.getsize(font_path) > 1000:
                print("📦 Downloaded default font")
            else:
                print("⚠️  Font download failed (optional)")
        except Exception:
            print("⚠️  Font download skipped")

    print()
    print("✅ Game Asset Design initialized!")
    print()
    print("Available commands in Claude Code:")
    print("   /game-asset:init      — Create project config")
    print("   /game-asset:generate  — Generate assets with AI")
    print("   /game-asset:analyze   — Analyze design image")
    print("   /game-asset:extract   — Extract assets from design")
    print("   /game-asset:refine    — Refine/polish assets")
    print("   /game-asset:manage    — Open asset manager")
    print("   /game-asset:serve     — Start web service")
    print("   /game-asset:version   — Version management")
    print("   /game-asset:export    — Export for game engines")
    print("   /game-asset:atlas     — Texture atlas packing")
    print()
    print("Start Claude Code in this directory, then run: /game-asset:init")


def main():
    parser = argparse.ArgumentParser(
        prog="game-asset",
        description="Game Asset Design — 2D game asset toolkit",
    )
    subparsers = parser.add_subparsers(dest="command")

    # init
    p_init = subparsers.add_parser("init", help="Initialize game asset commands in a project")
    p_init.add_argument("project_dir", nargs="?", default=".", help="Project directory (default: current)")

    args = parser.parse_args()

    if args.command == "init":
        init_project(args.project_dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
