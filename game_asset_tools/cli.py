"""CLI dispatcher for game_asset_tools: python3 -m game_asset_tools <command> [options]"""

import argparse
import sys


def _parse_size(size_str: str) -> tuple[int, int]:
    """Parse size string like '64x64' -> (64, 64) or '512' -> (512, 512)."""
    if "x" in size_str.lower():
        parts = size_str.lower().split("x")
        return int(parts[0]), int(parts[1])
    val = int(size_str)
    return val, val


def _cmd_resize(args):
    from game_asset_tools.resize import resize_image
    size = _parse_size(args.size)
    resize_image(args.input, args.output, size, mode=args.mode)
    print(f"Resized: {args.output}")


def _cmd_remove_bg(args):
    from game_asset_tools.remove_bg import remove_background, remove_background_batch
    if args.input_dir:
        results = remove_background_batch(args.input_dir, args.output_dir)
        print(f"Processed {len(results)} files -> {args.output_dir}")
    else:
        remove_background(args.input, args.output)
        print(f"Background removed: {args.output}")


def _cmd_sprite_sheet(args):
    from game_asset_tools.sprite_sheet import assemble_sprite_sheet
    frame_size = _parse_size(args.frame_size) if args.frame_size else None
    cols = int(args.cols) if args.cols else None
    assemble_sprite_sheet(
        input_dir=args.input_dir,
        output_path=args.output,
        meta_path=args.meta,
        frame_size=frame_size,
        cols=cols,
    )
    print(f"Sprite sheet: {args.output}, meta: {args.meta}")


def _cmd_card_composer(args):
    from game_asset_tools.card_composer import compose_card
    card_size = _parse_size(args.card_size) if args.card_size else (512, 768)
    # Parse artwork_region: "x,y,w,h"
    if args.artwork_region:
        parts = [int(v) for v in args.artwork_region.split(",")]
        artwork_region = tuple(parts)
    else:
        # Default region: full card
        artwork_region = (0, 0, card_size[0], card_size[1])

    title_region = None
    if args.title_region:
        parts = [int(v) for v in args.title_region.split(",")]
        title_region = tuple(parts)

    desc_region = None
    if args.desc_region:
        parts = [int(v) for v in args.desc_region.split(",")]
        desc_region = tuple(parts)

    compose_card(
        artwork_path=args.artwork,
        output_path=args.output,
        card_size=card_size,
        artwork_region=artwork_region,
        template_path=args.template,
        title=args.title,
        title_region=title_region,
        title_color=args.title_color,
        title_size=int(args.title_size),
        description=args.description,
        desc_region=desc_region,
        desc_color=args.desc_color,
        desc_size=int(args.desc_size),
        font_path=args.font,
        overflow=args.overflow,
    )
    print(f"Card composed: {args.output}")


def _cmd_video_to_frames(args):
    from game_asset_tools.video_to_frames import extract_frames
    count = extract_frames(
        video_path=args.input,
        output_dir=args.output_dir,
        fps=float(args.fps),
        dedup=args.dedup,
        dedup_threshold=float(args.dedup_threshold),
    )
    print(f"Extracted {count} frames -> {args.output_dir}")


def _cmd_tileset(args):
    from game_asset_tools.tileset import assemble_tileset
    tile_size = _parse_size(args.tile_size) if args.tile_size else None
    cols = int(args.cols) if args.cols else None
    assemble_tileset(
        input_dir=args.input_dir,
        output_path=args.output,
        meta_path=args.meta,
        tile_size=tile_size,
        cols=cols,
        seamless=args.seamless,
        blend_width=int(args.blend_width),
    )
    print(f"Tileset: {args.output}, meta: {args.meta}")


def _cmd_preview(args):
    from game_asset_tools.preview import generate_preview_html
    title = args.title if args.title else "Game Asset Preview"
    generate_preview_html(
        input_dir=args.input_dir,
        output_path=args.output,
        title=title,
    )
    print(f"Preview: {args.output}")


