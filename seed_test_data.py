"""
Seed test data for API testing
"""
import asyncio

# Import all models FIRST to avoid SQLAlchemy relationship resolution issues
from app.features.company import models as company_models  # noqa: F401
from app.features.user import models as user_models  # noqa: F401
from app.features.invitation import models as invitation_models  # noqa: F401

from app.core.security import hash_password
from app.db.session import async_session_maker
from app.features.company.models import Company
from app.features.user.models import User, UserRole
from sqlalchemy import select, delete


async def seed():
    async with async_session_maker() as db:
        # Delete existing test user to recreate with new password hash
        await db.execute(delete(User).where(User.email == "test@example.com"))
        await db.commit()

        # Check if company exists
        result = await db.execute(select(Company).where(Company.slug == "test-company"))
        company = result.scalar_one_or_none()

        if not company:
            company = Company(name="Test Company", slug="test-company")
            db.add(company)
            await db.flush()
            print("[OK] Created test company")

        # Create test user
        admin = User(
            email="test@example.com",
            full_name="Test Admin",
            hashed_password=hash_password("password123"),
            role=UserRole.ADMIN,
            company_id=company.id,
            is_active=True
        )
        db.add(admin)
        await db.commit()

        print("[OK] Created test user:")
        print("  Email: test@example.com")
        print("  Password: password123")
        print("  Role: admin")


if __name__ == "__main__":
    asyncio.run(seed())
