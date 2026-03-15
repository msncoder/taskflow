import secrets
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, create_access_token, create_refresh_token
from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
    BadRequestException,
    ConflictException,
)
from app.features.user.models import User, UserRole
from app.features.invitation.models import Invitation, InvitationRole


INVITATION_EXPIRY_HOURS = 48


async def send_invitation(
    db: AsyncSession,
    inviter: User,
    email: str,
    role: InvitationRole,
) -> Invitation:
    """
    Send an invitation to a user.

    Args:
        db: AsyncSession database session
        inviter: User sending the invitation
        email: Email address of the invitee
        role: Role to assign (manager or employee)

    Returns:
        Invitation instance

    Raises:
        ForbiddenException: If inviter lacks permission
        ConflictException: If invitation already exists for this email
    """
    # Validate inviter's permission
    if inviter.role == UserRole.EMPLOYEE:
        raise ForbiddenException("Employees cannot send invitations")

    if inviter.role == UserRole.MANAGER and role != InvitationRole.EMPLOYEE:
        raise ForbiddenException("Managers can only invite employees")

    # Check if invitation already exists for this email (pending)
    existing_result = await db.execute(
        select(Invitation).where(
            Invitation.email == email,
            Invitation.company_id == inviter.company_id,
            Invitation.is_accepted == False,
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise ConflictException("An invitation for this email already exists")

    # Check if user with this email already exists in the company
    existing_user_result = await db.execute(
        select(User).where(
            User.email == email,
            User.company_id == inviter.company_id,
        )
    )
    if existing_user_result.scalar_one_or_none():
        raise ConflictException("A user with this email already exists in your company")

    # Generate secure token
    token = secrets.token_urlsafe(32)

    # Set expiration time
    expires_at = datetime.now(timezone.utc) + timedelta(hours=INVITATION_EXPIRY_HOURS)

    # Create invitation
    invitation = Invitation(
        email=email,
        role=role,
        company_id=inviter.company_id,
        token=token,
        expires_at=expires_at,
    )
    db.add(invitation)
    await db.flush()
    await db.refresh(invitation)

    # TODO: Send email with invite link using BackgroundTasks
    # invite_link = f"{settings.frontend_url}/accept-invite?token={token}"
    # await send_email(email, "You've been invited to TaskFlow!", invite_link)

    return invitation


async def accept_invitation(
    db: AsyncSession,
    token: str,
    full_name: str,
    password: str,
) -> dict[str, Any]:
    """
    Accept an invitation and create a user account.

    Args:
        db: AsyncSession database session
        token: Invitation token
        full_name: Full name of the invitee
        password: Password for the new account

    Returns:
        dict with access_token, refresh_token, token_type

    Raises:
        NotFoundException: If invitation not found
        BadRequestException: If invitation is expired or already accepted
        ConflictException: If email already registered
    """
    # Find invitation by token
    result = await db.execute(
        select(Invitation).where(Invitation.token == token)
    )
    invitation = result.scalar_one_or_none()

    if invitation is None:
        raise NotFoundException("Invalid invitation token")

    # Check if already accepted
    if invitation.is_accepted:
        raise BadRequestException("This invitation has already been accepted")

    # Check if expired
    if invitation.is_expired:
        raise BadRequestException("This invitation has expired")

    # Check if email already exists (user might have registered separately)
    existing_user_result = await db.execute(
        select(User).where(User.email == invitation.email)
    )
    if existing_user_result.scalar_one_or_none():
        raise ConflictException("Email already registered")

    # Map invitation role to user role
    user_role = UserRole.MANAGER if invitation.role == InvitationRole.MANAGER else UserRole.EMPLOYEE

    # Create user
    hashed_pw = hash_password(password)
    user = User(
        email=invitation.email,
        full_name=full_name,
        hashed_password=hashed_pw,
        role=user_role,
        company_id=invitation.company_id,
        is_active=True,
    )
    db.add(user)

    # Mark invitation as accepted
    invitation.is_accepted = True

    await db.flush()
    await db.refresh(user)

    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def get_invitation_by_token(
    db: AsyncSession,
    token: str,
) -> Invitation:
    """
    Get invitation by token.

    Args:
        db: AsyncSession database session
        token: Invitation token

    Returns:
        Invitation instance

    Raises:
        NotFoundException: If invitation not found
    """
    result = await db.execute(
        select(Invitation).where(Invitation.token == token)
    )
    invitation = result.scalar_one_or_none()

    if invitation is None:
        raise NotFoundException("Invitation not found")

    return invitation


async def list_company_invitations(
    db: AsyncSession,
    company_id: uuid.UUID,
) -> list[Invitation]:
    """
    List all invitations for a company.

    Args:
        db: AsyncSession database session
        company_id: Company UUID

    Returns:
        List of Invitation instances
    """
    result = await db.execute(
        select(Invitation)
        .where(Invitation.company_id == company_id)
        .order_by(Invitation.created_at.desc())
    )
    return list(result.scalars().all())


async def revoke_invitation(
    db: AsyncSession,
    invitation_id: uuid.UUID,
    company_id: uuid.UUID,
) -> None:
    """
    Revoke an invitation.

    Args:
        db: AsyncSession database session
        invitation_id: Invitation UUID
        company_id: Company UUID (for authorization)

    Raises:
        NotFoundException: If invitation not found
    """
    result = await db.execute(
        select(Invitation).where(
            Invitation.id == invitation_id,
            Invitation.company_id == company_id,
        )
    )
    invitation = result.scalar_one_or_none()

    if invitation is None:
        raise NotFoundException("Invitation not found")

    await db.delete(invitation)
    await db.flush()
