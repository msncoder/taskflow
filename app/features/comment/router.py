from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, CurrentUser
from app.features.comment.schemas import CommentCreate, CommentRead, CommentListResponse
from app.features.comment.service import (
    add_comment,
    list_comments,
    delete_comment,
)

router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["Comments"])


@router.post(
    "/",
    response_model=CommentRead,
    status_code=201,
    summary="Add Comment",
)
async def add_comment_endpoint(
    task_id: UUID,
    data: CommentCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> CommentRead:
    """
    Add a comment to a task.

    **Permissions:**
    - Any user with read access to the task can comment

    Args:
        task_id: UUID of the task
        data: CommentCreate schema with body text
        current_user: Authenticated user
        db: Database session

    Returns:
        CommentRead: Created comment with author info
    """
    comment = await add_comment(
        db=db,
        task_id=task_id,
        current_user=current_user,
        body=data.body,
    )
    return CommentRead.model_validate(comment)


@router.get(
    "/",
    response_model=CommentListResponse,
    summary="List Comments",
)
async def list_comments_endpoint(
    task_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> CommentListResponse:
    """
    List all comments for a task.

    **Permissions:**
    - Any user with read access to the task can view comments

    Args:
        task_id: UUID of the task
        current_user: Authenticated user
        db: Database session

    Returns:
        CommentListResponse: List of comments ordered by creation date (oldest first)
    """
    comments = await list_comments(
        db=db,
        task_id=task_id,
        current_user=current_user,
    )
    return CommentListResponse(
        comments=[CommentRead.model_validate(comment) for comment in comments],
        total=len(comments),
    )


@router.delete(
    "/{comment_id}",
    status_code=204,
    summary="Delete Comment",
)
async def delete_comment_endpoint(
    task_id: UUID,
    comment_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a comment.

    **Permissions:**
    - Author can delete their own comment
    - Admin can delete any comment

    Args:
        task_id: UUID of the task (for path consistency)
        comment_id: UUID of the comment to delete
        current_user: Authenticated user
        db: Database session
    """
    await delete_comment(
        db=db,
        comment_id=comment_id,
        current_user=current_user,
    )
