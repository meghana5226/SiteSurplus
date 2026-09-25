"""
Logistics calculations.

Distance is computed with the Haversine formula (real spherical-earth great
circle distance from lat/lon), NOT a straight-line Euclidean approximation --
appropriate for the city-to-city distances this demo deals with. For a
production system you would swap `haversine_km` for a call to a real routing
API (Google Maps Distance Matrix, Mapbox Directions, OSRM) to get actual
road distance/time -- the call site (`estimate_logistics`) is written so
that's a one-function swap.

Transport cost and material value use simple, clearly-documented example
rates; a real deployment would price these from actual freight-rate data
and category-specific market values.
"""
import math
from dataclasses import dataclass
from typing import Optional

# Example flat rates -- tune these to real freight-rate data in production.
BASE_TRANSPORT_FEE_INR = 500.0
PER_KM_PER_TON_RATE_INR = 18.0

# Rough density/value assumptions per material category, used only for demo
# cost/weight estimates. Replace with real catalog pricing in production.
MATERIAL_PROFILES = {
    "flooring":       {"unit_weight_kg": 3.5,  "unit_value_inr": 45.0},
    "bricks":         {"unit_weight_kg": 3.0,  "unit_value_inr": 8.0},
    "concrete":       {"unit_weight_kg": 25.0, "unit_value_inr": 6.0},
    "metal":          {"unit_weight_kg": 8.0,  "unit_value_inr": 55.0},
    "wood":           {"unit_weight_kg": 5.0,  "unit_value_inr": 60.0},
    "glass":          {"unit_weight_kg": 4.0,  "unit_value_inr": 30.0},
    "plumbing":       {"unit_weight_kg": 1.5,  "unit_value_inr": 90.0},
    "electrical":     {"unit_weight_kg": 0.5,  "unit_value_inr": 70.0},
}
DEFAULT_PROFILE = {"unit_weight_kg": 2.0, "unit_value_inr": 20.0}


@dataclass
class LogisticsEstimate:
    distance_km: float
    estimated_weight_kg: float
    estimated_transport_cost_inr: float
    estimated_material_value_inr: float
    estimated_total_inr: float


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in kilometers."""
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def get_material_profile(material_category: str) -> dict:
    return MATERIAL_PROFILES.get(material_category.strip().lower(), DEFAULT_PROFILE)


def estimate_logistics(
    supplier_lat: Optional[float], supplier_lon: Optional[float],
    requester_lat: Optional[float], requester_lon: Optional[float],
    material_category: str, quantity: float,
) -> LogisticsEstimate:
    if None in (supplier_lat, supplier_lon, requester_lat, requester_lon):
        distance_km = 0.0
    else:
        distance_km = haversine_km(supplier_lat, supplier_lon, requester_lat, requester_lon)

    profile = get_material_profile(material_category)
    weight_kg = quantity * profile["unit_weight_kg"]
    weight_tons = weight_kg / 1000.0

    transport_cost = BASE_TRANSPORT_FEE_INR + (PER_KM_PER_TON_RATE_INR * distance_km * max(weight_tons, 0.05))
    material_value = quantity * profile["unit_value_inr"]

    return LogisticsEstimate(
        distance_km=distance_km,
        estimated_weight_kg=round(weight_kg, 2),
        estimated_transport_cost_inr=round(transport_cost, 2),
        estimated_material_value_inr=round(material_value, 2),
        estimated_total_inr=round(transport_cost + material_value, 2),
    )
