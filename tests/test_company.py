"""
Test suite for Company endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCompanyEndpoints:
    """Test company endpoints."""

    async def test_get_my_company(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
    ):
        """Test get current user's company."""
        response = await test_client.get(
            "/company/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"].startswith("Test Company")
        assert data["slug"].startswith("test-company")
        assert "id" in data
        assert "created_at" in data

    async def test_get_my_company_unauthorized(
        self,
        test_client: AsyncClient,
    ):
        """Test get company without auth returns 401."""
        response = await test_client.get("/company/me")
        
        assert response.status_code == 401
