import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app import models, schemas
from app.services.geodata import lookup_coordinates
from app.services.material_ai import classify_image

router = APIRouter(prefix="/api/listings", tags=["listings"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("", response_model=schemas.ListingOut)
def create_listing(payload: schemas.ListingCreate, db: Session = Depends(get_db)):
    lat, lon = lookup_coordinates(payload.location_city)
    listing = models.Listing(**payload.model_dump(), latitude=lat, longitude=lon)
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("", response_model=List[schemas.ListingOut])
def list_listings(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Listing)
    if status:
        query = query.filter(models.Listing.status == status)
    return query.order_by(models.Listing.created_at.desc()).all()


@router.get("/{listing_id}", response_model=schemas.ListingOut)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.get(models.Listing, listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")
    return listing


@router.post("/{listing_id}/images")
async def upload_listing_image(listing_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    listing = db.get(models.Listing, listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")

    image_bytes = await file.read()

    # Run the (heuristic) material AI on the uploaded photo. This is a
    # SUGGESTION only -- the frontend shows it to the user to confirm before
    # anything about the listing itself changes, per the "AI is not the
    # source of truth" design principle.
    prediction = classify_image(image_bytes)

    ext = os.path.splitext(file.filename or "upload.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)

    image = models.ListingImage(
        listing_id=listing_id,
        image_path=f"/static/uploads/{filename}",
        ai_predicted_category=f"{prediction.material_category} / {prediction.material_type}",
        ai_confidence=prediction.confidence,
    )
    db.add(image)
    db.commit()
    db.refresh(image)

    return {
        "image": schemas.ListingImageOut.model_validate(image),
        "ai_prediction": {
            "material_category": prediction.material_category,
            "material_type": prediction.material_type,
            "confidence": prediction.confidence,
            "dominant_color": prediction.dominant_color,
            "reasoning": prediction.reasoning,
        },
    }
