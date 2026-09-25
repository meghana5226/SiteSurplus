"""
Seeds the database with realistic demo data spanning the whole flow:
listings, requirements, a computed match, and one fully-completed
transaction with a reuse confirmation -- so the dashboard has real
numbers to show immediately.

Run with:  python -m app.seed
"""
from datetime import datetime, timedelta
from app.database import SessionLocal, Base, engine
from app import models
from app.services.geodata import lookup_coordinates
from app.services.matching_engine import compute_match
from app.services.logistics import estimate_logistics

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()

    # Wipe existing demo data for idempotent re-seeding
    for model in [models.ReuseConfirmation, models.Transaction, models.Match,
                  models.ListingImage, models.Listing, models.Requirement]:
        db.query(model).delete()
    db.commit()

    now = datetime(2026, 9, 18)

    listings_data = [
        dict(supplier_name="Site A - Gachibowli Tower", material_category="Flooring",
             material_type="Ceramic Tile", quantity=120, unit="Pieces",
             dimension_length_mm=600, dimension_width_mm=600, condition="Unused",
             color="White", location_city="Hyderabad", available_until=now + timedelta(days=12)),
        dict(supplier_name="Site B - Kondapur Complex", material_category="Structural",
             material_type="Brick", quantity=2000, unit="Pieces",
             dimension_length_mm=230, dimension_width_mm=110, condition="Good",
             color="Red", location_city="Hyderabad", available_until=now + timedelta(days=20)),
        dict(supplier_name="Site C - Whitefield Yard", material_category="Metal",
             material_type="Metal Scrap", quantity=500, unit="kg",
             dimension_length_mm=None, dimension_width_mm=None, condition="Fair",
             color="Grey", location_city="Bangalore", available_until=now + timedelta(days=8)),
        dict(supplier_name="Site D - Andheri Project", material_category="Carpentry",
             material_type="Plywood Sheet", quantity=80, unit="Sheets",
             dimension_length_mm=2440, dimension_width_mm=1220, condition="Unused",
             color="Brown", location_city="Mumbai", available_until=now + timedelta(days=15)),
        dict(supplier_name="Site E - Hitech City Annex", material_category="Flooring",
             material_type="Vitrified Tile", quantity=60, unit="Pieces",
             dimension_length_mm=600, dimension_width_mm=600, condition="Unused",
             color="Beige", location_city="Hyderabad", available_until=now + timedelta(days=5)),
    ]

    listings = []
    for data in listings_data:
        lat, lon = lookup_coordinates(data["location_city"])
        listing = models.Listing(**data, latitude=lat, longitude=lon)
        db.add(listing)
        listings.append(listing)
    db.commit()
    for l in listings:
        db.refresh(l)

    requirements_data = [
        dict(requester_name="Site X - Madhapur Build", material_category="Flooring",
             material_type="Ceramic Tile", quantity=100, unit="Pieces",
             dimension_length_mm=600, dimension_width_mm=600, condition="Unused",
             location_city="Hyderabad", required_by=now + timedelta(days=7)),
        dict(requester_name="Site Y - Powai Residency", material_category="Carpentry",
             material_type="Plywood Sheet", quantity=50, unit="Sheets",
             dimension_length_mm=2440, dimension_width_mm=1220, condition="Good",
             location_city="Mumbai", required_by=now + timedelta(days=10)),
    ]
    requirements = []
    for data in requirements_data:
        lat, lon = lookup_coordinates(data["location_city"])
        requirement = models.Requirement(**data, latitude=lat, longitude=lon)
        db.add(requirement)
        requirements.append(requirement)
    db.commit()
    for r in requirements:
        db.refresh(r)

    # Compute matches for requirement 1 (tiles) against all listings
    req = requirements[0]
    from app.services.logistics import haversine_km
    for listing in listings:
        distance_km = None
        if all([listing.latitude, listing.longitude, req.latitude, req.longitude]):
            distance_km = haversine_km(listing.latitude, listing.longitude, req.latitude, req.longitude)
        breakdown = compute_match(
            listing_category=listing.material_category, listing_type=listing.material_type,
            listing_length_mm=listing.dimension_length_mm, listing_width_mm=listing.dimension_width_mm,
            listing_quantity=listing.quantity, listing_condition=listing.condition,
            listing_available_until=listing.available_until,
            req_category=req.material_category, req_type=req.material_type,
            req_length_mm=req.dimension_length_mm, req_width_mm=req.dimension_width_mm,
            req_quantity=req.quantity, req_condition=req.condition,
            req_required_by=req.required_by, distance_km=distance_km,
        )
        if breakdown.overall_score < 0.10:
            continue
        match = models.Match(
            listing_id=listing.id, requirement_id=req.id, score=breakdown.overall_score,
            material_score=breakdown.material_score, dimension_score=breakdown.dimension_score,
            quantity_score=breakdown.quantity_score, condition_score=breakdown.condition_score,
            distance_score=breakdown.distance_score, availability_score=breakdown.availability_score,
            distance_km=breakdown.distance_km,
        )
        db.add(match)
    db.commit()

    # Take the best match (the tile listing) and walk it all the way through
    # to a completed, reuse-confirmed transaction so the dashboard has data.
    best_match = (
        db.query(models.Match)
        .filter(models.Match.requirement_id == req.id)
        .order_by(models.Match.score.desc())
        .first()
    )
    if best_match:
        listing = best_match.listing
        logistics = estimate_logistics(
            listing.latitude, listing.longitude, req.latitude, req.longitude,
            listing.material_category, req.quantity,
        )
        tx = models.Transaction(
            match_id=best_match.id, agreed_quantity=req.quantity,
            agreed_value_inr=logistics.estimated_material_value_inr,
            estimated_transport_cost_inr=logistics.estimated_transport_cost_inr,
            distance_km=logistics.distance_km,
            pickup_date=now + timedelta(days=2), delivery_date=now + timedelta(days=2),
            status=models.TransactionStatus.DELIVERED,
        )
        db.add(tx)
        listing.status = models.ListingStatus.CLOSED
        db.commit()
        db.refresh(tx)

        confirmation = models.ReuseConfirmation(
            transaction_id=tx.id, quantity_confirmed=req.quantity,
            notes="Tiles installed in Block C ground floor lobby.",
        )
        db.add(confirmation)
        tx.status = models.TransactionStatus.REUSE_CONFIRMED
        db.commit()

    print(f"Seeded {len(listings)} listings, {len(requirements)} requirements, "
          f"and 1 completed reuse-confirmed transaction.")
    db.close()


if __name__ == "__main__":
    seed()
