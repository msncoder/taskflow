from datetime import datetime, timezone
from uuid import UUID
from typing import Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ForbiddenException
from app.features.task.models import Task
from app.features.user.models import User, UserRole


async def create_task(
    db: AsyncSession,
    creator: User,
    title: str,
    description: Optional[str] = None,
    assigned_to_id: Optional[UUID] = None,
    due_date: Optional[datetime] = None,
) -> Task:
    """
    Create a new task.

    Business Rules:
    - Admin: Can assign to any user in company
    - Manager: Can assign to employees only (not other managers/admins)
    - Employee: Cannot create tasks

    Args:
        db: AsyncSession database session
        creator: User creating the task
        title: Task title
        description: Task description (optional)
        assigned_to_id: User ID to assign task to (optional)
        due_date: Task due date (optional)

    Returns:
        Created Task instance

    Raises:
        ForbiddenException: If user cannot create tasks or invalid assignment
        NotFoundException: If assigned user not found
    """
    # Employees cannot create tasks
    if creator.role == UserRole.EMPLOYEE:
        raise ForbiddenException("Employees cannot create tasks")

    # Validate assigned_to_id if provided
    if assigned_to_id:
        result = await db.execute(
            select(User).where(
                User.id == assigned_to_id,
                User.company_id == creator.company_id,
            )
        )
        assigned_user = result.scalar_one_or_none()

        if assigned_user is None:
            raise NotFoundException("Assigned user not found")

        # Managers can only assign to employees
        if creator.role == UserRole.MANAGER and assigned_user.role != UserRole.EMPLOYEE:
            raise ForbiddenException("Managers can only assign tasks to employees")

    # Create task
    task = Task(
        title=title,
        description=description,
        company_id=creator.company_id,
        created_by_id=creator.id,
        assigned_to_id=assigned_to_id,
        due_date=due_date,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)

    return task


async def list_tasks(
    db: AsyncSession,
    current_user: User,
) -> list[Task]:
    """
    List tasks based on user role.

    Business Rules:
    - Admin: All tasks in company
    - Manager: Tasks they created OR assigned to their employees
    - Employee: Only tasks assigned to them

    Args:
        db: AsyncSession database session
        current_user: Authenticated user

    Returns:
        List of Task instances
    """
    if current_user.role == UserRole.ADMIN:
        # Admin sees all tasks in company
        result = await db.execute(
            select(Task)
            .where(Task.company_id == current_user.company_id)
            .order_by(Task.created_at.desc())
        )
    elif current_user.role == UserRole.MANAGER:
        # Manager sees tasks they created OR assigned to their employees
        result = await db.execute(
            select(Task)
            .where(
                Task.company_id == current_user.company_id,
                (Task.created_by_id == current_user.id) |
                (Task.assigned_to_id == current_user.id)
            )
            .order_by(Task.created_at.desc())
        )
    else:
        # Employee sees only tasks assigned to them
        result = await db.execute(
            select(Task)
            .where(
                Task.company_id == current_user.company_id,
                Task.assigned_to_id == current_user.id,
            )
            .order_by(Task.created_at.desc())
        )

    return list(result.scalars().all())


async def get_task(
    db: AsyncSession,
    task_id: UUID,
    current_user: User,
) -> Task:
    """
    Get a task by ID with access check.

    Business Rules:
    - Admin: Can view any task in company
    - Manager: Can view tasks they created or are assigned to
    - Employee: Can only view tasks assigned to them

    Args:
        db: AsyncSession database session
        task_id: Task UUID
        current_user: Authenticated user

    Returns:
        Task instance

    Raises:
        NotFoundException: If task not found or user lacks access
    """
    task = await _get_task_by_id(db, task_id)

    # Check access based on role
    if current_user.role == UserRole.ADMIN:
        # Admin can view any task in company
        if task.company_id != current_user.company_id:
            raise NotFoundException("Task not found")
    elif current_user.role == UserRole.MANAGER:
        # Manager can view tasks they created or are assigned to
        if task.created_by_id != current_user.id and task.assigned_to_id != current_user.id:
            raise NotFoundException("Task not found")
    else:
        # Employee can only view tasks assigned to them
        if task.assigned_to_id != current_user.id:
            raise NotFoundException("Task not found")

    return task


