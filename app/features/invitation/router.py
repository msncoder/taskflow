from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, CurrentUser, AdminUser, ManagerUser
from app.features.invitation.schemas import (
    InviteRequest,
    AcceptInviteRequest,
    InvitationRead,
)
from app.features.invitation.service import (
    send_invitation,
    accept_invitation,
    list_company_invitations,
)
from app.features.auth.schemas import TokenResponse

router = APIRouter(prefix="/invitations", tags=["Invitations"])


@router.post(
    "/",
    response_model=InvitationRead,
    status_code=201,
    summary="Send Invitation",
)
async def create_invitation(
    request: InviteRequest,
    background_tasks: BackgroundTasks,
    current_user: ManagerUser,
    db: AsyncSession = Depends(get_db),
) -> InvitationRead:
    """
    Send an invitation to a user.

    **Permissions:**
    - Admin: Can invite managers and employees
    - Manager: Can only invite employees
    - Employee: Cannot send invitations

    Args:
        request: Invitation request with email and role
        current_user: Authenticated user (Admin or Manager)
        db: Database session

    Returns:
        Invitation: Created invitation details
    """
    invitation = await send_invitation(
        db=db,
        inviter=current_user,
        email=request.email,
        role=request.role,
    )

    # TODO: Send email in background
    # invite_link = f"{settings.frontend_url}/accept-invite?token={invitation.token}"
    # background_tasks.add_task(send_email, invitation.email, "Invitation to TaskFlow", invite_link)

    return InvitationRead.model_validate(invitation)


@router.get(
    "/",
    response_model=list[InvitationRead],
    summary="List Invitations",
)
async def list_invitations(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> list[InvitationRead]:
    """
    List all invitations for the company.

    **Admin only** - Returns all invitations (pending, accepted, expired)
    for the authenticated user's company.

    Args:
        current_user: Authenticated admin user
        db: Database session

    Returns:
        list[Invitation]: List of all company invitations
    """
    invitations = await list_company_invitations(
        db=db,
        company_id=current_user.company_id,
    )
    return [InvitationRead.model_validate(inv) for inv in invitations]


@router.post(
    "/accept",
    response_model=TokenResponse,
    summary="Accept Invitation",
)
async def accept_invitation_endpoint(
    request: AcceptInviteRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Accept an invitation and create a user account.

    This endpoint is **public** - no authentication required.
    The invitation token serves as the authentication mechanism.

    Args:
        request: Accept invitation request with token, full_name, and password
        db: Database session

    Returns:
        TokenResponse: JWT access and refresh tokens

    Raises:
        NotFoundException: If invitation token is invalid
        BadRequestException: If invitation is expired or already accepted
        ConflictException: If email already registered
    """
    return await accept_invitation(
        db=db,
        token=request.token,
        full_name=request.full_name,
        password=request.password,
    )
