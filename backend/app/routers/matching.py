from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services.matching_engine import compute_match
from app.services.logistics import haversine_km

router = APIRouter(prefix="/api/matching", tags=["matching"])


@router.post("/run/{requirement_id}", response_model=List[schemas.MatchOut])
def run_matching(requirement_id: int, db: Session = Depends(get_db)):
    """
    Computes match scores between one requirement and every AVAILABLE
    listing, persists the results, and returns them sorted best-first.
    Re-running for the same requirement replaces its previous matches.
    """
    requirement = db.get(models.Requirement, requirement_id)
    if not requirement:
        raise HTTPException(404, "Requirement not found")

    # Clear previous matches for this requirement so re-running is idempotent
    db.query(models.Match).filter(models.Match.requirement_id == requirement_id).delete()

    listings = db.query(models.Listing).filter(models.Listing.status == models.ListingStatus.AVAILABLE).all()

    created_matches = []
    for listing in listings:
        distance_km = None
        if all([listing.latitude, listing.longitude, requirement.latitude, requirement.longitude]):
            distance_km = haversine_km(listing.latitude, listing.longitude, requirement.latitude, requirement.longitude)

        breakdown = compute_match(
            listing_category=listing.material_category, listing_type=listing.material_type,
            listing_length_mm=listing.dimension_length_mm, listing_width_mm=listing.dimension_width_mm,
            listing_quantity=listing.quantity, listing_condition=listing.condition,
            listing_available_until=listing.available_until,
            req_category=requirement.material_category, req_type=requirement.material_type,
            req_length_mm=requirement.dimension_length_mm, req_width_mm=requirement.dimension_width_mm,
            req_quantity=requirement.quantity, req_condition=requirement.condition,
            req_required_by=requirement.required_by,
            distance_km=distance_km,
        )

        # Only persist matches with a meaningful score (>10%) to avoid noise
        if breakdown.overall_score < 0.10:
            continue

        match = models.Match(
            listing_id=listing.id,
            requirement_id=requirement.id,
            score=breakdown.overall_score,
            material_score=breakdown.material_score,
            dimension_score=breakdown.dimension_score,
            quantity_score=breakdown.quantity_score,
            condition_score=breakdown.condition_score,
            distance_score=breakdown.distance_score,
            availability_score=breakdown.availability_score,
            distance_km=breakdown.distance_km,
        )
        db.add(match)
        created_matches.append(match)

    db.commit()
    for m in created_matches:
        db.refresh(m)

    created_matches.sort(key=lambda m: m.score, reverse=True)
    return created_matches


@router.get("/for-requirement/{requirement_id}", response_model=List[schemas.MatchOut])
def get_matches_for_requirement(requirement_id: int, db: Session = Depends(get_db)):
    matches = (
        db.query(models.Match)
        .filter(models.Match.requirement_id == requirement_id)
        .order_by(models.Match.score.desc())
        .all()
    )
    return matches
