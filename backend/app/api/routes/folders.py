import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.storage import (
    VirtualFolderOut,
    CreateFolderRequest,
    UpdateFolderRequest,
    ShareFolderRequest,
    FolderDownloadPrepareResponse,
)
from app.schemas.response import DataResponse, MessageResponse
from app.services import virtual_folder_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=DataResponse[VirtualFolderOut])
async def create_folder(
    body: CreateFolderRequest,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Create a new virtual folder."""
    folder = await virtual_folder_service.create_folder(
        db=db,
        user_id=current_user.id,
        name=body.name,
        parent_id=body.parent_id,
        color=body.color,
    )
    return DataResponse(data=folder)


@router.get("/shared", response_model=DataResponse[List[VirtualFolderOut]])
async def list_shared_folders(
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """List all folders that have been shared with the current user."""
    folders = await virtual_folder_service.get_shared_folders(
        db=db,
        user_id=current_user.id,
    )
    return DataResponse(data=folders)


@router.get("/", response_model=DataResponse[List[VirtualFolderOut]])
async def list_folders(
    parent_id: Optional[UUID] = Query(None, description="List folders inside this parent"),
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """List all folders in the specified parent folder."""
    folders = await virtual_folder_service.list_folders(
        db=db,
        user_id=current_user.id,
        parent_id=parent_id,
    )
    return DataResponse(data=folders)


@router.get("/{folder_id}", response_model=DataResponse[VirtualFolderOut])
async def get_folder(
    folder_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Get a specific folder."""
    folder = await virtual_folder_service.get_folder(db, folder_id, current_user.id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return DataResponse(data=folder)


@router.patch("/{folder_id}", response_model=DataResponse[VirtualFolderOut])
async def update_folder(
    folder_id: UUID,
    body: UpdateFolderRequest,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Rename, move, or change metadata of a folder."""
    folder = await virtual_folder_service.update_folder(
        db=db,
        folder_id=folder_id,
        user_id=current_user.id,
        name=body.name,
        parent_id=body.parent_id,
        color=body.color,
        starred=body.starred,
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return DataResponse(data=folder)


@router.delete("/{folder_id}", response_model=MessageResponse)
async def delete_folder(
    folder_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Delete a folder and all its contents (files and subfolders)."""
    success = await virtual_folder_service.delete_folder(db, folder_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Folder not found")
    return MessageResponse(message="Folder deleted successfully")

@router.post("/{folder_id}/share", response_model=MessageResponse)
async def share_folder(
    folder_id: UUID,
    body: ShareFolderRequest,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Share a folder with another user by their email address."""
    try:
        await virtual_folder_service.share_folder(
            db=db,
            folder_id=folder_id,
            owner_id=current_user.id,
            target_email=body.target_user_email,
            role=body.role,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return MessageResponse(message=f"Folder successfully shared with {body.target_user_email}")


@router.delete("/{folder_id}/share/{target_email}", response_model=MessageResponse)
async def unshare_folder(
    folder_id: UUID,
    target_email: str,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Revoke a user's access to a shared folder."""
    try:
        await virtual_folder_service.unshare_folder(
            db=db,
            folder_id=folder_id,
            owner_id=current_user.id,
            target_email=target_email,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return MessageResponse(message=f"Access revoked for {target_email}")


@router.get("/{folder_id}/download", response_model=DataResponse[FolderDownloadPrepareResponse])
async def prepare_folder_download(
    folder_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Prepare a recursive download for a folder.
    Returns the folder metadata and a list of all files with their relative paths
    and chunk download URLs for client-side zipping.
    """
    try:
        data = await virtual_folder_service.prepare_folder_download(db, folder_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
        
    return DataResponse(data=data)

