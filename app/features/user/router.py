from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, CurrentUser, AdminUser, ManagerUser
from app.features.user.schemas import UserRead, UserUpdate
from app.features.user.service import (
    list_company_users,
    get_user_by_id,
    get_user_by_id_and_company,
    deactivate_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=list[UserRead],
    summary="List Company Users",
)
async def list_users(
    current_user: ManagerUser,
    db: AsyncSession = Depends(get_db),
) -> list[UserRead]:
    """
    List all users in the current user's company.

    **Permissions:**
    - Admin: Can view all users
    - Manager: Can view all users
    - Employee: Cannot access

    Returns users ordered by creation date (newest first).

    Args:
        current_user: Authenticated user (Admin or Manager)
        db: Database session

    Returns:
        list[UserRead]: List of users in the company
    """
    users = await list_company_users(
        db=db,
        company_id=current_user.company_id,
    )
    return [UserRead.model_validate(user) for user in users]


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get User Detail",
)
async def get_user(
    user_id: UUID,
    current_user: ManagerUser,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """
    Get details of a specific user in the company.

    **Permissions:**
    - Admin: Can view any user
    - Manager: Can view any user in their company

    Args:
        user_id: UUID of the user to retrieve
        current_user: Authenticated user (Admin or Manager)
        db: Database session

    Returns:
        UserRead: User details

    Raises:
        NotFoundException: If user not found or doesn't belong to company
    """
    user = await get_user_by_id_and_company(
        db=db,
        user_id=user_id,
        company_id=current_user.company_id,
    )
    return UserRead.model_validate(user)


@router.patch(
    "/me",
    response_model=UserRead,
    summary="Update Own Profile",
)
async def update_own_profile(
    data: UserUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """
    Update your own profile information.

    **Permissions:** All authenticated users

    Currently supports:
    - Updating full_name

    Args:
        data: UserUpdate schema with fields to update
        current_user: Authenticated user
        db: Database session

    Returns:
        UserRead: Updated user profile
    """
    from sqlalchemy import update

    # Update user's full_name
    await db.execute(
        update(type(current_user))
        .where(type(current_user).id == current_user.id)
        .values(full_name=data.full_name)
    )
    await db.flush()
    await db.refresh(current_user)

    return UserRead.model_validate(current_user)


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Deactivate User",
)
async def delete_user(
    user_id: UUID,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Deactivate a user (soft delete).

    **Permissions:**
    - Admin: Can deactivate any non-admin user
    - Manager/Employee: Cannot access

    **Restrictions:**
    - Cannot deactivate yourself
    - Cannot deactivate admin users

    Args:
        user_id: UUID of the user to deactivate
        current_user: Authenticated admin user
        db: Database session

    Raises:
        NotFoundException: If user not found
        ForbiddenException: If trying to deactivate self or admin
    """
    await deactivate_user(
        db=db,
        user_id=user_id,
        company_id=current_user.company_id,
        current_user_id=current_user.id,
    )
