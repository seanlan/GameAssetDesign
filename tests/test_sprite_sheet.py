import os
import json
from PIL import Image
from game_asset_tools.sprite_sheet import assemble_sprite_sheet


def test_assemble_basic(sample_frames, tmp_dir):
    frames_dir, _ = sample_frames
    output = os.path.join(tmp_dir, "sheet.png")
    meta_output = os.path.join(tmp_dir, "sheet.json")
    assemble_sprite_sheet(input_dir=frames_dir, output_path=output, meta_path=meta_output, cols=2, frame_size=(64, 64))
    sheet = Image.open(output)
    assert sheet.size == (128, 128)  # 4 frames, 2 cols -> 2 rows
    with open(meta_output) as f:
        meta = json.load(f)
    assert len(meta["frames"]) == 4
    assert meta["frames"][0]["frame"]["x"] == 0
    assert meta["frames"][0]["frame"]["w"] == 64


def test_assemble_auto_cols(sample_frames, tmp_dir):
    frames_dir, _ = sample_frames
    output = os.path.join(tmp_dir, "sheet.png")
    meta_output = os.path.join(tmp_dir, "sheet.json")
    assemble_sprite_sheet(input_dir=frames_dir, output_path=output, meta_path=meta_output, frame_size=(64, 64))
    sheet = Image.open(output)
    assert sheet.size[0] > 0 and sheet.size[1] > 0


def test_assemble_resizes_frames(tmp_dir):
    frames_dir = os.path.join(tmp_dir, "mixed")
    os.makedirs(frames_dir)
    Image.new("RGBA", (100, 100), (255, 0, 0, 255)).save(os.path.join(frames_dir, "frame_000.png"))
    Image.new("RGBA", (50, 80), (0, 255, 0, 255)).save(os.path.join(frames_dir, "frame_001.png"))
    output = os.path.join(tmp_dir, "sheet.png")
    meta_output = os.path.join(tmp_dir, "sheet.json")
    assemble_sprite_sheet(input_dir=frames_dir, output_path=output, meta_path=meta_output, cols=2, frame_size=(64, 64))
    sheet = Image.open(output)
    assert sheet.size == (128, 64)


def test_meta_format_phaser_compatible(sample_frames, tmp_dir):
    frames_dir, _ = sample_frames
    output = os.path.join(tmp_dir, "sheet.png")
    meta_output = os.path.join(tmp_dir, "sheet.json")
    assemble_sprite_sheet(input_dir=frames_dir, output_path=output, meta_path=meta_output, cols=2, frame_size=(64, 64))
    with open(meta_output) as f:
        meta = json.load(f)
    assert "frames" in meta
    assert "meta" in meta
    assert meta["meta"]["image"] == "sheet.png"
    frame = meta["frames"][0]
    assert "frame" in frame
    assert "sourceSize" in frame
