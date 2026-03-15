import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum

from sqlalchemy import String, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InvitationRole(str, Enum):
    """Invitation role enumeration."""

    MANAGER = "manager"
    EMPLOYEE = "employee"


class Invitation(Base):
    """Invitation model for user invites."""

    __tablename__ = "invitations"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    role: Mapped[InvitationRole] = mapped_column(
        SQLEnum(InvitationRole.MANAGER, InvitationRole.EMPLOYEE, name="invitationrole"),
        nullable=False,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    is_accepted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    company: Mapped["Company"] = relationship(back_populates="invitations")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Invitation {self.email} ({self.role})>"

    @property
    def is_expired(self) -> bool:
        """Check if invitation has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if invitation is still valid."""
        return not self.is_accepted and not self.is_expired
