from datetime import datetime
from app.services.matching_engine import (
    score_material, score_dimension, score_quantity, score_condition,
    score_distance, score_availability, compute_match,
)


def test_score_material_exact_type_match():
    assert score_material("Flooring", "Ceramic Tile", "Flooring", "Ceramic Tile") == 1.0


def test_score_material_category_only_match():
    assert score_material("Flooring", "Vitrified Tile", "Flooring", "Ceramic Tile") == 0.6


def test_score_material_no_match():
    assert score_material("Flooring", "Ceramic Tile", "Metal", "Steel Bar") == 0.0


def test_score_dimension_exact():
    assert score_dimension(600, 600, 600, 600) == 1.0


def test_score_dimension_far_off():
    assert score_dimension(600, 600, 100, 100) == 0.0


def test_score_quantity_sufficient():
    assert score_quantity(120, 100) == 1.0


def test_score_quantity_insufficient_is_proportional():
    assert score_quantity(50, 100) == 0.5


def test_score_condition_exceeds_requirement():
    assert score_condition("Unused", "Good") == 1.0


def test_score_condition_below_requirement():
    assert score_condition("Fair", "Unused") < 1.0


def test_score_distance_zero_is_perfect():
    assert score_distance(0) == 1.0


def test_score_distance_beyond_max_is_zero():
    assert score_distance(1000) == 0.0


def test_score_availability_in_time():
    assert score_availability(datetime(2026, 9, 30), datetime(2026, 9, 25)) == 1.0


def test_score_availability_too_late():
    assert score_availability(datetime(2026, 9, 20), datetime(2026, 9, 25)) < 1.0


def test_compute_match_perfect_scenario_scores_near_one():
    result = compute_match(
        listing_category="Flooring", listing_type="Ceramic Tile",
        listing_length_mm=600, listing_width_mm=600,
        listing_quantity=120, listing_condition="Unused",
        listing_available_until=datetime(2026, 9, 30),
        req_category="Flooring", req_type="Ceramic Tile",
        req_length_mm=600, req_width_mm=600,
        req_quantity=100, req_condition="Unused",
        req_required_by=datetime(2026, 9, 25),
        distance_km=0,
    )
    assert result.overall_score > 0.95


def test_compute_match_weights_sum_to_one():
    from app.services.matching_engine import WEIGHTS
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9
