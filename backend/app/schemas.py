from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# --- Listings ---

class ListingCreate(BaseModel):
    supplier_name: str
    material_category: str
    material_type: str
    quantity: float
    unit: str
    dimension_length_mm: Optional[float] = None
    dimension_width_mm: Optional[float] = None
    condition: str
    color: Optional[str] = None
    location_city: str
    available_until: datetime


class ListingImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    image_path: str
    ai_predicted_category: Optional[str] = None
    ai_confidence: Optional[float] = None


class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    supplier_name: str
    material_category: str
    material_type: str
    quantity: float
    unit: str
    dimension_length_mm: Optional[float]
    dimension_width_mm: Optional[float]
    condition: str
    color: Optional[str]
    location_city: str
    latitude: Optional[float]
    longitude: Optional[float]
    available_until: datetime
    status: str
    created_at: datetime
    images: List[ListingImageOut] = []


# --- Requirements ---

class RequirementCreate(BaseModel):
    requester_name: str
    material_category: str
    material_type: str
    quantity: float
    unit: str
    dimension_length_mm: Optional[float] = None
    dimension_width_mm: Optional[float] = None
    condition: str
    location_city: str
    required_by: datetime


class RequirementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    requester_name: str
    material_category: str
    material_type: str
    quantity: float
    unit: str
    dimension_length_mm: Optional[float]
    dimension_width_mm: Optional[float]
    condition: str
    location_city: str
    latitude: Optional[float]
    longitude: Optional[float]
    required_by: datetime
    created_at: datetime


# --- Matches ---

class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    listing_id: int
    requirement_id: int
    score: float
    material_score: float
    dimension_score: float
    quantity_score: float
    condition_score: float
    distance_score: float
    availability_score: float
    distance_km: Optional[float]
    listing: ListingOut


# --- Transactions ---

class TransactionCreate(BaseModel):
    match_id: int
    agreed_quantity: float
    pickup_date: Optional[datetime] = None
    delivery_date: Optional[datetime] = None


class TransactionStatusUpdate(BaseModel):
    status: str


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    match_id: int
    agreed_quantity: float
    agreed_value_inr: float
    estimated_transport_cost_inr: float
    distance_km: float
    pickup_date: Optional[datetime]
    delivery_date: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: datetime


# --- Reuse confirmation ---

class ReuseConfirmationCreate(BaseModel):
    transaction_id: int
    quantity_confirmed: float
    notes: Optional[str] = None


class ReuseConfirmationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    transaction_id: int
    quantity_confirmed: float
    photo_path: Optional[str]
    notes: Optional[str]
    confirmed_at: datetime


# --- Dashboard ---

class DashboardStats(BaseModel):
    materials_reused_units: float
    waste_diverted_kg: float
    projects_connected: int
    active_listings: int
    open_requirements: int
