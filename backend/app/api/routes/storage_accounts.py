"""
Storage Accounts API
====================
Routes for connecting, listing, and managing Google Drive accounts.
The Google OAuth flow for Drive access is separate from the login OAuth flow —
it uses the offline access scope to obtain a refresh token.
"""
import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.oauth_clients import oauth
from app.api import deps
from app.core.config import settings
from app.models.user import User
from app.schemas.storage import (
    StorageAccountOut,
    StorageSummaryOut,
    DisconnectPreviewResponse,
    DisconnectRequest,
)
from app.schemas.response import DataResponse, MessageResponse
from app.services import storage_account_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=DataResponse[List[StorageAccountOut]])
async def list_storage_accounts(
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """List all connected Google Drive accounts for the current user."""
    accounts = await storage_account_service.get_accounts_for_user(db, current_user.id)
    return DataResponse(data=[StorageAccountOut.from_orm_with_computed(a) for a in accounts])


@router.get("/summary", response_model=DataResponse[StorageSummaryOut])
async def get_storage_summary(
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Get aggregated storage metrics across all connected accounts."""
    summary = await storage_account_service.get_user_storage_summary(db, current_user.id)
    return DataResponse(data=summary)


@router.get("/connect/google")
async def connect_google_drive(
    request: Request,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Initiates the Google OAuth flow to connect a new Drive account.
    The user is redirected to Google's consent screen requesting Drive file access.
    """
    redirect_uri = str(request.url_for("connect_google_drive_callback"))
    # Store user_id in session so the callback knows who to associate the account with
    request.session["connecting_user_id"] = str(current_user.id)
    logger.info(f"Starting Drive connect flow for user {current_user.id}")
    return await oauth.google_drive.authorize_redirect(
        request, 
        redirect_uri, 
        access_type="offline", 
        prompt="consent"
    )


@router.get("/connect/google/callback", name="connect_google_drive_callback")
async def connect_google_drive_callback(
    request: Request,
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Handles the Google OAuth callback after Drive consent.
    Extracts the refresh token, encrypts it, and stores the account.
    """
    user_id_str = request.session.get("connecting_user_id")
    if not user_id_str:
        raise HTTPException(status_code=400, detail="No user session found. Please try again.")

    try:
        token = await oauth.google_drive.authorize_access_token(request)
    except Exception as e:
        logger.error(f"Drive OAuth error: {e}")
        raise HTTPException(status_code=400, detail="Google Drive authorization failed.")

    refresh_token = token.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="No refresh token returned. Make sure to grant offline access and use 'prompt=consent'.",
        )

    user_info = token.get("userinfo", {})
    provider_account_id = user_info.get("sub", "")
    provider_email = user_info.get("email", "")

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID in session")

    account = await storage_account_service.connect_google_drive_account(
        db=db,
        user_id=user_id,
        provider_account_id=provider_account_id,
        provider_account_email=provider_email,
        refresh_token=refresh_token,
    )

    logger.info(f"Connected Drive account {provider_email} for user {user_id}")
    redirect_url = f"{settings.FRONTEND_URL}/drive"
    return RedirectResponse(url=redirect_url)


@router.post("/{account_id}/sync", response_model=DataResponse[StorageAccountOut])
async def sync_account_quota(
    account_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Re-fetch quota information from Google Drive for a specific account."""
    account = await storage_account_service.get_account(db, account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Storage account not found")
    account = await storage_account_service.sync_quota(db, account)
    return DataResponse(data=StorageAccountOut.from_orm_with_computed(account))


@router.get("/{account_id}/disconnect-preview", response_model=DataResponse[DisconnectPreviewResponse])
async def preview_disconnect(
    account_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Preview the impact of disconnecting an account and check if migration is possible."""
    try:
        preview = await storage_account_service.preview_disconnect(db, account_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return DataResponse(data=preview)


@router.post("/{account_id}/disconnect", response_model=DataResponse[StorageAccountOut])
async def disconnect_account(
    account_id: UUID,
    body: DisconnectRequest,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Initiate a disconnect (either migrate or delete)."""
    try:
        account = await storage_account_service.disconnect_account(
            db, account_id, current_user.id, action=body.action
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return DataResponse(data=StorageAccountOut.from_orm_with_computed(account))
