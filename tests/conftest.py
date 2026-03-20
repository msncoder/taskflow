"""
Pytest configuration and fixtures for TaskFlow SaaS API tests.
"""
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from uuid import UUID

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.session import async_session_maker, engine, close_db
from app.db.base import Base
from app.core.security import hash_password
from app.features.user.models import User, UserRole
from app.features.company.models import Company
from sqlalchemy import text, delete


# Test database URL (using same DB but with transaction isolation)
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/taskflow_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_database():
    """
    Clean up test data before each test.
    Uses existing database schema (migrations should be applied).
    """
    # Clean up existing test data in reverse dependency order
    async with async_session_maker() as session:
        # Delete test data (in reverse FK order)
        await session.execute(text("DELETE FROM comments"))
        await session.execute(text("DELETE FROM tasks"))
        await session.execute(text("DELETE FROM invitations"))
        await session.execute(text("DELETE FROM users WHERE email LIKE '%@test.com'"))
        await session.execute(text("DELETE FROM companies WHERE slug LIKE 'test-%'"))
        await session.commit()

    yield


@pytest_asyncio.fixture(scope="function")
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create async test client for API testing.

    Usage:
        async def test_example(test_client):
            response = await test_client.get("/health")
            assert response.status_code == 200
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test/api/v1"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Create a fresh database session for each test.

    Usage:
        async def test_example(db_session):
            users = await db_session.execute(select(User))
    """
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def test_company(db_session) -> Company:
    """
    Create a test company.

    Usage:
        async def test_example(test_company):
            assert test_company.name == "Test Company"
    """
    company = Company(
        name="Test Company",
        slug="test-company"
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)
    return company


@pytest_asyncio.fixture(scope="function")
async def test_admin_user(db_session, test_company) -> User:
    """
    Create a test admin user.

    Usage:
        async def test_example(test_admin_user):
            assert test_admin_user.role == UserRole.ADMIN
    """
    user = User(
        email="admin@test.com",
        full_name="Test Admin",
        hashed_password=hash_password("password123"),
        role=UserRole.ADMIN,
        company_id=test_company.id,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_manager_user(db_session, test_company) -> User:
    """
    Create a test manager user.

    Usage:
        async def test_example(test_manager_user):
            assert test_manager_user.role == UserRole.MANAGER
    """
    user = User(
        email="manager@test.com",
        full_name="Test Manager",
        hashed_password=hash_password("password123"),
        role=UserRole.MANAGER,
        company_id=test_company.id,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_employee_user(db_session, test_company) -> User:
    """
    Create a test employee user.

    Usage:
        async def test_example(test_employee_user):
            assert test_employee_user.role == UserRole.EMPLOYEE
    """
    user = User(
        email="employee@test.com",
        full_name="Test Employee",
        hashed_password=hash_password("password123"),
        role=UserRole.EMPLOYEE,
        company_id=test_company.id,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def admin_token(test_admin_user) -> str:
    """
    Create a valid JWT access token for admin user.
    
    Usage:
        async def test_example(admin_token, test_client):
            response = await test_client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
    """
    from app.core.security import create_access_token
    
    return create_access_token({"sub": str(test_admin_user.id)})


@pytest_asyncio.fixture(scope="function")
async def manager_token(test_manager_user) -> str:
    """Create a valid JWT access token for manager user."""
    from app.core.security import create_access_token
    
    return create_access_token({"sub": str(test_manager_user.id)})


@pytest_asyncio.fixture(scope="function")
async def employee_token(test_employee_user) -> str:
    """Create a valid JWT access token for employee user."""
    from app.core.security import create_access_token
    
    return create_access_token({"sub": str(test_employee_user.id)})


# Helper factory functions

async def create_test_user(
    db_session,
    company: Company,
    email: str = None,
    role: UserRole = UserRole.EMPLOYEE,
    full_name: str = "Test User"
) -> User:
    """
    Helper factory to create a test user.
    
    Usage:
        user = await create_test_user(
            db_session,
            test_company,
            email="custom@test.com",
            role=UserRole.MANAGER
        )
    """
    if email is None:
        email = f"user_{asyncio.get_event_loop().time()}@test.com"
    
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hash_password("password123"),
        role=role,
        company_id=company.id,
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


async def create_test_company(
    db_session,
    name: str = "Test Company",
    slug: str = None
) -> Company:
    """
    Helper factory to create a test company.
    
    Usage:
        company = await create_test_company(
            db_session,
            name="Custom Company"
        )
    """
    if slug is None:
        slug = name.lower().replace(" ", "-")
    
    company = Company(name=name, slug=slug)
    db_session.add(company)
    await db_session.flush()
    await db_session.refresh(company)
    return company


async def login_user(test_client: AsyncClient, email: str, password: str = "password123") -> str:
    """
    Helper function to login and get access token.
    
    Usage:
        token = await login_user(test_client, "admin@test.com")
    """
    response = await test_client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]
