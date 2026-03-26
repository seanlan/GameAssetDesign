import os
import json
from PIL import Image
from game_asset_tools.annotate import annotate_image, TYPE_COLORS


def _make_elements(layers=None, shared=None):
    return {
        "source": "test.png",
        "source_size": [400, 300],
        "layers": layers or {},
        "shared_assets": shared or [],
    }


def test_annotate_basic(tmp_dir):
    src = Image.new("RGB", (400, 300), (200, 200, 200))
    src_path = os.path.join(tmp_dir, "source.png")
    src.save(src_path)
    elements = _make_elements(
        layers={
            "top": [{"name": "btn_attack", "type": "ui", "bbox": [50, 200, 200, 250]}],
            "middle": [{"name": "hero", "type": "character", "bbox": [100, 50, 300, 280]}],
        }
    )
    elements_path = os.path.join(tmp_dir, "elements.json")
    with open(elements_path, "w") as f:
        json.dump(elements, f)
    out_path = os.path.join(tmp_dir, "annotated.png")
    annotate_image(src_path, elements_path, out_path)
    assert os.path.exists(out_path)
    result = Image.open(out_path)
    assert result.size == (400, 300)


def test_annotate_with_shared_assets(tmp_dir):
    src = Image.new("RGB", (400, 300), (200, 200, 200))
    src_path = os.path.join(tmp_dir, "source.png")
    src.save(src_path)
    elements = _make_elements(
        layers={"top": [
            {"name": "icon_fire", "type": "icon", "bbox": [10, 10, 74, 74], "uses_shared": ["frame"]},
            {"name": "icon_ice", "type": "icon", "bbox": [80, 10, 144, 74], "uses_shared": ["frame"]},
        ]},
        shared=[{"name": "frame", "type": "ui", "bbox": [10, 10, 74, 74], "reuse_count": 2}],
    )
    elements_path = os.path.join(tmp_dir, "elements.json")
    with open(elements_path, "w") as f:
        json.dump(elements, f)
    out_path = os.path.join(tmp_dir, "annotated.png")
    annotate_image(src_path, elements_path, out_path)
    assert os.path.exists(out_path)


def test_annotate_empty_elements(tmp_dir):
    src = Image.new("RGB", (200, 200), (100, 100, 100))
    src_path = os.path.join(tmp_dir, "source.png")
    src.save(src_path)
    elements = _make_elements()
    elements_path = os.path.join(tmp_dir, "elements.json")
    with open(elements_path, "w") as f:
        json.dump(elements, f)
    out_path = os.path.join(tmp_dir, "annotated.png")
    annotate_image(src_path, elements_path, out_path)
    assert os.path.exists(out_path)


def test_type_colors_defined():
    for t in ["character", "icon", "ui", "background", "shared"]:
        assert t in TYPE_COLORS


def test_annotate_from_dict(tmp_dir):
    src = Image.new("RGB", (200, 200), (150, 150, 150))
    src_path = os.path.join(tmp_dir, "source.png")
    src.save(src_path)
    elements = _make_elements(
        layers={"middle": [{"name": "item", "type": "icon", "bbox": [10, 10, 60, 60]}]}
    )
    out_path = os.path.join(tmp_dir, "annotated.png")
    annotate_image(src_path, elements, out_path)
    assert os.path.exists(out_path)