def _cmd_trim(args):
    from game_asset_tools.trim import trim_transparent
    result = trim_transparent(args.input, args.output, padding=args.padding)
    if result:
        print(f"Trimmed: {args.output}")
    else:
        print("Image is fully transparent, no output produced")


def _cmd_annotate(args):
    from game_asset_tools.annotate import annotate_image
    annotate_image(args.input, args.elements, args.output)
    print(f"Annotated: {args.output}")


def _cmd_extract(args):
    from game_asset_tools.extract import extract_elements, load_elements
    elements = load_elements(args.elements)
    results = extract_elements(
        source_path=args.input, elements=elements, output_dir=args.output_dir,
        remove_bg=args.remove_bg, trim=args.do_trim, crop_padding=args.padding,
    )
    print(f"Extracted {len(results)} elements")
    for r in results:
        flag = " [needs inpaint]" if r.get("needs_inpaint") else ""
        shared = " [shared]" if r.get("is_shared") else ""
        print(f"  {r['type']}: {r['name']} -> {r['output_path']}{flag}{shared}")


def _cmd_version(args):
    from game_asset_tools.version import VersionManager
    vm = VersionManager(args.asset)
    if args.version_action == "save":
        v = vm.save_version(action=args.action, note=args.note or "")
        print(f"Saved v{v}")
    elif args.version_action == "list":
        versions = vm.list_versions()
        for v in versions:
            note = f" - {v.get('note', '')}" if v.get('note') else ""
            print(f"  v{v['version']}: {v['action']}{note} ({v.get('timestamp', '')[:19]})")
    elif args.version_action == "rollback":
        vm.rollback(args.to)
        print(f"Rolled back to v{args.to}")
    elif args.version_action == "compare":
        vm.compare(args.v1, args.v2, args.output)
        print(f"Comparison: {args.output}")


def _cmd_manager(args):
    from game_asset_tools.manager import generate_manager_html
    import os
    manifest = args.manifest if args.manifest and os.path.exists(args.manifest) else None
    generate_manager_html(args.output_dir, manifest, args.output)
    print(f"Manager: {args.output}")


def _cmd_export(args):
    from game_asset_tools.export import export_for_engine
    result = export_for_engine(args.engine, args.input_dir, args.export_dir)
    print(f"Exported {result['total']} files for {args.engine} -> {args.export_dir}")


def _cmd_atlas(args):
    from game_asset_tools.atlas import pack_atlas
    max_size = _parse_size(args.max_size)
    pack_atlas(args.input_dir, args.output, args.meta, max_size=max_size, padding=args.padding, meta_format=args.format)
    print(f"Atlas packed: {args.output}, meta: {args.meta}")