async def update_task(
    db: AsyncSession,
    task_id: UUID,
    current_user: User,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None,
    assigned_to_id: Optional[UUID] = None,
) -> Task:
    """
    Update a task.

    Business Rules:
    - Creator or Admin can update
    - Manager can update tasks they created
    - Employee cannot update tasks (unless they created them)

    Args:
        db: AsyncSession database session
        task_id: Task UUID
        current_user: Authenticated user
        title: New title (optional)
        description: New description (optional)
        due_date: New due date (optional)
        assigned_to_id: New assigned user ID (optional)

    Returns:
        Updated Task instance

    Raises:
        ForbiddenException: If user cannot update this task
        NotFoundException: If task not found
    """
    task = await _get_task_by_id(db, task_id)

    # Check if user can update this task
    can_update = (
        current_user.role == UserRole.ADMIN or
        task.created_by_id == current_user.id
    )

    if not can_update:
        raise ForbiddenException("You can only update tasks you created")

    # Validate assigned_to_id if provided
    if assigned_to_id:
        result = await db.execute(
            select(User).where(
                User.id == assigned_to_id,
                User.company_id == current_user.company_id,
            )
        )
        assigned_user = result.scalar_one_or_none()

        if assigned_user is None:
            raise NotFoundException("Assigned user not found")

        # Managers can only assign to employees
        if current_user.role == UserRole.MANAGER and assigned_user.role != UserRole.EMPLOYEE:
            raise ForbiddenException("Managers can only assign tasks to employees")

    # Update fields
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if due_date is not None:
        update_data["due_date"] = due_date
    if assigned_to_id is not None:
        update_data["assigned_to_id"] = assigned_to_id
    update_data["updated_at"] = datetime.now(timezone.utc)

    await db.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(**update_data)
    )
    await db.flush()

    # Refresh and return
    await db.refresh(task)
    return task


async def toggle_complete(
    db: AsyncSession,
    task_id: UUID,
    current_user: User,
) -> Task:
    """
    Toggle task completion status.

    Business Rules:
    - Only the assigned employee can toggle their task
    - Admin/Manager cannot toggle (they can update via update_task)

    Args:
        db: AsyncSession database session
        task_id: Task UUID
        current_user: Authenticated user

    Returns:
        Updated Task instance

    Raises:
        ForbiddenException: If user is not assigned to this task
        NotFoundException: If task not found
    """
    task = await _get_task_by_id(db, task_id)

    # Only assigned user can toggle
    if task.assigned_to_id != current_user.id:
        raise ForbiddenException("Only the assigned user can toggle task completion")

    # Toggle status
    await db.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(
            is_completed=not task.is_completed,
            updated_at=datetime.now(timezone.utc),
        )
    )
    await db.flush()

    # Refresh and return
    await db.refresh(task)
    return task


async def delete_task(
    db: AsyncSession,
    task_id: UUID,
    current_user: User,
) -> None:
    """
    Delete a task.

    Business Rules:
    - Admin only can delete tasks

    Args:
        db: AsyncSession database session
        task_id: Task UUID
        current_user: Authenticated user

    Raises:
        ForbiddenException: If user is not admin
        NotFoundException: If task not found
    """
    # Only admins can delete
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Only admins can delete tasks")

    task = await _get_task_by_id(db, task_id)

    # Verify task belongs to same company
    if task.company_id != current_user.company_id:
        raise NotFoundException("Task not found")

    # Delete task
    await db.execute(
        delete(Task).where(Task.id == task_id)
    )
    await db.flush()


async def _get_task_by_id(db: AsyncSession, task_id: UUID) -> Task:
    """
    Internal helper to get task by ID.

    Args:
        db: AsyncSession database session
        task_id: Task UUID

    Returns:
        Task instance

    Raises:
        NotFoundException: If task not found
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if task is None:
        raise NotFoundException("Task not found")

    return task
