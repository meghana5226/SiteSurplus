"""
Small fixed city -> (latitude, longitude) lookup.

Standing in for a real geocoding API call (e.g. Google Maps Geocoding API,
Mapbox) so the project runs with zero API keys. Swapping this for a real
geocoding call is a one-function change -- see logistics.py.
"""

CITY_COORDINATES = {
    "hyderabad": (17.3850, 78.4867),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "mumbai": (19.0760, 72.8777),
    "pune": (18.5204, 73.8567),
    "delhi": (28.7041, 77.1025),
    "kolkata": (22.5726, 88.3639),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873),
}


def lookup_coordinates(city: str):
    """Returns (lat, lon) or (None, None) if the city isn't in our demo lookup."""
    key = city.strip().lower()
    if key in CITY_COORDINATES:
        return CITY_COORDINATES[key]
    return (None, None)
