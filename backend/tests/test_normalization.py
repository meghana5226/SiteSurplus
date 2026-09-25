from app.services.normalization import normalize_description


def test_dimension_with_explicit_mm():
    r = normalize_description("600x600 ceramic tile")
    assert r.length_mm == 600.0 and r.width_mm == 600.0
    assert r.material_type == "Ceramic Tile"


def test_dimension_bare_small_numbers_assumed_feet():
    r = normalize_description("2x2 ceramic flooring")
    assert abs(r.length_mm - 609.6) < 0.1


def test_dimension_with_inches():
    r = normalize_description("24x24 inch marble tile")
    assert abs(r.length_mm - 609.6) < 0.1
    assert r.material_type == "Marble Slab"


def test_square_shorthand():
    r = normalize_description("600 sq tile")
    assert r.length_mm == 600.0 and r.width_mm == 600.0


def test_unrecognized_material_returns_none():
    r = normalize_description("some random item with no keyword and 100x200")
    assert r.material_category is None
    assert r.length_mm == 100.0
