from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ForbiddenException
from app.features.comment.models import Comment
from app.features.task.models import Task
from app.features.user.models import User, UserRole


async def _check_task_access(
    db: AsyncSession,
    task_id: UUID,
    current_user: User,
) -> Task:
    """
    Check if user has access to a task.

    Business Rules:
    - Admin: Can access any task in company
    - Manager: Can access tasks they created or are assigned to
    - Employee: Can only access tasks assigned to them

    Args:
        db: AsyncSession database session
        task_id: Task UUID
        current_user: Authenticated user

    Returns:
        Task instance

    Raises:
        NotFoundException: If task not found or user lacks access
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if task is None:
        raise NotFoundException("Task not found")

    # Check access based on role
    if current_user.role == UserRole.ADMIN:
        # Admin can access any task in company
        if task.company_id != current_user.company_id:
            raise NotFoundException("Task not found")
    elif current_user.role == UserRole.MANAGER:
        # Manager can access tasks they created or are assigned to
        if task.created_by_id != current_user.id and task.assigned_to_id != current_user.id:
            raise NotFoundException("Task not found")
    else:
        # Employee can only access tasks assigned to them
        if task.assigned_to_id != current_user.id:
            raise NotFoundException("Task not found")

    return task


async def add_comment(
    db: AsyncSession,
    task_id: UUID,
    current_user: User,
    body: str,
) -> Comment:
    """
    Add a comment to a task.

    Business Rules:
    - User must have read access to the task
    - Any user with task access can comment

    Args:
        db: AsyncSession database session
        task_id: Task UUID
        current_user: Authenticated user (comment author)
        body: Comment body text

    Returns:
        Created Comment instance

    Raises:
        NotFoundException: If task not found or user lacks access
    """
    # Verify user has access to the task
    task = await _check_task_access(db, task_id, current_user)

    # Create comment
    comment = Comment(
        task_id=task_id,
        author_id=current_user.id,
        body=body,
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)

    return comment


async def list_comments(
    db: AsyncSession,
    task_id: UUID,
    current_user: User,
) -> list[Comment]:
    """
    List all comments for a task.

    Business Rules:
    - User must have read access to the task to view comments

    Args:
        db: AsyncSession database session
        task_id: Task UUID
        current_user: Authenticated user

    Returns:
        List of Comment instances ordered by created_at asc

    Raises:
        NotFoundException: If task not found or user lacks access
    """
    # Verify user has access to the task
    await _check_task_access(db, task_id, current_user)

    # Get comments
    result = await db.execute(
        select(Comment)
        .where(Comment.task_id == task_id)
        .order_by(Comment.created_at.asc())
    )

    return list(result.scalars().all())


async def delete_comment(
    db: AsyncSession,
    comment_id: UUID,
    current_user: User,
) -> None:
    """
    Delete a comment.

    Business Rules:
    - Author can delete their own comment
    - Admin can delete any comment in their company

    Args:
        db: AsyncSession database session
        comment_id: Comment UUID
        current_user: Authenticated user

    Raises:
        NotFoundException: If comment not found
        ForbiddenException: If user cannot delete this comment
    """
    # Get comment with author info
    result = await db.execute(
        select(Comment).where(Comment.id == comment_id)
    )
    comment = result.scalar_one_or_none()

    if comment is None:
        raise NotFoundException("Comment not found")

    # Check if user can delete this comment
    can_delete = (
        comment.author_id == current_user.id or  # Author can delete own comment
        current_user.role == UserRole.ADMIN  # Admin can delete any comment
    )

    if not can_delete:
        raise ForbiddenException("You can only delete your own comments")

    # Delete comment
    await db.execute(
        delete(Comment).where(Comment.id == comment_id)
    )
    await db.flush()
