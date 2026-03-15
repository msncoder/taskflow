from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class CompanyCreate(BaseModel):
    """Schema for creating a company."""

    name: str = Field(..., min_length=1, max_length=255, description="Company name")


class CompanyRead(BaseModel):
    """Schema for reading company data."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    created_at: datetime
