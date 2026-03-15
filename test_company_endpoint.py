"""
Test script to manually test the /api/v1/company/me endpoint.

This script:
1. Creates a test company and admin user directly in the database
2. Generates a valid JWT access token
3. Makes a request to the protected endpoint
"""

import asyncio
import uuid
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.features.company.models import Company
from app.features.user.models import User, UserRole


async def setup_test_data():
    """Create test company and admin user in database."""

    # Create async engine (use same driver as app)
    engine = create_async_engine(settings.database_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as db:
        # Check if test user already exists
        result = await db.execute(select(User).where(User.email == "admin@test.com"))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("[OK] Test user already exists")
            user = existing_user
        else:
            # Create test company
            company = Company(name="Test Company", slug="test-company")
            db.add(company)
            await db.flush()
            print(f"[OK] Created company: {company.name} (ID: {company.id})")

            # Create test admin user
            user = User(
                id=uuid.uuid4(),
                email="admin@test.com",
                full_name="Test Admin",
                hashed_password=hash_password("password123"),
                role=UserRole.ADMIN,
                company_id=company.id,
                is_active=True,
            )
            db.add(user)
            await db.commit()  # Commit the transaction
            await db.refresh(user)
            await db.refresh(company)
            print(f"[OK] Created admin user: {user.email} (ID: {user.id})")

        # Generate JWT token
        token = create_access_token({"sub": str(user.id)})
        print(f"\n[OK] Generated JWT token:\n{token}\n")

        return str(user.id), token


async def test_company_me_endpoint(token: str):
    """Test the /api/v1/company/me endpoint."""
    
    async with httpx.AsyncClient() as client:
        # Test with valid token
        print("Testing GET /api/v1/company/me with valid token...")
        response = await client.get(
            "http://localhost:8000/api/v1/company/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("\n[SUCCESS] Endpoint working correctly.")
        else:
            print(f"\n[FAILED] Expected 200, got {response.status_code}")

        # Test without token
        print("\n\nTesting GET /api/v1/company/me WITHOUT token...")
        response_no_auth = await client.get("http://localhost:8000/api/v1/company/me")
        print(f"Status: {response_no_auth.status_code}")
        print(f"Response: {response_no_auth.json()}")

        if response_no_auth.status_code == 401:
            print("\n[OK] Correctly returns 401 Unauthorized without token.")


async def main():
    print("=" * 60)
    print("TaskFlow SaaS - Test /api/v1/company/me Endpoint")
    print("=" * 60)
    print()
    
    # Setup test data
    user_id, token = await setup_test_data()
    
    print("\n" + "=" * 60)
    print("Testing Endpoint")
    print("=" * 60)
    print()
    
    # Test endpoint
    await test_company_me_endpoint(token)
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print()
    print("Credentials for manual testing:")
    print("  Email: admin@test.com")
    print("  Password: password123")
    print()


if __name__ == "__main__":
    asyncio.run(main())
