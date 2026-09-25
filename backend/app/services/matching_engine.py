"""
Matching engine.

Deterministic, auditable weighted scoring -- intentionally NOT an LLM or a
black-box ML model, so every match score can be explained field-by-field to
the user (see the design note in the spec about matching staying your own
algorithm before you ever consider ML). Weights match the spec exactly:

    30% material compatibility
    20% dimension compatibility
    15% quantity compatibility
    15% condition compatibility
    10% distance
    10% availability

Each sub-score is 0.0-1.0; the final score is a weighted sum, also 0.0-1.0
(displayed to the user as a percentage).
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

WEIGHTS = {
    "material": 0.30,
    "dimension": 0.20,
    "quantity": 0.15,
    "condition": 0.15,
    "distance": 0.10,
    "availability": 0.10,
}

# Distance beyond which the distance score bottoms out at 0 (demo constant;
# tune per real logistics economics, e.g. distance where transport cost
# exceeds the material's value).
MAX_USEFUL_DISTANCE_KM = 300.0

# Condition compatibility: how well a listing's condition satisfies a
# requirement's condition. 1.0 = fully satisfies, lower = partial.
CONDITION_RANK = {"unused": 3, "good": 2, "fair": 1}


@dataclass
class MatchBreakdown:
    material_score: float
    dimension_score: float
    quantity_score: float
    condition_score: float
    distance_score: float
    availability_score: float
    distance_km: float
    overall_score: float


def score_material(listing_category: str, listing_type: str, req_category: str, req_type: str) -> float:
    if listing_type.strip().lower() == req_type.strip().lower():
        return 1.0
    if listing_category.strip().lower() == req_category.strip().lower():
        return 0.6
    return 0.0


def score_dimension(l_len: Optional[float], l_wid: Optional[float],
                     r_len: Optional[float], r_wid: Optional[float]) -> float:
    if not all([l_len, l_wid, r_len, r_wid]):
        return 0.5  # unknown dimensions on either side -> neutral score
    len_diff = abs(l_len - r_len) / max(r_len, 1)
    wid_diff = abs(l_wid - r_wid) / max(r_wid, 1)
    avg_diff = (len_diff + wid_diff) / 2
    # Within 2% -> perfect; scales down linearly to 0 at 25% difference
    if avg_diff <= 0.02:
        return 1.0
    if avg_diff >= 0.25:
        return 0.0
    return round(1.0 - (avg_diff - 0.02) / (0.25 - 0.02), 3)


def score_quantity(available_qty: float, required_qty: float) -> float:
    if required_qty <= 0:
        return 0.0
    if available_qty >= required_qty:
        return 1.0
    # Partial fulfillment scores proportionally
    return round(max(0.0, available_qty / required_qty), 3)


def score_condition(listing_condition: str, required_condition: str) -> float:
    l_rank = CONDITION_RANK.get(listing_condition.strip().lower(), 1)
    r_rank = CONDITION_RANK.get(required_condition.strip().lower(), 1)
    if l_rank >= r_rank:
        return 1.0
    # One tier below what's required still has some value
    diff = r_rank - l_rank
    return max(0.0, 1.0 - diff * 0.5)


def score_distance(distance_km: Optional[float]) -> float:
    if distance_km is None:
        return 0.5  # unknown location on either side -> neutral score
    if distance_km <= 0:
        return 1.0
    if distance_km >= MAX_USEFUL_DISTANCE_KM:
        return 0.0
    return round(1.0 - (distance_km / MAX_USEFUL_DISTANCE_KM), 3)


def score_availability(available_until: datetime, required_by: datetime) -> float:
    if available_until >= required_by:
        return 1.0
    # Available window closes before it's needed -- partial credit shrinks
    # the further past the deadline the material would arrive.
    days_late = (required_by - available_until).days
    return max(0.0, 1.0 - days_late * 0.1)


def compute_match(
    *,
    listing_category: str, listing_type: str,
    listing_length_mm: Optional[float], listing_width_mm: Optional[float],
    listing_quantity: float, listing_condition: str,
    listing_available_until: datetime,
    req_category: str, req_type: str,
    req_length_mm: Optional[float], req_width_mm: Optional[float],
    req_quantity: float, req_condition: str, req_required_by: datetime,
    distance_km: Optional[float],
) -> MatchBreakdown:
    material_score = score_material(listing_category, listing_type, req_category, req_type)
    dimension_score = score_dimension(listing_length_mm, listing_width_mm, req_length_mm, req_width_mm)
    quantity_score = score_quantity(listing_quantity, req_quantity)
    condition_score = score_condition(listing_condition, req_condition)
    distance_score = score_distance(distance_km)
    availability_score = score_availability(listing_available_until, req_required_by)

    overall = (
        material_score * WEIGHTS["material"]
        + dimension_score * WEIGHTS["dimension"]
        + quantity_score * WEIGHTS["quantity"]
        + condition_score * WEIGHTS["condition"]
        + distance_score * WEIGHTS["distance"]
        + availability_score * WEIGHTS["availability"]
    )

    return MatchBreakdown(
        material_score=material_score,
        dimension_score=dimension_score,
        quantity_score=quantity_score,
        condition_score=condition_score,
        distance_score=distance_score,
        availability_score=availability_score,
        distance_km=distance_km or 0.0,
        overall_score=round(overall, 4),
    )
