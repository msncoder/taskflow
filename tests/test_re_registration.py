import pytest
from httpx import AsyncClient
from sqlalchemy import select
import time
from app.features.user.models import User, UserRole
from app.features.invitation.models import Invitation
from app.core.security import hash_password

@pytest.mark.asyncio
class TestReRegistration:
    """Test suite for re-registration of deactivated users."""

    async def test_re_register_via_invitation(
        self,
        test_client: AsyncClient,
        test_admin_user,
        admin_token: str,
        db_session,
    ):
        """Test inviting and registering a deactivated user."""
        # 1. Create and deactivate a user
        ts = int(time.time())
        email = f"deactivated_{ts}@test.com"
        user = User(
            email=email,
            full_name="Deactivated User",
            hashed_password=hash_password("password123"),
            role=UserRole.EMPLOYEE,
            company_id=test_admin_user.company_id,
            is_active=False
        )
        db_session.add(user)
        await db_session.commit()

        # 2. Invite the deactivated user as a MANAGER
        response = await test_client.post(
            "/invitations/",
            json={
                "email": email,
                "role": "manager"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # 2.5 Get token from database (since it's not in the response for security)
        result = await db_session.execute(
            select(Invitation).where(Invitation.email == email).order_by(Invitation.created_at.desc())
        )
        invitation = result.scalars().first()
        token = invitation.token

        # 3. Accept the invitation
        response = await test_client.post(
            "/invitations/accept",
            json={
                "token": token,
                "full_name": "Reactivated User",
                "password": "newpassword123"
            }
        )
        assert response.status_code == 200

        # 4. Verify user is reactivated with new details
        await db_session.refresh(user)
        assert user.is_active is True
        assert user.full_name == "Reactivated User"
        assert user.role == UserRole.MANAGER
        assert user.company_id == test_admin_user.company_id

    async def test_re_register_different_company(
        self,
        test_client: AsyncClient,
        test_admin_user,
        admin_token: str,
        db_session,
    ):
        """Test inviting a deactivated user to a different company."""
        # 1. Create a user in Company A and deactivate them
        ts = int(time.time())
        email = f"cross_company_{ts}@test.com"
        company_a = test_admin_user.company
        user = User(
            email=email,
            full_name="Original User",
            hashed_password=hash_password("password123"),
            role=UserRole.EMPLOYEE,
            company_id=company_a.id,
            is_active=False
        )
        db_session.add(user)
        
        # 2. Create Company B and an Admin there
        from app.features.company.models import Company
        company_b = Company(name="Company B", slug="test-company-b")
        db_session.add(company_b)
        await db_session.flush()
        
        admin_b = User(
            email="admin_b@test.com",
            full_name="Admin B",
            hashed_password=hash_password("password123"),
            role=UserRole.ADMIN,
            company_id=company_b.id,
            is_active=True
        )
        db_session.add(admin_b)
        await db_session.commit()
        
        from app.core.security import create_access_token
        admin_b_token = create_access_token({"sub": str(admin_b.id)})

        # 3. Admin B invites the deactivated user
        response = await test_client.post(
            "/invitations/",
            json={
                "email": email,
                "role": "employee"
            },
            headers={"Authorization": f"Bearer {admin_b_token}"}
        )
        assert response.status_code == 201
        
        # 3.5 Get token from database
        result = await db_session.execute(
            select(Invitation).where(Invitation.email == email).order_by(Invitation.created_at.desc())
        )
        invitation = result.scalars().first()
        token = invitation.token

        # 4. Accept invitation
        response = await test_client.post(
            "/invitations/accept",
            json={
                "token": token,
                "full_name": "New Name",
                "password": "newpassword123"
            }
        )
        assert response.status_code == 200

        # 5. Verify user moved to Company B
        await db_session.refresh(user)
        assert user.is_active is True
        assert user.company_id == company_b.id
        assert user.full_name == "New Name"

    async def test_register_admin_deactivated_email(
        self,
        test_client: AsyncClient,
        db_session,
    ):
        """Test registering a new company with a deactivated email."""
        # 1. Create and deactivate a user
        ts = int(time.time())
        email = f"admin_reactivate_{ts}@test.com"
        
        from app.features.company.models import Company
        dummy_company = Company(name=f"Old Company {ts}", slug=f"test-old-company-{ts}")
        db_session.add(dummy_company)
        await db_session.flush()

        user = User(
            email=email,
            full_name="Old Admin",
            hashed_password=hash_password("password123"),
            role=UserRole.ADMIN,
            company_id=dummy_company.id,
            is_active=False
        )
        db_session.add(user)
        await db_session.commit()

        # 2. Register new company with same email
        response = await test_client.post(
            "/auth/register",
            json={
                "email": email,
                "full_name": "New Admin Name",
                "password": "newpassword123",
                "company_name": "Brand New Company"
            }
        )
        assert response.status_code == 200
        
        # 3. Verify user is reactivated and linked to new company
        await db_session.refresh(user)
        assert user.is_active is True
        assert user.full_name == "New Admin Name"
        assert user.role == UserRole.ADMIN
        
        result = await db_session.execute(select(Company).where(Company.name == "Brand New Company"))
        new_company = result.scalar_one()
        assert user.company_id == new_company.id

    async def test_invite_active_user_fails(
        self,
        test_client: AsyncClient,
        test_admin_user,
        admin_token: str,
        test_employee_user,
    ):
        """Test that inviting an active user still fails."""
        response = await test_client.post(
            "/invitations/",
            json={
                "email": test_employee_user.email,
                "role": "employee"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
