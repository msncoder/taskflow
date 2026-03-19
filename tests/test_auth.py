"""
Test suite for Authentication endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthEndpoints:
    """Test authentication endpoints."""

    async def test_login_success(
        self,
        test_client: AsyncClient,
        test_admin_user,
    ):
        """Test successful login returns tokens."""
        response = await test_client.post(
            "/auth/login",
            json={
                "email": "admin@test.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_password(
        self,
        test_client: AsyncClient,
        test_admin_user,
    ):
        """Test login with invalid password returns 401."""
        response = await test_client.post(
            "/auth/login",
            json={
                "email": "admin@test.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401

    async def test_login_nonexistent_user(
        self,
        test_client: AsyncClient,
    ):
        """Test login with non-existent email returns 401."""
        response = await test_client.post(
            "/auth/login",
            json={
                "email": "nonexistent@test.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401

    async def test_get_current_user(
        self,
        test_client: AsyncClient,
        test_admin_user,
        admin_token: str,
    ):
        """Test get current user endpoint."""
        response = await test_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["role"] == "admin"

    async def test_get_current_user_unauthorized(
        self,
        test_client: AsyncClient,
    ):
        """Test get current user without token returns 401."""
        response = await test_client.get("/auth/me")
        
        assert response.status_code == 401

    async def test_get_current_user_invalid_token(
        self,
        test_client: AsyncClient,
    ):
        """Test get current user with invalid token returns 401."""
        response = await test_client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
