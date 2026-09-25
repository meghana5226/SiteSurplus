import io
from PIL import Image
from app.services.material_ai import classify_image


def _make_image_bytes(size, color):
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_square_light_image_predicts_tile():
    data = _make_image_bytes((600, 600), (230, 230, 225))
    result = classify_image(data)
    assert result.material_type == "Ceramic Tile"
    assert result.confidence > 0.5


def test_elongated_reddish_image_predicts_brick():
    data = _make_image_bytes((900, 300), (140, 70, 50))
    result = classify_image(data)
    assert result.material_type == "Brick"


def test_grey_rectangular_image_predicts_metal():
    data = _make_image_bytes((500, 350), (120, 125, 135))
    result = classify_image(data)
    assert result.material_type == "Metal Scrap"


def test_malformed_image_bytes_fail_soft_not_crash():
    result = classify_image(b"this is not a valid image file")
    assert result.material_category == "Unknown"
    assert result.confidence == 0.0
