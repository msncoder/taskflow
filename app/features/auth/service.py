from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from app.core.exceptions import ConflictException, UnauthorizedException, NotFoundException
from app.features.user.models import User, UserRole
from app.features.company.service import create_company
from app.features.auth.schemas import AdminRegisterRequest


async def register_admin(db: AsyncSession, data: AdminRegisterRequest) -> dict:
    """
    Register a new admin user and create a company.
    
    Args:
        db: AsyncSession database session
        data: AdminRegisterRequest with email, full_name, password, company_name
        
    Returns:
        dict with access_token, refresh_token, token_type
        
    Raises:
        ConflictException: If email already exists
    """
    # Check if an active user with this email already exists
    active_user_result = await db.execute(
        select(User).where(User.email == data.email, User.is_active == True)
    )
    active_user = active_user_result.scalar_one_or_none()
    
    if active_user:
        raise ConflictException("Email already registered and active")
    
    # Check if an inactive user with this email exists to reactivate
    inactive_user_result = await db.execute(
        select(User)
        .where(User.email == data.email, User.is_active == False)
        .order_by(User.created_at.desc())
    )
    existing_user = inactive_user_result.scalars().first()
    
    if existing_user:
        
        # Create company
        company = await create_company(db, data.company_name)
        
        # Reactivate user and update details
        hashed_pw = hash_password(data.password)
        existing_user.is_active = True
        existing_user.full_name = data.full_name
        existing_user.hashed_password = hashed_pw
        existing_user.role = UserRole.ADMIN
        existing_user.company_id = company.id
        
        user = existing_user
    else:
        # Create company
        company = await create_company(db, data.company_name)
        
        # Hash password
        hashed_pw = hash_password(data.password)
        
        # Create admin user
        user = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hashed_pw,
            role=UserRole.ADMIN,
            company_id=company.id,
            is_active=True,
        )
        db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def login(db: AsyncSession, email: str, password: str) -> dict:
    """
    Authenticate user and return tokens.
    
    Args:
        db: AsyncSession database session
        email: User email
        password: User password
        
    Returns:
        dict with access_token, refresh_token, token_type
        
    Raises:
        UnauthorizedException: If credentials are invalid
    """
    # Fetch user by email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise UnauthorizedException("Invalid email or password")
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        raise UnauthorizedException("Invalid email or password")
    
    # Check if user is active
    if not user.is_active:
        raise UnauthorizedException("Account is deactivated")
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> dict:
    """
    Refresh access token using refresh token.
    
    Args:
        db: AsyncSession database session
        refresh_token: JWT refresh token
        
    Returns:
        dict with new access_token, refresh_token, token_type
        
    Raises:
        UnauthorizedException: If token is invalid or user not found
    """
    try:
        # Verify refresh token
        payload = verify_token(refresh_token, token_type="refresh")
    except Exception:
        raise UnauthorizedException("Invalid or expired refresh token")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Invalid token payload")
    
    # Fetch user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise UnauthorizedException("User not found")
    
    # Check if user is active
    if not user.is_active:
        raise UnauthorizedException("Account is deactivated")
    
    # Generate new tokens
    access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


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
