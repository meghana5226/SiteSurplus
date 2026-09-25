from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services.geodata import lookup_coordinates

router = APIRouter(prefix="/api/requirements", tags=["requirements"])


@router.post("", response_model=schemas.RequirementOut)
def create_requirement(payload: schemas.RequirementCreate, db: Session = Depends(get_db)):
    lat, lon = lookup_coordinates(payload.location_city)
    requirement = models.Requirement(**payload.model_dump(), latitude=lat, longitude=lon)
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return requirement


@router.get("", response_model=List[schemas.RequirementOut])
def list_requirements(db: Session = Depends(get_db)):
    return db.query(models.Requirement).order_by(models.Requirement.created_at.desc()).all()


@router.get("/{requirement_id}", response_model=schemas.RequirementOut)
def get_requirement(requirement_id: int, db: Session = Depends(get_db)):
    requirement = db.get(models.Requirement, requirement_id)
    if not requirement:
        raise HTTPException(404, "Requirement not found")
    return requirement
