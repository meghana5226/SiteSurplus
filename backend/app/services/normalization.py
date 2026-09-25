"""
Description normalization.

Turns free-text material descriptions like:
    "600 sq tile"
    "600x600 ceramic tile"
    "2x2 ceramic flooring"
    "24x24 inch tile"

into structured (material_category, material_type, length_mm, width_mm) so
listings and requirements can be compared on a consistent basis regardless
of how a user phrases them.

This is a deterministic regex + lookup-table normalizer -- intentionally NOT
an LLM call, per the design principle that the matching pipeline should
stay auditable and reproducible. A real deployment could add an LLM-based
fallback for descriptions this parser can't handle, but every field it
returns should still be shown to the user for confirmation before being
trusted (see the design note about not letting AI become the source of
truth).
"""
import re
from dataclasses import dataclass
from typing import Optional

# unit -> multiplier to convert to millimeters
UNIT_TO_MM = {
    "mm": 1.0,
    "cm": 10.0,
    "m": 1000.0,
    "in": 25.4,
    "inch": 25.4,
    "inches": 25.4,
    "ft": 304.8,
    "feet": 304.8,
}

MATERIAL_KEYWORDS = {
    "ceramic": ("Flooring", "Ceramic Tile"),
    "vitrified": ("Flooring", "Vitrified Tile"),
    "marble": ("Flooring", "Marble Slab"),
    "granite": ("Flooring", "Granite Slab"),
    "tile": ("Flooring", "Tile"),
    "brick": ("Structural", "Brick"),
    "concrete": ("Structural", "Concrete Block"),
    "block": ("Structural", "Concrete Block"),
    "wood": ("Carpentry", "Wood Panel"),
    "plywood": ("Carpentry", "Plywood Sheet"),
    "steel": ("Metal", "Steel Bar"),
    "metal": ("Metal", "Metal Scrap"),
    "glass": ("Glazing", "Glass Panel"),
    "pipe": ("Plumbing", "PVC Pipe"),
    "wire": ("Electrical", "Electrical Wire"),
}

# Matches things like "600x600", "600 x 600 mm", "24x24 inch", "2x2 ft"
DIMENSION_PATTERN = re.compile(
    r"(?P<a>\d+(?:\.\d+)?)\s*(?:x|×|by)\s*(?P<b>\d+(?:\.\d+)?)\s*(?P<unit>mm|cm|m|in|inch|inches|ft|feet)?",
    re.IGNORECASE,
)

# Matches "600 sq" style single-dimension-implies-square descriptions
SQUARE_PATTERN = re.compile(
    r"(?P<a>\d+(?:\.\d+)?)\s*(?:sq|square)\b\s*(?P<unit>mm|cm|m|in|inch|inches|ft|feet)?",
    re.IGNORECASE,
)


@dataclass
class NormalizedDescription:
    material_category: Optional[str]
    material_type: Optional[str]
    length_mm: Optional[float]
    width_mm: Optional[float]
    raw_text: str


def normalize_description(text: str) -> NormalizedDescription:
    text_lower = text.lower()

    # 1. Material lookup - first matching keyword wins (checked in insertion order,
    #    with more specific keywords like "vitrified" listed before generic "tile")
    material_category, material_type = None, None
    for keyword, (category, mtype) in MATERIAL_KEYWORDS.items():
        if keyword in text_lower:
            material_category, material_type = category, mtype
            break

    # 2. Dimension extraction
    length_mm, width_mm = None, None

    dim_match = DIMENSION_PATTERN.search(text_lower)
    if dim_match:
        a_val = float(dim_match.group("a"))
        b_val = float(dim_match.group("b"))
        unit = dim_match.group("unit")
        if unit:
            multiplier = UNIT_TO_MM.get(unit.lower(), 1.0)
        else:
            # No unit given. Construction material dimensions with small
            # numbers (< 20) are conventionally expressed in feet (e.g. a
            # "2x2" tile means 2ft x 2ft => ~600x600mm, a very common tile
            # size), while larger bare numbers are conventionally mm.
            multiplier = UNIT_TO_MM["ft"] if max(a_val, b_val) < 20 else 1.0
        length_mm = a_val * multiplier
        width_mm = b_val * multiplier
    else:
        sq_match = SQUARE_PATTERN.search(text_lower)
        if sq_match:
            unit = sq_match.group("unit") or "mm"
            multiplier = UNIT_TO_MM.get(unit.lower(), 1.0)
            side = float(sq_match.group("a")) * multiplier
            length_mm, width_mm = side, side

    return NormalizedDescription(
        material_category=material_category,
        material_type=material_type,
        length_mm=round(length_mm, 1) if length_mm else None,
        width_mm=round(width_mm, 1) if width_mm else None,
        raw_text=text,
    )
