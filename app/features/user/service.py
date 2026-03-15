from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.features.user.models import User


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
