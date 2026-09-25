from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, UploadFile
import uuid

from app.models.assets import Asset
from app.utils.storage import storage


async def upload_asset(
    db: AsyncSession,
    user_id: uuid.UUID,
    file: UploadFile,
    folder: str = "assets/common",
) -> Asset:
    """
    Reads the uploaded file, persists it via the storage provider,
    then creates and saves an Asset record in the database.
    Returns the newly created Asset.
    """
    file_bytes = await file.read()
    filename = file.filename or f"file_{uuid.uuid4().hex}"

    storage_key, file_url = storage.upload_file(
        user_id=str(user_id),
        service=folder,
        filename=filename,
        file_bytes=file_bytes,
    )

    asset = Asset(
        user_id=user_id,
        folder=folder,
        filename=filename,
        storage_key=storage_key,
        file_url=file_url,
        content_type=file.content_type,
        file_size=len(file_bytes),
    )
    db.add(asset)
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
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.user_id == user_id)
    )
    asset = result.scalars().first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    storage.delete_file(asset.storage_key)
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
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.user_id == user_id)
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
    query = select(Asset).where(Asset.user_id == user_id)
    if folder:
        query = query.where(Asset.folder.like(f"assets/{folder}%" if folder != "" else "assets/%" ) )
    query = query.order_by(Asset.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()
