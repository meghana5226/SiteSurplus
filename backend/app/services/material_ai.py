"""
Material identification from an uploaded photo.

This is a lightweight, genuinely-computed heuristic classifier -- it reads
real pixel data (dominant color + aspect ratio) with Pillow and maps that to
a material category with a confidence score. It is explicitly NOT a trained
neural network, and is designed to be replaced: swap `classify_image` for a
call to a real vision model (a fine-tuned ResNet/EfficientNet classifier, or
a hosted vision API) without changing anything else in the pipeline, since
callers only depend on this function's (category, material_type, confidence)
return shape.

Per the design principle in the spec: this prediction is always shown to the
user as a *suggestion* they must confirm -- it is never written to the
listing directly. See routers/listings.py.
"""
from dataclasses import dataclass
from typing import Optional
from PIL import Image
import io


@dataclass
class MaterialPrediction:
    material_category: str
    material_type: str
    confidence: float
    dominant_color: str
    reasoning: str


def _dominant_color_name(img: Image.Image) -> tuple[str, tuple]:
    small = img.convert("RGB").resize((50, 50))
    colors = small.getcolors(50 * 50)
    colors.sort(key=lambda c: c[0], reverse=True)
    _, (r, g, b) = colors[0]

    brightness = (r + g + b) / 3
    if brightness > 200:
        name = "white/light"
    elif brightness < 60:
        name = "black/dark"
    elif r > g and r > b and r - b > 40:
        name = "red/brown"
    elif g > r and g > b:
        name = "green"
    elif b > r and b > g:
        name = "blue/grey"
    elif abs(r - g) < 20 and abs(g - b) < 20:
        name = "grey"
    else:
        name = "mixed"

    return name, (r, g, b)


def classify_image(image_bytes: bytes) -> MaterialPrediction:
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.load()  # force full decode now so any corruption is caught here, not later
    except Exception:
        # Malformed/partial image data (e.g. an unsupported format or a
        # truncated upload) -- fail soft with a low-confidence fallback
        # rather than 500ing the whole request. The user still confirms
        # the material fields manually either way.
        return MaterialPrediction(
            material_category="Unknown",
            material_type="Unknown",
            confidence=0.0,
            dominant_color="unknown",
            reasoning="Could not analyze this image automatically. Please fill in the material details manually.",
        )

    width, height = img.size
    aspect_ratio = width / height if height else 1.0

    color_name, rgb = _dominant_color_name(img)

    # Simple heuristic rule set. Real system: replace with a trained classifier.
    if 0.85 <= aspect_ratio <= 1.18:
        if color_name in ("white/light", "grey"):
            category, mtype, confidence = "Flooring", "Ceramic Tile", 0.78
            reasoning = "Near-square image with light/neutral tone is commonly a tile photo."
        else:
            category, mtype, confidence = "Flooring", "Tile", 0.55
            reasoning = "Near-square aspect ratio suggests a tile, color inconclusive."
    elif aspect_ratio > 1.6 or aspect_ratio < 0.63:
        if color_name in ("red/brown",):
            category, mtype, confidence = "Structural", "Brick", 0.70
            reasoning = "Elongated shape with reddish-brown tone suggests brick or timber."
        else:
            category, mtype, confidence = "Carpentry", "Wood Panel", 0.52
            reasoning = "Elongated aspect ratio suggests a plank/panel shape."
    else:
        if color_name in ("blue/grey", "grey"):
            category, mtype, confidence = "Metal", "Metal Scrap", 0.60
            reasoning = "Grey/blue-grey tone in a moderately rectangular photo suggests metal."
        else:
            category, mtype, confidence = "Structural", "Concrete Block", 0.50
            reasoning = "Rectangular shape, neutral confidence fallback to concrete/masonry."

    return MaterialPrediction(
        material_category=category,
        material_type=mtype,
        confidence=confidence,
        dominant_color=color_name,
        reasoning=reasoning,
    )
