from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services.logistics import estimate_logistics

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

# Explicit allowed forward transitions -- enforced server-side so the
# lifecycle can't be skipped or reversed from the API.
ALLOWED_TRANSITIONS = {
    models.TransactionStatus.MATCHED: [models.TransactionStatus.ACCEPTED],
    models.TransactionStatus.ACCEPTED: [models.TransactionStatus.PICKUP_SCHEDULED],
    models.TransactionStatus.PICKUP_SCHEDULED: [models.TransactionStatus.PICKED_UP],
    models.TransactionStatus.PICKED_UP: [models.TransactionStatus.DELIVERED],
    models.TransactionStatus.DELIVERED: [models.TransactionStatus.REUSE_CONFIRMED],
    models.TransactionStatus.REUSE_CONFIRMED: [],
}


@router.post("", response_model=schemas.TransactionOut)
def create_transaction(payload: schemas.TransactionCreate, db: Session = Depends(get_db)):
    match = db.get(models.Match, payload.match_id)
    if not match:
        raise HTTPException(404, "Match not found")
    if match.transaction:
        raise HTTPException(400, "A transaction already exists for this match")

    listing = match.listing
    requirement = match.requirement

    logistics = estimate_logistics(
        listing.latitude, listing.longitude,
        requirement.latitude, requirement.longitude,
        listing.material_category, payload.agreed_quantity,
    )

    transaction = models.Transaction(
        match_id=match.id,
        agreed_quantity=payload.agreed_quantity,
        agreed_value_inr=logistics.estimated_material_value_inr,
        estimated_transport_cost_inr=logistics.estimated_transport_cost_inr,
        distance_km=logistics.distance_km,
        pickup_date=payload.pickup_date,
        delivery_date=payload.delivery_date,
        status=models.TransactionStatus.MATCHED,
    )
    db.add(transaction)

    # Reserve the listing so it stops appearing in future matching runs
    listing.status = models.ListingStatus.RESERVED

    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("/{transaction_id}", response_model=schemas.TransactionOut)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.get(models.Transaction, transaction_id)
    if not tx:
        raise HTTPException(404, "Transaction not found")
    return tx


@router.patch("/{transaction_id}/status", response_model=schemas.TransactionOut)
def update_status(transaction_id: int, payload: schemas.TransactionStatusUpdate, db: Session = Depends(get_db)):
    tx = db.get(models.Transaction, transaction_id)
    if not tx:
        raise HTTPException(404, "Transaction not found")

    try:
        new_status = models.TransactionStatus(payload.status)
    except ValueError:
        raise HTTPException(400, f"Invalid status: {payload.status}")

    allowed = ALLOWED_TRANSITIONS.get(tx.status, [])
    if new_status not in allowed:
        raise HTTPException(
            400,
            f"Cannot move from {tx.status.value} to {new_status.value}. "
            f"Allowed next step(s): {[s.value for s in allowed] or 'none (terminal state)'}"
        )

    tx.status = new_status
    if new_status == models.TransactionStatus.DELIVERED:
        tx.match.listing.status = models.ListingStatus.CLOSED

    db.commit()
    db.refresh(tx)
    return tx
