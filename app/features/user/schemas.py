from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.features.user.models import UserRole


class UserRead(BaseModel):
    """Schema for reading user data."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    role: UserRole
    company_id: UUID
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    full_name: str | None = Field(None, min_length=1, max_length=255, description="Full name")
