from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, CurrentUser, AdminUser, ManagerUser
from app.features.task.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskRead,
    TaskListResponse,
)
from app.features.task.service import (
    create_task,
    list_tasks,
    get_task,
    update_task,
    toggle_complete,
    delete_task,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "/",
    response_model=TaskRead,
    status_code=201,
    summary="Create Task",
)
async def create_task_endpoint(
    data: TaskCreate,
    current_user: ManagerUser,
    db: AsyncSession = Depends(get_db),
) -> TaskRead:
    """
    Create a new task.

    **Permissions:**
    - Admin: Can create and assign to anyone in company
    - Manager: Can create and assign to employees only
    - Employee: Cannot create tasks

    Args:
        data: TaskCreate schema with title, description, assigned_to_id, due_date
        current_user: Authenticated user (Admin or Manager)
        db: Database session

    Returns:
        TaskRead: Created task with full details
    """
    task = await create_task(
        db=db,
        creator=current_user,
        title=data.title,
        description=data.description,
        assigned_to_id=data.assigned_to_id,
        due_date=data.due_date,
    )
    return TaskRead.model_validate(task)


@router.get(
    "/",
    response_model=TaskListResponse,
    summary="List Tasks",
)
async def list_tasks_endpoint(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    """
    List tasks based on user role.

    **Permissions:**
    - Admin: All tasks in company
    - Manager: Tasks they created OR assigned to their employees
    - Employee: Only tasks assigned to them

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        TaskListResponse: List of tasks with total count
    """
    tasks = await list_tasks(
        db=db,
        current_user=current_user,
    )
    return TaskListResponse(
        tasks=[TaskRead.model_validate(task) for task in tasks],
        total=len(tasks),
    )


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get Task Detail",
)
async def get_task_endpoint(
    task_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TaskRead:
    """
    Get details of a specific task.

    **Permissions:**
    - Admin: Can view any task in company
    - Manager: Can view tasks they created or are assigned to
    - Employee: Can only view tasks assigned to them

    Args:
        task_id: UUID of the task
        current_user: Authenticated user
        db: Database session

    Returns:
        TaskRead: Task details with created_by and assigned_to info
    """
    task = await get_task(
        db=db,
        task_id=task_id,
        current_user=current_user,
    )
    return TaskRead.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update Task",
)
async def update_task_endpoint(
    task_id: UUID,
    data: TaskUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TaskRead:
    """
    Update task metadata.

    **Permissions:**
    - Creator or Admin can update
    - Manager can update tasks they created
    - Employee can update tasks they created

    Args:
        task_id: UUID of the task
        data: TaskUpdate schema with fields to update
        current_user: Authenticated user
        db: Database session

    Returns:
        TaskRead: Updated task details
    """
    task = await update_task(
        db=db,
        task_id=task_id,
        current_user=current_user,
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        assigned_to_id=data.assigned_to_id,
    )
    return TaskRead.model_validate(task)


@router.patch(
    "/{task_id}/toggle-complete",
    response_model=TaskRead,
    summary="Toggle Task Complete",
)
async def toggle_complete_endpoint(
    task_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TaskRead:
    """
    Toggle task completion status.

    **Permissions:**
    - Only the assigned employee can toggle their task
    - Admin/Manager cannot toggle (they can use update endpoint)

    Args:
        task_id: UUID of the task
        current_user: Authenticated user
        db: Database session

    Returns:
        TaskRead: Updated task with toggled status
    """
    task = await toggle_complete(
        db=db,
        task_id=task_id,
        current_user=current_user,
    )
    return TaskRead.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=204,
    summary="Delete Task",
)
async def delete_task_endpoint(
    task_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a task.

    **Permissions:**
    - Admin only can delete tasks

    Args:
        task_id: UUID of the task
        current_user: Authenticated admin user
        db: Database session
    """
    await delete_task(
        db=db,
        task_id=task_id,
        current_user=current_user,
    )
