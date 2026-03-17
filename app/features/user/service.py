from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ForbiddenException
from app.features.user.models import User


async def list_company_users(db: AsyncSession, company_id: UUID) -> list[User]:
    """
    List all users in a company.

    Args:
        db: AsyncSession database session
        company_id: Company UUID

    Returns:
        List of User instances ordered by created_at desc
    """
    result = await db.execute(
        select(User)
        .where(User.company_id == company_id)
        .order_by(User.created_at.desc())
    )
    return list(result.scalars().all())


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User:
    """
    Get user by ID.

    Args:
        db: AsyncSession database session
        user_id: User UUID

    Returns:
        User instance

    Raises:
        NotFoundException: If user not found
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundException("User not found")

    return user


async def get_user_by_id_and_company(
    db: AsyncSession,
    user_id: UUID,
    company_id: UUID,
) -> User:
    """
    Get user by ID and company ID (for authorization).

    Args:
        db: AsyncSession database session
        user_id: User UUID
        company_id: Company UUID

    Returns:
        User instance

    Raises:
        NotFoundException: If user not found or doesn't belong to company
    """
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.company_id == company_id,
        )
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundException("User not found")

    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User:
    """
    Get user by email.

    Args:
        db: AsyncSession database session
        email: User email

    Returns:
        User instance

    Raises:
        NotFoundException: If user not found
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        raise NotFoundException("User not found")

    return user


async def deactivate_user(
    db: AsyncSession,
    user_id: UUID,
    company_id: UUID,
    current_user_id: UUID,
) -> None:
    """
    Deactivate a user (soft delete).

    Args:
        db: AsyncSession database session
        user_id: User UUID to deactivate
        company_id: Company UUID (for authorization)
        current_user_id: ID of user performing the action

    Raises:
        NotFoundException: If user not found
        ForbiddenException: If trying to deactivate admin or self
    """
    # Get the target user
    user = await get_user_by_id_and_company(db, user_id, company_id)

    # Cannot deactivate yourself
    if user.id == current_user_id:
        raise ForbiddenException("You cannot deactivate your own account")

    # Cannot deactivate admin users (only admins can do this, so prevents admin removal)
    if user.is_admin:
        raise ForbiddenException("Cannot deactivate admin users")

    # Deactivate the user
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active=False)
    )
    await db.flush()


async def activate_user(
    db: AsyncSession,
    user_id: UUID,
    company_id: UUID,
) -> None:
    """
    Reactivate a deactivated user.

    Args:
        db: AsyncSession database session
        user_id: User UUID to activate
        company_id: Company UUID (for authorization)

    Raises:
        NotFoundException: If user not found
    """
    user = await get_user_by_id_and_company(db, user_id, company_id)

    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active=True)
    )
    await db.flush()
