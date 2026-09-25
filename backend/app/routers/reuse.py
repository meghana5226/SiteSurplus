import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/reuse", tags=["reuse"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("", response_model=schemas.ReuseConfirmationOut)
async def confirm_reuse(
    transaction_id: int = Form(...),
    quantity_confirmed: float = Form(...),
    notes: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    tx = db.get(models.Transaction, transaction_id)
    if not tx:
        raise HTTPException(404, "Transaction not found")
    if tx.status != models.TransactionStatus.DELIVERED:
        raise HTTPException(400, "Material must be DELIVERED before reuse can be confirmed")
    if tx.reuse_confirmation:
        raise HTTPException(400, "Reuse already confirmed for this transaction")

    photo_path = None
    if photo is not None:
        image_bytes = await photo.read()
        ext = os.path.splitext(photo.filename or "reuse.jpg")[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        photo_path = f"/static/uploads/{filename}"

    confirmation = models.ReuseConfirmation(
        transaction_id=transaction_id,
        quantity_confirmed=quantity_confirmed,
        photo_path=photo_path,
        notes=notes,
    )
    db.add(confirmation)
    tx.status = models.TransactionStatus.REUSE_CONFIRMED
    db.commit()
    db.refresh(confirmation)
    return confirmation
