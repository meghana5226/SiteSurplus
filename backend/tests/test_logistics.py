from app.services.logistics import haversine_km, estimate_logistics
from app.services.geodata import lookup_coordinates, CITY_COORDINATES


def test_haversine_same_point_is_zero():
    assert haversine_km(17.38, 78.48, 17.38, 78.48) == 0.0


def test_haversine_known_city_pair_is_realistic():
    hyd = lookup_coordinates("Hyderabad")
    blr = lookup_coordinates("Bangalore")
    d = haversine_km(*hyd, *blr)
    assert 480 <= d <= 520  # real-world distance is ~500km


def test_lookup_coordinates_case_insensitive():
    assert lookup_coordinates("HYDERABAD") == lookup_coordinates("hyderabad")


def test_lookup_unknown_city_returns_none():
    assert lookup_coordinates("Atlantis") == (None, None)


def test_estimate_logistics_zero_distance_still_has_base_fee():
    hyd = lookup_coordinates("Hyderabad")
    est = estimate_logistics(*hyd, *hyd, "flooring", 100)
    assert est.distance_km == 0.0
    assert est.estimated_transport_cost_inr >= 500.0  # base fee floor


def test_estimate_logistics_missing_coordinates_defaults_distance_zero():
    est = estimate_logistics(None, None, 17.38, 78.48, "flooring", 100)
    assert est.distance_km == 0.0


def test_all_seed_cities_have_coordinates():
    for city in ["hyderabad", "bangalore", "mumbai", "pune", "delhi"]:
        assert CITY_COORDINATES.get(city) is not None
