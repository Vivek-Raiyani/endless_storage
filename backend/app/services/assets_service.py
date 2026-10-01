from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, UploadFile
import uuid

from app.models.assets import Asset
from app.models.user import User
from app.utils.storage import storage
from app.core.config import settings

import os
import logging

logger = logging.getLogger(__name__)

async def request_upload_url(
    db: AsyncSession,
    user_id: uuid.UUID,
    filename: str,
    content_type: str,
    file_size: int,
    folder: str = "assets/common",
) -> tuple[Asset, str, dict, str]:
    """
    Generates a presigned URL (or local upload URL) for direct upload.
    Creates an Asset record in 'pending' status.
    """
    if content_type not in settings.ALLOWED_IMAGE_TYPES and content_type not in settings.ALLOWED_VIDEO_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Only images and videos are allowed.")

    if content_type in settings.ALLOWED_IMAGE_TYPES and file_size > settings.MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail=f"Image file too large. Max size is {settings.MAX_IMAGE_SIZE / (1024*1024)}MB.")
    
    if content_type in settings.ALLOWED_VIDEO_TYPES and file_size > settings.MAX_VIDEO_SIZE:
        raise HTTPException(status_code=400, detail=f"Video file too large. Max size is {settings.MAX_VIDEO_SIZE / (1024*1024)}MB.")

    # Check quota
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.subscription_tier == "free" and (user.storage_used + file_size) > 104857600: # 100MB
        raise HTTPException(status_code=400, detail="Storage limit exceeded for free tier. Max 100MB.")

    original_filename = os.path.basename(filename or "file")
    name, ext = os.path.splitext(original_filename)

    if ext[1:].lower() not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file extension. Only image and video extensions are allowed.")

    unique_filename = f"{name}_{uuid.uuid4().hex}{ext}"

    storage_key, upload_url, fields = storage.generate_upload_url(
        user_id=str(user_id),
        service=folder,
        filename=unique_filename,
        file_size=file_size,
    )

    provider = "s3" if hasattr(storage, 's3_client') else "local"

    asset = Asset(
        uploaded_by=user_id,
        folder=folder,
        filename=unique_filename,
        storage_key=storage_key,
        # For local, URL will be updated upon completion. For S3, we know it now.
        file_url=storage.get_file_url(storage_key) if provider == "s3" else "", 
        content_type=content_type,
        file_size=file_size,
        status="pending"
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    
    # If local, append asset_id to the URL for the local-upload handler
    if provider == "local":
        upload_url = f"{upload_url}/{asset.id}"

    return asset, upload_url, fields, provider

async def complete_local_upload(
    db: AsyncSession,
    user_id: uuid.UUID,
    asset_id: uuid.UUID,
    file: UploadFile
) -> Asset:
    """
    Handles the actual file upload for the local storage fallback.
    """
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.uploaded_by == user_id, Asset.status == "pending")
    )
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Pending asset not found")
        
    file_bytes = await file.read()
    
    # Force use local upload method directly avoiding generate_presigned logic
    if not hasattr(storage, 'base_dir'):
        raise HTTPException(status_code=400, detail="Local upload called but storage provider is not local")
        
    # Manually write it
    file_path = os.path.join(storage.base_dir, asset.storage_key)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    asset.file_url = storage.get_file_url(asset.storage_key)
    asset.status = "completed"
    
    # Update quota
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    user.storage_used += asset.file_size
    
    await db.commit()
    await db.refresh(asset)
    return asset
    
async def complete_cloud_upload(
    db: AsyncSession,
    user_id: uuid.UUID,
    asset_id: uuid.UUID
) -> Asset:
    """
    Marks a cloud upload as completed and updates quota.
    """
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.uploaded_by == user_id, Asset.status == "pending")
    )
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Pending asset not found")
        
    asset.status = "completed"
    
    # Update quota
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    user.storage_used += asset.file_size
    
    await db.commit()
    await db.refresh(asset)
    return asset


async def delete_asset(
    db: AsyncSession,
    user_id: uuid.UUID,
    asset_id: uuid.UUID,
) -> None:
    """
    Looks up the Asset record by ID, deletes the file from storage using the
    persisted storage_key, then removes the DB record.
    Raises 404 if the asset doesn't exist or doesn't belong to the user.
    """
    logger.info(f"Deleting asset {asset_id} for user {user_id}")
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.uploaded_by == user_id)
    )
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    storage.delete_file(asset.storage_key)
    
    # Update quota if completed
    if asset.status == "completed":
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        user.storage_used = max(0, user.storage_used - asset.file_size)
    
    await db.delete(asset)
    await db.commit()


async def get_asset_url(
    db: AsyncSession,
    user_id: uuid.UUID,
    asset_id: uuid.UUID,
) -> str:
    """
    Returns a fresh URL for the asset (presigned for cloud, static for local).
    For cloud storage the presigned URL is regenerated on each call so clients
    always get a valid, unexpired link.
    """
    logger.info(f"Getting URL for asset {asset_id} (user {user_id})")
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.uploaded_by == user_id)
    )
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return storage.get_file_url(asset.storage_key)


async def list_assets(
    db: AsyncSession,
    user_id: uuid.UUID,
    folder: str | None = None,
) -> list[Asset]:
    """
    Lists all Asset records for the user, optionally filtered by folder.
    """
    logger.info(f"Listing assets for user {user_id} (folder: {folder})")
    query = select(Asset).where(Asset.uploaded_by == user_id)
    if folder:
        query = query.where(Asset.folder.like(f"assets/{folder}%" if folder != "" else "assets/%" ) )
    query = query.order_by(Asset.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()
