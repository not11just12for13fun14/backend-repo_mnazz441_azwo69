"""
Database Schemas for Campus360

Each Pydantic model corresponds to a MongoDB collection. The collection
name is the lowercase of the class name (e.g., User -> "user").

These schemas are used for request validation in the API and for tooling that
introspects your data model via GET /schema.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, EmailStr, HttpUrl


class User(BaseModel):
    """
    Users across Campus360
    Roles: student, driver, vendor, admin
    Collection name: "user"
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    role: str = Field("student", description="Role of the user: student | driver | vendor | admin")
    avatar_url: Optional[HttpUrl] = Field(None, description="Profile image URL")
    phone: Optional[str] = Field(None, description="Contact number")
    is_active: bool = Field(True, description="Whether user is active")


class Address(BaseModel):
    """
    Saved addresses for quick access during bookings/orders
    Collection name: "address"
    """
    user_id: str = Field(..., description="Owner user id")
    label: str = Field(..., description="Friendly label e.g., Home, Library")
    line1: str
    line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = Field(None, description="Geo latitude")
    longitude: Optional[float] = Field(None, description="Geo longitude")


class Activity(BaseModel):
    """
    Recent activity feed items aggregated across services
    Collection name: "activity"
    """
    user_id: Optional[str] = Field(None, description="User related to the activity")
    service: str = Field(..., description="cab360 | medi360 | print360 | system")
    action: str = Field(..., description="Short verb, e.g., booked_ride, placed_order, uploaded_file")
    summary: str = Field(..., description="Human readable summary")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extra data for the activity")
    status: Optional[str] = Field(None, description="optional status e.g., success, failed")


# Optional sample catalog entry to demonstrate DB usage
class CatalogItem(BaseModel):
    """
    Generic catalog items (e.g., medicines or print bindings) for demos
    Collection name: "catalogitem"
    """
    service: str = Field(..., description="cab360 | medi360 | print360")
    name: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    tags: List[str] = Field(default_factory=list)
