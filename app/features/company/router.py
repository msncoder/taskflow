from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import AdminUser, get_db
from app.features.company.schemas import CompanyRead
from app.features.company.service import get_user_company

router = APIRouter(prefix="/company", tags=["Company"])


@router.get("/me", response_model=CompanyRead)
async def get_my_company(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> CompanyRead:
    """
    Get the current user's company.
    
    **Admin only** - Returns the company associated with the authenticated admin user.
    
    Returns:
        Company: Current user's company data
    """
    return await get_user_company(db=db, user_id=current_user.id)
