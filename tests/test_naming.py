from game_asset_tools.naming import generate_filename, find_next_variant


def test_generate_filename_basic():
    result = generate_filename(
        template="{type}_{name}_{size}_{variant}",
        asset_type="character",
        name="fire_mage",
        size="512",
        variant="v1",
    )
    assert result == "char_fire_mage_512_v1.png"


def test_generate_filename_with_action():
    result = generate_filename(
        template="{type}_{name}_{action}_{size}",
        asset_type="sprite",
        name="warrior",
        size="128x128",
        action="walk",
    )
    assert result == "sprite_warrior_walk_128x128.png"


def test_generate_filename_with_timestamp():
    result = generate_filename(
        template="{type}_{name}_{timestamp}",
        asset_type="icon",
        name="potion",
        timestamp="20260326_143022",
    )
    assert result == "icon_potion_20260326_143022.png"


def test_type_abbreviation():
    result = generate_filename(
        template="{type}_{name}",
        asset_type="character",
        name="test",
    )
    assert result.startswith("char_")


def test_type_abbreviation_background():
    result = generate_filename(
        template="{type}_{name}",
        asset_type="background",
        name="forest",
    )
    assert result.startswith("bg_")


def test_find_next_variant(tmp_dir):
    import os
    open(os.path.join(tmp_dir, "char_mage_512_v1.png"), "w").close()
    open(os.path.join(tmp_dir, "char_mage_512_v2.png"), "w").close()
    variant = find_next_variant(tmp_dir, "char_mage_512")
    assert variant == "v3"


def test_find_next_variant_no_existing(tmp_dir):
    variant = find_next_variant(tmp_dir, "char_mage_512")
    assert variant == "v1"
