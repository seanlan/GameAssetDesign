import os
from PIL import Image
from game_asset_tools.card_composer import compose_card


def test_compose_card_basic(sample_rgb_image, tmp_dir):
    output = os.path.join(tmp_dir, "card.png")
    compose_card(artwork_path=sample_rgb_image, output_path=output, card_size=(750, 1050), artwork_region=(50, 50, 650, 600))
    card = Image.open(output)
    assert card.size == (750, 1050)


def test_compose_card_with_template(tmp_dir):
    template_path = os.path.join(tmp_dir, "border.png")
    template = Image.new("RGBA", (750, 1050), (50, 50, 50, 255))
    for x in range(50, 700):
        for y in range(50, 650):
            template.putpixel((x, y), (0, 0, 0, 0))
    template.save(template_path)

    artwork_path = os.path.join(tmp_dir, "art.png")
    Image.new("RGB", (300, 300), (255, 0, 0)).save(artwork_path)

    output = os.path.join(tmp_dir, "card.png")
    compose_card(artwork_path=artwork_path, output_path=output, card_size=(750, 1050), artwork_region=(50, 50, 650, 600), template_path=template_path)
    card = Image.open(output)
    assert card.size == (750, 1050)


def test_compose_card_with_text(sample_rgb_image, tmp_dir):
    output = os.path.join(tmp_dir, "card.png")
    compose_card(artwork_path=sample_rgb_image, output_path=output, card_size=(750, 1050), artwork_region=(50, 50, 650, 600), title="Fire Mage", title_region=(50, 660, 650, 60), title_color="#FFFFFF", title_size=28)
    card = Image.open(output)
    assert card.size == (750, 1050)


def test_compose_card_with_description(sample_rgb_image, tmp_dir):
    output = os.path.join(tmp_dir, "card.png")
    compose_card(artwork_path=sample_rgb_image, output_path=output, card_size=(750, 1050), artwork_region=(50, 50, 650, 600), title="Fire Mage", title_region=(50, 660, 650, 60), description="A powerful mage who controls fire magic", desc_region=(50, 740, 650, 200), desc_color="#CCCCCC", desc_size=16, overflow="wrap")
    card = Image.open(output)
    assert card.size == (750, 1050)


def test_compose_card_truncate_long_title(sample_rgb_image, tmp_dir):
    output = os.path.join(tmp_dir, "card.png")
    compose_card(artwork_path=sample_rgb_image, output_path=output, card_size=(750, 1050), artwork_region=(50, 50, 650, 600), title="This Is An Extremely Long Card Title That Should Be Truncated", title_region=(50, 660, 200, 60), title_size=28, overflow="truncate")
    card = Image.open(output)
    assert card.size == (750, 1050)
