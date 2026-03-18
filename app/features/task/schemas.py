from datetime import datetime, date
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.features.user.schemas import UserRead


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    assigned_to_id: Optional[UUID] = Field(None, description="User ID to assign task to")
    due_date: Optional[date] = Field(None, description="Task due date")


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    due_date: Optional[date] = Field(None, description="Task due date")
    assigned_to_id: Optional[UUID] = Field(None, description="User ID to assign task to")


class TaskRead(BaseModel):
    """Schema for reading task data."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: Optional[str]
    is_completed: bool
    company_id: UUID
    created_by_id: UUID
    assigned_to_id: Optional[UUID]
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UserRead] = None
    assigned_to: Optional[UserRead] = None


class TaskToggleComplete(BaseModel):
    """Schema for toggling task completion status (no body needed)."""

    pass


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""

    tasks: list[TaskRead]
    total: int
