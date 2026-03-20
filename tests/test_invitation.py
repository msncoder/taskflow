"""
Test suite for Invitation endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from datetime import datetime, timezone, timedelta

from app.features.invitation.models import Invitation
from app.features.user.models import User


@pytest.mark.asyncio
class TestInvitationEndpoints:
    """Test invitation endpoints."""

    async def test_admin_invites_manager(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
    ):
        """Test admin can invite manager."""
        response = await test_client.post(
            "/invitations/",
            json={
                "email": "manager@test.com",
                "role": "manager"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "manager@test.com"
        assert data["role"] == "manager"
        assert data["is_accepted"] is False

    async def test_admin_invites_employee(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
    ):
        """Test admin can invite employee."""
        response = await test_client.post(
            "/invitations/",
            json={
                "email": "employee@test.com",
                "role": "employee"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "employee@test.com"
        assert data["role"] == "employee"

    async def test_manager_invites_employee(
        self,
        test_client: AsyncClient,
        test_manager_user,
        test_company,
        manager_token: str,
    ):
        """Test manager can invite employee."""
        response = await test_client.post(
            "/invitations/",
            json={
                "email": "newemployee@test.com",
                "role": "employee"
            },
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "employee"

    async def test_manager_invites_manager_forbidden(
        self,
        test_client: AsyncClient,
        test_manager_user,
        test_company,
        manager_token: str,
    ):
        """Test manager cannot invite manager (403)."""
        response = await test_client.post(
            "/invitations/",
            json={
                "email": "anothermanager@test.com",
                "role": "manager"
            },
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert response.status_code == 403

    async def test_employee_invites_forbidden(
        self,
        test_client: AsyncClient,
        test_employee_user,
        test_company,
        employee_token: str,
    ):
        """Test employee cannot send invitations (403)."""
        response = await test_client.post(
            "/invitations/",
            json={
                "email": "someone@test.com",
                "role": "employee"
            },
            headers={"Authorization": f"Bearer {employee_token}"}
        )

        assert response.status_code == 403

    async def test_list_invitations_admin(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
        db_session,
    ):
        """Test admin can list invitations."""
        # Create an invitation
        invitation = Invitation(
            email="test@test.com",
            role="employee",
            company_id=test_company.id,
            token="test-token-123",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db_session.add(invitation)
        await db_session.commit()

        response = await test_client.get(
            "/invitations/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "total" in data or isinstance(data, list)
        if isinstance(data, list):
            assert len(data) > 0
        else:
            assert data["total"] > 0

    async def test_list_invitations_unauthorized(
        self,
        test_client: AsyncClient,
        test_employee_user,
        employee_token: str,
    ):
        """Test non-admin cannot list invitations (403)."""
        response = await test_client.get(
            "/invitations/",
            headers={"Authorization": f"Bearer {employee_token}"}
        )

        assert response.status_code == 403

    async def test_accept_valid_invitation(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        db_session,
    ):
        """Test accepting a valid invitation creates user and returns tokens."""
        # Create invitation
        invitation = Invitation(
            email="newuser@test.com",
            role="employee",
            company_id=test_company.id,
            token="valid-accept-token",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db_session.add(invitation)
        await db_session.commit()

        # Accept invitation
        response = await test_client.post(
            "/invitations/accept",
            json={
                "token": "valid-accept-token",
                "full_name": "New User",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

        # Verify user was created
        result = await db_session.execute(
            select(User).where(User.email == "newuser@test.com")
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.full_name == "New User"
        assert user.role == "employee"

    async def test_accept_invalid_token(
        self,
        test_client: AsyncClient,
    ):
        """Test accepting with invalid token returns 404."""
        response = await test_client.post(
            "/invitations/accept",
            json={
                "token": "invalid-token-xyz",
                "full_name": "Test User",
                "password": "password123"
            }
        )

        assert response.status_code == 404

    async def test_accept_already_accepted_invite(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        db_session,
    ):
        """Test accepting already accepted invitation returns 400."""
        # Create already accepted invitation
        invitation = Invitation(
            email="accepted@test.com",
            role="employee",
            company_id=test_company.id,
            token="already-accepted-token",
            is_accepted=True,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db_session.add(invitation)
        await db_session.commit()

        response = await test_client.post(
            "/invitations/accept",
            json={
                "token": "already-accepted-token",
                "full_name": "Test User",
                "password": "password123"
            }
        )

        assert response.status_code == 400

    async def test_accept_expired_invite(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        db_session,
    ):
        """Test accepting expired invitation returns 400."""
        # Create expired invitation
        invitation = Invitation(
            email="expired@test.com",
            role="employee",
            company_id=test_company.id,
            token="expired-token",
            expires_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db_session.add(invitation)
        await db_session.commit()

        response = await test_client.post(
            "/invitations/accept",
            json={
                "token": "expired-token",
                "full_name": "Test User",
                "password": "password123"
            }
        )

        assert response.status_code == 400

    async def test_duplicate_invitation(
        self,
        test_client: AsyncClient,
        test_admin_user,
        test_company,
        admin_token: str,
        db_session,
    ):
        """Test creating duplicate invitation returns 409."""
        # Create existing invitation
        invitation = Invitation(
            email="duplicate@test.com",
            role="employee",
            company_id=test_company.id,
            token="existing-token",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db_session.add(invitation)
        await db_session.commit()

        # Try to create duplicate
        response = await test_client.post(
            "/invitations/",
            json={
                "email": "duplicate@test.com",
                "role": "employee"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 409
