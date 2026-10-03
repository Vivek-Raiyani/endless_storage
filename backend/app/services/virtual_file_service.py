"""
Virtual File Service
====================
Business logic for creating, listing, and managing virtual files.
This service orchestrates:
1. Placement planning
2. Storage account reservation
3. Google Drive resumable session creation
4. Upload session tracking and completion
"""
import logging
import uuid
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

from app.models.virtual_file import VirtualFile, FileChunk, UploadSession
from app.models.storage_account import StorageAccount
from app.services.placement_engine import placement_engine, PlacedChunk, reserve_capacity, release_reservation, InsufficientStorageError
from app.services.providers.factory import ProviderFactory
from app.services.virtual_folder_service import has_folder_access
from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Listing / retrieval
# ---------------------------------------------------------------------------

async def list_files(db: AsyncSession, user_id: UUID, folder_id: Optional[UUID] = None) -> List[VirtualFile]:
    """List all non-deleted virtual files for a user in a folder, checking shared access."""
    if folder_id:
        has_access = await has_folder_access(db, folder_id, user_id)
        if not has_access:
            return []
            
        result = await db.execute(
            select(VirtualFile)
            .where(
                VirtualFile.folder_id == folder_id,
                VirtualFile.status != "deleted",
            )
            .order_by(VirtualFile.created_at.desc())
        )
    else:
        result = await db.execute(
            select(VirtualFile)
            .where(
                VirtualFile.user_id == user_id,
                VirtualFile.folder_id == None,
                VirtualFile.status != "deleted",
            )
            .order_by(VirtualFile.created_at.desc())
        )
    return result.scalars().all()


async def get_file(db: AsyncSession, file_id: UUID, user_id: UUID) -> Optional[VirtualFile]:
    """Get a single virtual file with its chunks loaded, verifying access via ownership or shared folders."""
    result = await db.execute(
        select(VirtualFile)
        .options(selectinload(VirtualFile.chunks))
        .where(VirtualFile.id == file_id, VirtualFile.status != "deleted")
    )
    virtual_file = result.scalars().first()
    
    if not virtual_file:
        return None
        
    if virtual_file.user_id == user_id:
        return virtual_file
        
    if virtual_file.folder_id:
        has_access = await has_folder_access(db, virtual_file.folder_id, user_id)
        if has_access:
            return virtual_file
            
    return None


async def get_upload_session(db: AsyncSession, file_id: UUID, user_id: UUID) -> Optional[UploadSession]:
    """Return the upload session for a file."""
    result = await db.execute(
        select(UploadSession).where(
            UploadSession.file_id == file_id,
            UploadSession.user_id == user_id,
        )
    )
    return result.scalars().first()


# ---------------------------------------------------------------------------
# Upload initiation
# ---------------------------------------------------------------------------

