from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from app.features.invitation.models import InvitationRole


class InviteRequest(BaseModel):
    """Schema for sending an invitation."""

    email: EmailStr = Field(..., description="Email address of the invitee")
    role: InvitationRole = Field(..., description="Role to assign (manager or employee)")


class AcceptInviteRequest(BaseModel):
    """Schema for accepting an invitation."""

    token: str = Field(..., description="Invitation token")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    password: str = Field(..., min_length=8, max_length=72, description="Password (8-72 chars)")


class InvitationRead(BaseModel):
    """Schema for reading invitation data."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    role: InvitationRole
    is_accepted: bool
    expires_at: datetime
