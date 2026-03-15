from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import async_session_maker
from app.core.security import verify_token
from app.features.user.models import User
from app.core.exceptions import UnauthorizedException, ForbiddenException


# HTTP Bearer token security
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncSession:
    """Dependency to get async database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Raises:
        UnauthorizedException: If token is missing, invalid, or expired.
    """
    if credentials is None:
        raise UnauthorizedException("Missing authentication token")
    
    token = credentials.credentials
    
    try:
        payload = verify_token(token, token_type="access")
    except Exception:
        raise UnauthorizedException("Invalid or expired token")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Invalid token payload")
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise UnauthorizedException("Invalid user ID in token")
    
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise UnauthorizedException("User not found")
    
    if not user.is_active:
        raise UnauthorizedException("User account is deactivated")
    
    return user


def require_role(*roles: str):
    """
    Dependency factory to require specific user roles.
    
    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            current_user: Annotated[User, Depends(require_role("admin"))]
        ):
            ...
    
    Args:
        *roles: One or more role names that the user must have.
    
    Returns:
        Dependency function that checks user role.
    """
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in roles:
            raise ForbiddenException(
                f"User role '{current_user.role}' does not have access. "
                f"Required: {', '.join(roles)}"
            )
        return current_user
    
    return role_checker


# Type aliases for common dependency injections
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_role("admin"))]
ManagerUser = Annotated[User, Depends(require_role("manager", "admin"))]
