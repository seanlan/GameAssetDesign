import os
import json
from PIL import Image
from game_asset_tools.extract import crop_element, extract_elements, validate_elements, load_elements


def _make_test_image(tmp_dir, width=400, height=300):
    img = Image.new("RGBA", (width, height), (200, 200, 200, 255))
    for x in range(50, 150):
        for y in range(50, 150):
            img.putpixel((x, y), (255, 0, 0, 255))
    for x in range(200, 260):
        for y in range(50, 110):
            img.putpixel((x, y), (0, 0, 255, 255))
    path = os.path.join(tmp_dir, "design.png")
    img.save(path)
    return path


def test_crop_element_basic(tmp_dir):
    src_path = _make_test_image(tmp_dir)
    out_path = os.path.join(tmp_dir, "cropped.png")
    crop_element(src_path, out_path, bbox=[50, 50, 150, 150], padding=0)
    result = Image.open(out_path)
    assert result.size == (100, 100)


def test_crop_element_with_padding(tmp_dir):
    src_path = _make_test_image(tmp_dir)
    out_path = os.path.join(tmp_dir, "cropped.png")
    crop_element(src_path, out_path, bbox=[50, 50, 150, 150], padding=10)
    result = Image.open(out_path)
    assert result.size == (120, 120)


def test_crop_element_padding_clamp(tmp_dir):
    src_path = _make_test_image(tmp_dir)
    out_path = os.path.join(tmp_dir, "cropped.png")
    crop_element(src_path, out_path, bbox=[0, 0, 50, 50], padding=100)
    result = Image.open(out_path)
    assert result.size[0] <= 400
    assert result.size[1] <= 300


def test_validate_elements_valid(tmp_dir):
    elements = {
        "source": "test.png", "source_size": [400, 300],
        "layers": {"middle": [{"name": "hero", "type": "character", "bbox": [0, 0, 100, 100]}]},
        "shared_assets": [],
    }
    errors = validate_elements(elements, image_size=(400, 300))
    assert len(errors) == 0


def test_validate_elements_bbox_out_of_bounds(tmp_dir):
    elements = {
        "source": "test.png", "source_size": [400, 300],
        "layers": {"middle": [{"name": "hero", "type": "character", "bbox": [0, 0, 500, 400]}]},
        "shared_assets": [],
    }
    errors = validate_elements(elements, image_size=(400, 300))
    assert len(errors) > 0


def test_validate_elements_missing_name(tmp_dir):
    elements = {
        "source": "test.png", "source_size": [400, 300],
        "layers": {"middle": [{"type": "character", "bbox": [0, 0, 100, 100]}]},
        "shared_assets": [],
    }
    errors = validate_elements(elements, image_size=(400, 300))
    assert len(errors) > 0


def test_load_elements_from_file(tmp_dir):
    elements_dict = {"source": "test.png", "source_size": [400, 300], "layers": {}, "shared_assets": []}
    path = os.path.join(tmp_dir, "elements.json")
    with open(path, "w") as f:
        json.dump(elements_dict, f)
    loaded = load_elements(path)
    assert loaded["source"] == "test.png"


def test_extract_elements_basic(tmp_dir):
    src_path = _make_test_image(tmp_dir)
    out_dir = os.path.join(tmp_dir, "output")
    os.makedirs(out_dir)
    elements = {
        "source": src_path, "source_size": [400, 300],
        "layers": {
            "middle": [{"name": "hero", "type": "character", "bbox": [50, 50, 150, 150], "needs_remove_bg": False, "needs_trim": False}],
            "top": [{"name": "icon_fire", "type": "icon", "bbox": [200, 50, 260, 110], "needs_remove_bg": False, "needs_trim": False}],
        },
        "shared_assets": [],
    }
    results = extract_elements(src_path, elements, out_dir)
    assert len(results) == 2
    assert all(os.path.exists(r["output_path"]) for r in results)


def test_extract_with_trim(tmp_dir):
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    for x in range(80, 120):
        for y in range(80, 120):
            img.putpixel((x, y), (255, 0, 0, 255))
    src_path = os.path.join(tmp_dir, "design.png")
    img.save(src_path)
    out_dir = os.path.join(tmp_dir, "output")
    os.makedirs(out_dir)
    elements = {
        "source": src_path, "source_size": [200, 200],
        "layers": {"middle": [{"name": "item", "type": "icon", "bbox": [60, 60, 140, 140], "needs_remove_bg": False, "needs_trim": True, "trim_padding": 2}]},
        "shared_assets": [],
    }
    results = extract_elements(src_path, elements, out_dir)
    assert len(results) == 1
    result_img = Image.open(results[0]["output_path"])
    assert result_img.size[0] < 80


def test_extract_shared_assets(tmp_dir):
    src_path = _make_test_image(tmp_dir)
    out_dir = os.path.join(tmp_dir, "output")
    os.makedirs(out_dir)
    elements = {
        "source": src_path, "source_size": [400, 300],
        "layers": {"top": [
            {"name": "icon_fire", "type": "icon", "bbox": [200, 50, 260, 110], "uses_shared": ["frame"], "needs_remove_bg": False},
            {"name": "icon_ice", "type": "icon", "bbox": [200, 50, 260, 110], "uses_shared": ["frame"], "needs_remove_bg": False},
        ]},
        "shared_assets": [{"name": "frame", "type": "ui", "bbox": [200, 50, 260, 110], "reuse_count": 2}],
    }
    results = extract_elements(src_path, elements, out_dir)
    shared_results = [r for r in results if r.get("is_shared")]
    assert len(shared_results) == 1
    assert "shared" in shared_results[0]["output_path"]


def test_extract_bottom_layer_flagged(tmp_dir):
    src_path = _make_test_image(tmp_dir)
    out_dir = os.path.join(tmp_dir, "output")
    os.makedirs(out_dir)
    elements = {
        "source": src_path, "source_size": [400, 300],
        "layers": {"bottom": [{"name": "bg", "type": "background", "bbox": [0, 0, 400, 300], "needs_inpaint": True, "inpaint_prompt": "Remove characters"}]},
        "shared_assets": [],
    }
    results = extract_elements(src_path, elements, out_dir)
    bg_results = [r for r in results if r["type"] == "background"]
    assert len(bg_results) == 1
    assert bg_results[0].get("needs_inpaint") is True
    assert os.path.exists(bg_results[0]["output_path"])