def _cmd_chromakey(args):
    from game_asset_tools.chromakey import remove_chromakey
    remove_chromakey(args.input, args.output, color=args.color,
                     despill=not args.no_despill)
    print(f"Chroma key removed: {args.output}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="game_asset_tools",
        description="Game asset processing toolkit",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    # --- resize ---
    p_resize = subparsers.add_parser("resize", help="Resize an image to a target size")
    p_resize.add_argument("--input", required=True, help="Input image path")
    p_resize.add_argument("--output", required=True, help="Output image path")
    p_resize.add_argument("--size", required=True, help="Target size e.g. 64x64 or 512")
    p_resize.add_argument("--mode", default="contain", choices=["contain", "cover", "stretch"], help="Resize mode")

    # --- remove_bg ---
    p_rmbg = subparsers.add_parser("remove_bg", help="Remove background from an image")
    p_rmbg.add_argument("--input", help="Input image path (single file mode)")
    p_rmbg.add_argument("--output", help="Output image path (single file mode)")
    p_rmbg.add_argument("--input-dir", dest="input_dir", help="Input directory (batch mode)")
    p_rmbg.add_argument("--output-dir", dest="output_dir", help="Output directory (batch mode)")

    # --- sprite_sheet ---
    p_ss = subparsers.add_parser("sprite_sheet", help="Assemble a sprite sheet from frames")
    p_ss.add_argument("--input-dir", dest="input_dir", required=True, help="Directory of frame images")
    p_ss.add_argument("--output", required=True, help="Output sprite sheet image path")
    p_ss.add_argument("--meta", required=True, help="Output JSON metadata path")
    p_ss.add_argument("--frame-size", dest="frame_size", help="Frame size e.g. 64x64")
    p_ss.add_argument("--cols", help="Number of columns in the sheet")

    # --- card_composer ---
    p_card = subparsers.add_parser("card_composer", help="Compose a game card")
    p_card.add_argument("--artwork", required=True, help="Artwork image path")
    p_card.add_argument("--output", required=True, help="Output card image path")
    p_card.add_argument("--card-size", dest="card_size", help="Card size e.g. 512x768")
    p_card.add_argument("--artwork-region", dest="artwork_region", help="Artwork region x,y,w,h")
    p_card.add_argument("--template", help="Optional card template overlay image")
    p_card.add_argument("--title", help="Card title text")
    p_card.add_argument("--title-region", dest="title_region", help="Title region x,y,w,h")
    p_card.add_argument("--title-color", dest="title_color", default="#000000", help="Title text color")
    p_card.add_argument("--title-size", dest="title_size", default="24", help="Title font size")
    p_card.add_argument("--description", help="Card description text")
    p_card.add_argument("--desc-region", dest="desc_region", help="Description region x,y,w,h")
    p_card.add_argument("--desc-color", dest="desc_color", default="#000000", help="Description text color")
    p_card.add_argument("--desc-size", dest="desc_size", default="16", help="Description font size")
    p_card.add_argument("--overflow", default="truncate", choices=["truncate", "shrink", "wrap"], help="Text overflow mode")
    p_card.add_argument("--font", help="Font file path for text rendering")

    # --- video_to_frames ---
    p_v2f = subparsers.add_parser("video_to_frames", help="Extract frames from a video")
    p_v2f.add_argument("--input", required=True, help="Input video path")
    p_v2f.add_argument("--output-dir", dest="output_dir", required=True, help="Output directory for frames")
    p_v2f.add_argument("--fps", default="8", help="Frames per second to extract")
    p_v2f.add_argument("--dedup", action="store_true", help="Enable frame deduplication")
    p_v2f.add_argument("--dedup-threshold", dest="dedup_threshold", default="0.95", help="Deduplication similarity threshold")

    # --- tileset ---
    p_ts = subparsers.add_parser("tileset", help="Assemble a tileset image")
    p_ts.add_argument("--input-dir", dest="input_dir", required=True, help="Directory of tile images")
    p_ts.add_argument("--output", required=True, help="Output tileset image path")
    p_ts.add_argument("--meta", required=True, help="Output JSON metadata path")
    p_ts.add_argument("--tile-size", dest="tile_size", help="Tile size e.g. 32x32")
    p_ts.add_argument("--cols", help="Number of columns in the tileset")
    p_ts.add_argument("--seamless", action="store_true", help="Enable seamless edge blending")
    p_ts.add_argument("--blend-width", dest="blend_width", default="8", help="Blend width for seamless mode")

    # --- preview ---
    p_preview = subparsers.add_parser("preview", help="Generate HTML asset preview")
    p_preview.add_argument("--input-dir", dest="input_dir", required=True, help="Directory of assets to preview")
    p_preview.add_argument("--output", required=True, help="Output HTML file path")
    p_preview.add_argument("--title", help="Preview page title")

    # --- trim ---
    p_trim = subparsers.add_parser("trim", help="Trim transparent edges from an image")
    p_trim.add_argument("--input", required=True, help="Input image path")
    p_trim.add_argument("--output", required=True, help="Output image path")
    p_trim.add_argument("--padding", type=int, default=0, help="Pixels of padding to keep")

    # --- annotate ---
    p_ann = subparsers.add_parser("annotate", help="Generate annotated preview of detected elements")
    p_ann.add_argument("--input", required=True, help="Source design image path")
    p_ann.add_argument("--elements", required=True, help="Path to elements.json")
    p_ann.add_argument("--output", required=True, help="Output annotated image path")

    # --- extract ---
    p_ext = subparsers.add_parser("extract", help="Extract elements from a design image")
    p_ext.add_argument("--input", required=True, help="Source design image path")
    p_ext.add_argument("--elements", required=True, help="Path to elements.json")
    p_ext.add_argument("--output-dir", dest="output_dir", required=True, help="Output directory")
    p_ext.add_argument("--no-remove-bg", dest="remove_bg", action="store_false", default=True)
    p_ext.add_argument("--no-trim", dest="do_trim", action="store_false", default=True)
    p_ext.add_argument("--padding", type=int, default=4, help="Crop padding pixels")

    # --- version ---
    p_ver = subparsers.add_parser("version", help="Manage asset versions")
    ver_sub = p_ver.add_subparsers(dest="version_action")
    vs = ver_sub.add_parser("save")
    vs.add_argument("--asset", required=True)
    vs.add_argument("--action", required=True)
    vs.add_argument("--note", default="")
    vl = ver_sub.add_parser("list")
    vl.add_argument("--asset", required=True)
    vr = ver_sub.add_parser("rollback")
    vr.add_argument("--asset", required=True)
    vr.add_argument("--to", type=int, required=True)
    vc = ver_sub.add_parser("compare")
    vc.add_argument("--asset", required=True)
    vc.add_argument("--v1", type=int, required=True)
    vc.add_argument("--v2", type=int, required=True)
    vc.add_argument("--output", required=True)

    # --- manager ---
    p_mgr = subparsers.add_parser("manager", help="Generate asset manager HTML")
    p_mgr.add_argument("--output-dir", dest="output_dir", required=True)
    p_mgr.add_argument("--manifest", default=None)
    p_mgr.add_argument("--output", required=True)

    # --- export ---
    p_exp = subparsers.add_parser("export", help="Export assets for game engine")
    p_exp.add_argument("--engine", required=True, choices=["unity", "godot", "cocos", "web"])
    p_exp.add_argument("--input-dir", dest="input_dir", required=True)
    p_exp.add_argument("--export-dir", dest="export_dir", required=True)

    # --- atlas ---
    p_atl = subparsers.add_parser("atlas", help="Pack sprites into texture atlas")
    p_atl.add_argument("--input-dir", dest="input_dir", required=True)
    p_atl.add_argument("--output", required=True)
    p_atl.add_argument("--meta", required=True)
    p_atl.add_argument("--max-size", dest="max_size", default="2048x2048")
    p_atl.add_argument("--padding", type=int, default=2)
    p_atl.add_argument("--format", default="generic", choices=["generic", "phaser"])

    # --- chromakey ---
    p_ck = subparsers.add_parser("chromakey", help="Remove chroma key background (green/magenta)")
    p_ck.add_argument("--input", required=True, help="Input image path")
    p_ck.add_argument("--output", required=True, help="Output image path")
    p_ck.add_argument("--color", default="auto", choices=["auto", "green", "magenta"])
    p_ck.add_argument("--no-despill", dest="no_despill", action="store_true")

    return parser


_COMMAND_HANDLERS = {
    "resize": _cmd_resize,
    "remove_bg": _cmd_remove_bg,
    "sprite_sheet": _cmd_sprite_sheet,
    "card_composer": _cmd_card_composer,
    "video_to_frames": _cmd_video_to_frames,
    "tileset": _cmd_tileset,
    "preview": _cmd_preview,
    "trim": _cmd_trim,
    "annotate": _cmd_annotate,
    "extract": _cmd_extract,
    "version": _cmd_version,
    "manager": _cmd_manager,
    "export": _cmd_export,
    "atlas": _cmd_atlas,
    "chromakey": _cmd_chromakey,
}


def main():
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    handler = _COMMAND_HANDLERS.get(args.command)
    if handler is None:
        parser.error(f"Unknown command: {args.command}")
        sys.exit(2)

    try:
        handler(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
