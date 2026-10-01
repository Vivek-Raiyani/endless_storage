from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
import re
import logging

logger = logging.getLogger(__name__)

from app.api import deps
from app.models.user import User
from app.schemas.response import DataResponse, MessageResponse
from app.schemas.assets import AssetResponse, AssetUploadResponse
from app.services import assets_service

router = APIRouter()


@router.post("/upload", response_model=DataResponse[AssetUploadResponse])
async def upload_file(
    file: UploadFile = File(...),
    folder: str = "common",
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Upload an asset file. The file is stored and a DB record is created.
    Returns the asset ID and URL so the caller can reference or delete it later.
    """
    logger.info(f"User {current_user.id} uploading file to folder {folder}")
    safe_folder = re.sub(r'[^a-zA-Z0-9_\-]', '', folder) or "common"
    
    asset = await assets_service.upload_asset(
        db=db,
        user_id=current_user.id,
        file=file,
        folder=f"assets/{safe_folder}",
    )
    return DataResponse(data=AssetUploadResponse(id=asset.id, url=asset.file_url, filename=asset.filename))


@router.get("/list", response_model=DataResponse[list[AssetResponse]])
async def list_files(
    folder: Optional[str] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    List all assets for the current user, optionally filtered by folder.
    """
    logger.info(f"User {current_user.id} fetching asset list (folder={folder})")
    safe_folder = re.sub(r'[^a-zA-Z0-9_\-]', '', folder) if folder else None
    
    assets = await assets_service.list_assets(
        db=db,
        user_id=current_user.id,
        folder=safe_folder,
    )
    return DataResponse(data=[AssetResponse.model_validate(a) for a in assets])


@router.get("/url/{asset_id}", response_model=DataResponse[str])
async def get_file_url(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get a fresh URL for an asset.
    For cloud storage this returns a newly generated presigned URL.
    """
    url = await assets_service.get_asset_url(
        db=db,
        user_id=current_user.id,
        asset_id=asset_id,
    )
    return DataResponse(data=url)


@router.delete("/delete/{asset_id}", response_model=MessageResponse)
async def delete_file(
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete an asset by its ID. Removes the file from storage and the DB record.
    """
    await assets_service.delete_asset(
        db=db,
        user_id=current_user.id,
        asset_id=asset_id,
    )
    return MessageResponse(message="Asset successfully deleted")
