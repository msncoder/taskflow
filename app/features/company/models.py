import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.features.user.models import User
    from app.features.invitation.models import Invitation


class Company(Base):
    """Company (tenant) model for multi-tenant SaaS."""

    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    users: Mapped[list["User"]] = relationship(  # noqa: F821
        back_populates="company",
        lazy="selectin",
    )
    invitations: Mapped[list["Invitation"]] = relationship(  # noqa: F821
        back_populates="company",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Company {self.name}>"
