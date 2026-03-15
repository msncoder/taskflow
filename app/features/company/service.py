import re
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.company.models import Company
from app.core.exceptions import NotFoundException


def generate_slug(name: str) -> str:
    """
    Generate a URL-friendly slug from a company name.
    
    Example: "Acme Corp" -> "acme-corp"
    """
    # Convert to lowercase
    slug = name.lower()
    # Replace spaces and underscores with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)
    # Remove non-alphanumeric characters except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    # Collapse multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug


async def create_company(db: AsyncSession, name: str) -> Company:
    """
    Create a new company with auto-generated slug.
    
    Args:
        db: AsyncSession database session
        name: Company name
        
    Returns:
        Created Company instance
    """
    slug = generate_slug(name)
    
    company = Company(name=name, slug=slug)
    db.add(company)
    await db.flush()  # Flush to get the ID before commit
    await db.refresh(company)
    
    return company


async def get_company_by_id(db: AsyncSession, company_id: UUID) -> Company:
    """
    Get a company by its ID.
    
    Args:
        db: AsyncSession database session
        company_id: Company UUID
        
    Returns:
        Company instance
        
    Raises:
        NotFoundException: If company not found
    """
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if company is None:
        raise NotFoundException("Company not found")
    
    return company


async def get_company_by_slug(db: AsyncSession, slug: str) -> Company:
    """
    Get a company by its slug.
    
    Args:
        db: AsyncSession database session
        slug: Company slug
        
    Returns:
        Company instance
        
    Raises:
        NotFoundException: If company not found
    """
    result = await db.execute(select(Company).where(Company.slug == slug))
    company = result.scalar_one_or_none()
    
    if company is None:
        raise NotFoundException("Company not found")
    
    return company


async def get_user_company(db: AsyncSession, user_id: UUID) -> Company:
    """
    Get the company associated with a user.
    
    Args:
        db: AsyncSession database session
        user_id: User UUID
        
    Returns:
        Company instance
        
    Raises:
        NotFoundException: If company not found
    """
    from app.features.user.models import User
    
    result = await db.execute(
        select(Company)
        .join(User)
        .where(User.id == user_id)
    )
    company = result.scalar_one_or_none()
    
    if company is None:
        raise NotFoundException("Company not found")
    
    return company
