from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models
from app.services.logistics import get_material_profile

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    confirmations = (
        db.query(models.ReuseConfirmation, models.Transaction, models.Match, models.Listing)
        .join(models.Transaction, models.ReuseConfirmation.transaction_id == models.Transaction.id)
        .join(models.Match, models.Transaction.match_id == models.Match.id)
        .join(models.Listing, models.Match.listing_id == models.Listing.id)
        .all()
    )

    materials_reused_units = 0.0
    waste_diverted_kg = 0.0
    project_pairs = set()

    for confirmation, tx, match, listing in confirmations:
        materials_reused_units += confirmation.quantity_confirmed
        profile = get_material_profile(listing.material_category)
        waste_diverted_kg += confirmation.quantity_confirmed * profile["unit_weight_kg"]
        project_pairs.add((match.listing_id, match.requirement_id))

    active_listings = db.query(models.Listing).filter(
        models.Listing.status == models.ListingStatus.AVAILABLE
    ).count()
    open_requirements = db.query(models.Requirement).count()

    return {
        "materials_reused_units": round(materials_reused_units, 2),
        "waste_diverted_kg": round(waste_diverted_kg, 2),
        "projects_connected": len(project_pairs),
        "active_listings": active_listings,
        "open_requirements": open_requirements,
    }