async def initiate_upload(
    db: AsyncSession,
    user_id: UUID,
    name: str,
    size: int,
    mime_type: Optional[str],
    folder_id: Optional[UUID] = None,
) -> Tuple[VirtualFile, UploadSession, List[dict]]:
    """
    Main entry point for the upload flow.

    Steps:
    1. Run placement engine to plan chunk distribution
    2. Atomically reserve capacity on chosen storage accounts
    3. Create Drive resumable upload sessions for each chunk
    4. Persist VirtualFile, FileChunk, UploadSession records
    5. Return the chunk plan to the frontend (chunk index → upload URI)

    The frontend will PUT each chunk directly to Google Drive.
    """
    # 1 — Load user's active storage accounts
    result = await db.execute(
        select(StorageAccount).where(
            StorageAccount.user_id == user_id,
            StorageAccount.status == "active",
        )
    )
    accounts = result.scalars().all()

    if not accounts:
        raise ValueError("No active storage accounts connected. Please connect a Google Drive account first.")

    # 2 — Placement planning
    try:
        placements: List[PlacedChunk] = placement_engine.plan(size, accounts)
    except InsufficientStorageError as e:
        raise ValueError(str(e))

    # 3 — Atomic reservation
    await reserve_capacity(db, placements)

    # 4 — Create VirtualFile record
    virtual_file = VirtualFile(
        user_id=user_id,
        name=name,
        mime_type=mime_type,
        size=size,
        status="uploading",
        folder_id=folder_id,
    )
    db.add(virtual_file)
    await db.flush()  # get the ID

    # 5 — Create Drive resumable sessions + FileChunk records
    # Build a map of account_id → account for quick lookup
    account_map: dict[UUID, StorageAccount] = {a.id: a for a in accounts}

    chunk_infos = []
    for p in placements:
        account = account_map[p.storage_account_id]
        
        if len(placements) == 1:
            chunk_name = virtual_file.name
            chunk_mime = virtual_file.mime_type or "application/octet-stream"
        else:
            chunk_name = f"{virtual_file.id}_chunk_{p.chunk_index}"
            chunk_mime = "application/octet-stream"

        try:
            provider = ProviderFactory.get_provider(account.provider)
            session_uri = await provider.create_resumable_upload_session(
                encrypted_refresh_token=account.encrypted_refresh_token,
                folder_id=account.root_folder_id or "root",
                filename=chunk_name,
                mime_type=chunk_mime,
                file_size=p.size,
            )
        except Exception as e:
            logger.error(f"Failed to create Drive session for chunk {p.chunk_index}: {e}")
            # Roll back reservation for this chunk
            await release_reservation(db, p.storage_account_id, p.size)
            raise ValueError(f"Failed to prepare upload for chunk {p.chunk_index}: {e}")

        chunk = FileChunk(
            file_id=virtual_file.id,
            storage_account_id=p.storage_account_id,
            chunk_index=p.chunk_index,
            offset=p.offset,
            size=p.size,
            upload_session_uri=session_uri,
            status="pending",
        )
        db.add(chunk)
        await db.flush()

        chunk_infos.append({
            "chunk_id": str(chunk.id),
            "index": p.chunk_index,
            "offset": p.offset,
            "size": p.size,
            "upload_url": session_uri,  # The frontend PUTs bytes here directly
            "storage_account_id": str(p.storage_account_id),
        })

    # 6 — Create UploadSession
    session = UploadSession(
        file_id=virtual_file.id,
        user_id=user_id,
        total_chunks=len(placements),
        completed_chunks=0,
        status="created",
    )
    db.add(session)
    await db.commit()
    await db.refresh(virtual_file)
    await db.refresh(session)

    logger.info(
        f"Upload session created: file={virtual_file.id}, "
        f"chunks={len(placements)}, size={size:,} bytes"
    )

    return virtual_file, session, chunk_infos


# ---------------------------------------------------------------------------
# Upload progress / completion
# ---------------------------------------------------------------------------

async def confirm_chunk_uploaded(
    db: AsyncSession,
    file_id: UUID,
    chunk_index: int,
    user_id: UUID,
    provider_file_id: str,
    checksum: Optional[str] = None,
) -> FileChunk:
    """
    Called by the frontend after each chunk is successfully PUT to Google Drive.
    Marks the chunk as complete, updates the upload session counter, and
    releases the reserved bytes on the storage account.
    """
    # Load chunk
    result = await db.execute(
        select(FileChunk)
        .join(VirtualFile)
        .where(
            FileChunk.file_id == file_id,
            FileChunk.chunk_index == chunk_index,
            VirtualFile.user_id == user_id,
        )
    )
    chunk = result.scalars().first()
    if not chunk:
        raise ValueError(f"Chunk {chunk_index} not found for file {file_id}")

    chunk.provider_file_id = provider_file_id
    chunk.checksum = checksum
    chunk.status = "complete"
    db.add(chunk)

    # Release reservation, add to used_bytes
    if chunk.storage_account_id:
        await db.execute(
            update(StorageAccount)
            .where(StorageAccount.id == chunk.storage_account_id)
            .values(
                reserved_bytes=StorageAccount.reserved_bytes - chunk.size,
                used_bytes=StorageAccount.used_bytes + chunk.size,
                app_used_bytes=StorageAccount.app_used_bytes + chunk.size,
            )
        )

    # Update upload session counter
    result = await db.execute(
        select(UploadSession).where(UploadSession.file_id == file_id)
    )
    session = result.scalars().first()
    if session:
        session.completed_chunks += 1
        if session.completed_chunks >= session.total_chunks:
            session.status = "completed"
            # Mark the virtual file as available
            result2 = await db.execute(
                select(VirtualFile).where(VirtualFile.id == file_id)
            )
            vf = result2.scalars().first()
            if vf:
                vf.status = "available"
                db.add(vf)
        db.add(session)

    await db.commit()
    await db.refresh(chunk)
    return chunk


