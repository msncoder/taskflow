from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, CurrentUser
from app.features.auth.schemas import (
    AdminRegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.features.auth.service import (
    register_admin as register_admin_service,
    login as login_service,
    refresh_tokens as refresh_tokens_service,
)
from app.features.user.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, summary="Register Admin")
async def register(
    data: AdminRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Register a new admin user and create a company.

    This endpoint:
    1. Creates a new company with the given name
    2. Creates an admin user associated with the company
    3. Returns JWT access and refresh tokens

    **No authentication required**
    """
    return await register_admin_service(db=db, data=data)


@router.post("/login", response_model=TokenResponse, summary="Login")
async def login_endpoint(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.

    **No authentication required**
    """
    return await login_service(db=db, email=data.email, password=data.password)


@router.post("/refresh", response_model=TokenResponse, summary="Refresh Token")
async def refresh(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    **No authentication required** (uses refresh token)
    """
    return await refresh_tokens_service(db=db, refresh_token=data.refresh_token)


@router.get("/me", response_model=UserRead, summary="Current User")
async def get_me(
    current_user: CurrentUser,
) -> UserRead:
    """
    Get current authenticated user information.

    **Requires authentication** (valid JWT access token)
    """
    return UserRead.model_validate(current_user)
