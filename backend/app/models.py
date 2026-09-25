"""
ORM models covering the full flow described in the spec:
Listing -> Requirement -> Match -> Transaction -> ReuseConfirmation
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import relationship
from app.database import Base


class ListingStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    CLOSED = "CLOSED"


class TransactionStatus(str, enum.Enum):
    MATCHED = "MATCHED"
    ACCEPTED = "ACCEPTED"
    PICKUP_SCHEDULED = "PICKUP_SCHEDULED"
    PICKED_UP = "PICKED_UP"
    DELIVERED = "DELIVERED"
    REUSE_CONFIRMED = "REUSE_CONFIRMED"


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String, nullable=False)
    material_category = Column(String, nullable=False)   # e.g. Flooring
    material_type = Column(String, nullable=False)        # e.g. Ceramic Tile
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)                 # e.g. Pieces, kg, m2
    dimension_length_mm = Column(Float, nullable=True)
    dimension_width_mm = Column(Float, nullable=True)
    condition = Column(String, nullable=False)             # Unused / Good / Fair
    color = Column(String, nullable=True)
    location_city = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    available_until = Column(DateTime, nullable=False)
    status = Column(Enum(ListingStatus), default=ListingStatus.AVAILABLE)
    created_at = Column(DateTime, default=datetime.utcnow)

    images = relationship("ListingImage", back_populates="listing", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="listing")


class ListingImage(Base):
    __tablename__ = "listing_images"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    image_path = Column(String, nullable=False)
    ai_predicted_category = Column(String, nullable=True)
    ai_confidence = Column(Float, nullable=True)

    listing = relationship("Listing", back_populates="images")


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    requester_name = Column(String, nullable=False)
    material_category = Column(String, nullable=False)
    material_type = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    dimension_length_mm = Column(Float, nullable=True)
    dimension_width_mm = Column(Float, nullable=True)
    condition = Column(String, nullable=False)
    location_city = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    required_by = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    matches = relationship("Match", back_populates="requirement")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)

    score = Column(Float, nullable=False)
    material_score = Column(Float, nullable=False)
    dimension_score = Column(Float, nullable=False)
    quantity_score = Column(Float, nullable=False)
    condition_score = Column(Float, nullable=False)
    distance_score = Column(Float, nullable=False)
    availability_score = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("Listing", back_populates="matches")
    requirement = relationship("Requirement", back_populates="matches")
    transaction = relationship("Transaction", back_populates="match", uselist=False)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, unique=True)

    agreed_quantity = Column(Float, nullable=False)
    agreed_value_inr = Column(Float, nullable=False)
    estimated_transport_cost_inr = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=False)

    pickup_date = Column(DateTime, nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.MATCHED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    match = relationship("Match", back_populates="transaction")
    reuse_confirmation = relationship("ReuseConfirmation", back_populates="transaction", uselist=False)


class ReuseConfirmation(Base):
    __tablename__ = "reuse_confirmations"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, unique=True)
    quantity_confirmed = Column(Float, nullable=False)
    photo_path = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    confirmed_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="reuse_confirmation")
