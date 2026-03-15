from pydantic import BaseModel, Field, EmailStr


class AdminRegisterRequest(BaseModel):
    """Schema for admin registration."""

    email: EmailStr = Field(..., description="Admin email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    password: str = Field(..., min_length=8, max_length=72, description="Password (8-72 chars)")
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")


class LoginRequest(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class RefreshTokenRequest(BaseModel):
    """Schema for refreshing access token."""

    refresh_token: str = Field(..., description="JWT refresh token")
