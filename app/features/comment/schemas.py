from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.features.user.schemas import UserRead


class CommentCreate(BaseModel):
    """Schema for creating a comment."""

    body: str = Field(..., min_length=1, max_length=5000, description="Comment body text")


class CommentRead(BaseModel):
    """Schema for reading comment data."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    author_id: UUID
    body: str
    created_at: datetime
    author: UserRead


class CommentListResponse(BaseModel):
    """Schema for comment list response."""

    comments: list[CommentRead]
    total: int