# ---------------------------------------------------------------------------
# Download preparation
# ---------------------------------------------------------------------------

async def prepare_download(
    db: AsyncSession,
    file_id: UUID,
    user_id: UUID,
) -> Tuple[VirtualFile, List[dict]]:
    """
    Prepare a download by generating short-lived download URLs for each chunk.
    Returns the virtual file metadata and an ordered list of chunk download descriptors.
    The frontend fetches each chunk in parallel and streams them to disk in order.
    """
    virtual_file = await get_file(db, file_id, user_id)
    if not virtual_file:
        raise ValueError("File not found")

    if virtual_file.status != "available":
        raise ValueError(f"File is not available for download (status: {virtual_file.status})")

    chunk_downloads = []
    for chunk in sorted(virtual_file.chunks, key=lambda c: c.chunk_index):
        if not chunk.provider_file_id or not chunk.storage_account_id:
            raise ValueError(f"Chunk {chunk.chunk_index} has no provider file ID")

        # Load storage account for this chunk
        result = await db.execute(
            select(StorageAccount).where(StorageAccount.id == chunk.storage_account_id)
        )
        account = result.scalars().first()
        if not account or not account.encrypted_refresh_token:
            raise ValueError(f"Storage account for chunk {chunk.chunk_index} is unavailable")

        provider = ProviderFactory.get_provider(account.provider)
        download_url, access_token = await provider.get_download_url(
            account.encrypted_refresh_token,
            chunk.provider_file_id,
        )

        chunk_downloads.append({
            "chunk_id": str(chunk.id),
            "index": chunk.chunk_index,
            "offset": chunk.offset,
            "size": chunk.size,
            "download_url": download_url,
            "access_token": access_token,  # Short-lived — frontend attaches as Authorization header
            "checksum": chunk.checksum,
        })

    return virtual_file, chunk_downloads


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

async def delete_file(db: AsyncSession, file_id: UUID, user_id: UUID) -> bool:
    """
    Soft-delete a virtual file and attempt to delete all its chunks from Google Drive.
    """
    virtual_file = await get_file(db, file_id, user_id)
    if not virtual_file:
        return False

    virtual_file.status = "deleted"
    db.add(virtual_file)

    # Attempt to delete all chunks from Google Drive
    for chunk in virtual_file.chunks:
        if chunk.provider_file_id and chunk.storage_account_id:
            chunk.status = "pending_deletion"
            db.add(chunk)
            
            result = await db.execute(
                select(StorageAccount).where(StorageAccount.id == chunk.storage_account_id)
            )
            account = result.scalars().first()
            if account and account.encrypted_refresh_token:
                try:
                    provider = ProviderFactory.get_provider(account.provider)
                    await provider.delete_file(
                        account.encrypted_refresh_token,
                        chunk.provider_file_id,
                    )
                    
                    # If successful, mark as fully deleted
                    chunk.status = "deleted"
                    db.add(chunk)
                    
                    # Update used_bytes and app_used_bytes
                    await db.execute(
                        update(StorageAccount)
                        .where(StorageAccount.id == chunk.storage_account_id)
                        .values(
                            used_bytes=StorageAccount.used_bytes - chunk.size,
                            app_used_bytes=StorageAccount.app_used_bytes - chunk.size,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to delete chunk {chunk.id} from Drive. Marked as pending_deletion: {e}")
                    # Bytes are NOT freed, it remains as pending_deletion

    await db.commit()
    return True


async def rename_file(db: AsyncSession, file_id: UUID, user_id: UUID, new_name: str) -> Optional[VirtualFile]:
    """Rename a virtual file."""
    virtual_file = await get_file(db, file_id, user_id)
    if not virtual_file:
        return None
    virtual_file.name = new_name
    db.add(virtual_file)
    await db.commit()
    await db.refresh(virtual_file)
    return virtual_file
