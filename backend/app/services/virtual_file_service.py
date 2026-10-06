"""
Virtual File Service
====================
Business logic for creating, listing, and managing virtual files.
This service orchestrates:
1. Placement planning
2. Storage account reservation
3. Google Drive resumable session creation
4. Upload session tracking and completion
5. Trash / restore / permanent deletion (Drive-style lifecycle)

File lifecycle
--------------
    uploading ──confirm all chunks──▶ available ──trash──▶ (is_deleted=True) ──restore──▶ available
        │                                 │                       │
        └──cancel / expired──▶ deleted ◀──┴───delete forever──────┘

"deleted" files keep their row; their chunks become `pending_deletion` and are removed
from Google Drive by the cleanup job (see internal/doubts-plan.md — 404 rescue flow).
"""
import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.virtual_file import VirtualFile, FileChunk, UploadSession
from app.models.virtual_folder import VirtualFolder
from app.models.storage_account import StorageAccount
from app.services.placement_engine import placement_engine, PlacedChunk, reserve_capacity, InsufficientStorageError
from app.services.providers.factory import ProviderFactory
from app.services.virtual_folder_service import get_folder_role, role_at_least, _UNSET
from app.services.errors import NotFoundError, ForbiddenError, ConflictError
from app.core.config import settings

logger = logging.getLogger(__name__)

FILE_SORT_COLUMNS = {
    "name": VirtualFile.name,
    "size": VirtualFile.size,
    "created_at": VirtualFile.created_at,
    "updated_at": VirtualFile.updated_at,
}


# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------

async def get_file_role(db: AsyncSession, virtual_file: VirtualFile, user_id: UUID) -> Optional[str]:
    """Effective role on a file: the file owner is "owner"; otherwise inherited from its folder."""
    if virtual_file.user_id == user_id:
        return "owner"
    if virtual_file.folder_id:
        return await get_folder_role(db, virtual_file.folder_id, user_id)
    return None


async def require_file(
    db: AsyncSession,
    file_id: UUID,
    user_id: UUID,
    required: str = "viewer",
    include_trashed: bool = False,
) -> Tuple[VirtualFile, str]:
    """Load a file and assert the user has at least `required` role on it."""
    virtual_file = await db.get(VirtualFile, file_id)
    if (
        not virtual_file
        or virtual_file.status == "deleted"
        or (virtual_file.is_deleted and not include_trashed)
    ):
        raise NotFoundError("File not found")
    role = await get_file_role(db, virtual_file, user_id)
    if role is None:
        raise NotFoundError("File not found")
    if not role_at_least(role, required):
        raise ForbiddenError(f"You need {required} access to do this")
    return virtual_file, role


# ---------------------------------------------------------------------------
# Listing / retrieval
# ---------------------------------------------------------------------------

async def search_files(db: AsyncSession, user_id: UUID, query: str) -> List[VirtualFile]:
    if not query.strip():
        return []
    q = f"%{query}%"
    result = await db.execute(
        select(VirtualFile)
        .where(
            VirtualFile.user_id == user_id,
            VirtualFile.is_deleted == False,
            VirtualFile.name.ilike(q)
        )
        .order_by(VirtualFile.name)
        .limit(50)
    )
    return list(result.scalars().all())


async def list_files(
    db: AsyncSession,
    user_id: UUID,
    folder_id: Optional[UUID] = None,
    thumbnail: Optional[str] = None,
    sort_by: str = "name",
    order: str = "asc",
) -> List[VirtualFile]:
    """List available (not uploading, not trashed) files in a folder, checking shared access."""
    if folder_id:
        if await get_folder_role(db, folder_id, user_id) is None:
            raise NotFoundError("Folder not found")
        stmt = select(VirtualFile).where(VirtualFile.folder_id == folder_id)
    else:
        stmt = select(VirtualFile).where(
            VirtualFile.user_id == user_id,
            VirtualFile.folder_id == None,
        )
    stmt = stmt.where(VirtualFile.status == "available", VirtualFile.is_deleted == False)
    column = FILE_SORT_COLUMNS.get(sort_by, VirtualFile.name)
    stmt = stmt.order_by(column.desc() if order == "desc" else column.asc())
    return (await db.execute(stmt)).scalars().all()


async def get_file(db: AsyncSession, file_id: UUID, user_id: UUID) -> Optional[VirtualFile]:
    """Get a single non-trashed virtual file the user can view (owner or shared folder)."""
    try:
        virtual_file, _ = await require_file(db, file_id, user_id, required="viewer")
        return virtual_file
    except (NotFoundError, ForbiddenError):
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

async def _release_reservations(db: AsyncSession, placements: List[PlacedChunk]) -> None:
    """Undo reserve_capacity() for an entire placement plan."""
    totals: Dict[UUID, int] = {}
    for p in placements:
        totals[p.storage_account_id] = totals.get(p.storage_account_id, 0) + p.size
    for account_id, size in totals.items():
        await db.execute(
            update(StorageAccount)
            .where(StorageAccount.id == account_id)
            .values(reserved_bytes=StorageAccount.reserved_bytes - size)
        )
    await db.commit()


async def initiate_upload(
    db: AsyncSession,
    user_id: UUID,
    name: str,
    size: int,
    mime_type: Optional[str],
    folder_id: Optional[UUID] = None,
    thumbnail: Optional[str] = None,
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
    Uploading into a shared folder requires editor access; bytes are stored on the
    uploader's own connected drives.
    """
    if folder_id:
        role = await get_folder_role(db, folder_id, user_id)
        if role is None:
            raise NotFoundError("Folder not found")
        if not role_at_least(role, "editor"):
            raise ForbiddenError("You need editor access to upload into this folder")

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

    try:
        # 4 — Create VirtualFile record
        virtual_file = VirtualFile(
            user_id=user_id,
            name=name.strip(),
            mime_type=mime_type,
            size=size,
            thumbnail=thumbnail,
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
    except Exception:
        # Nothing was committed for the file — roll back and release EVERY reservation
        # (previously only the failing chunk's bytes were released, leaking the rest).
        await db.rollback()
        await _release_reservations(db, placements)
        raise

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

    Idempotent: confirming an already-complete chunk is a no-op (safe for client retries).
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
        raise NotFoundError(f"Chunk {chunk_index} not found for file {file_id}")

    if chunk.status in ("complete", "verified"):
        return chunk

    virtual_file = await db.get(VirtualFile, file_id)
    if not virtual_file or virtual_file.status != "uploading":
        raise ConflictError("This upload is no longer active")

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
        session.status = "uploading"
        if session.completed_chunks >= session.total_chunks:
            session.status = "completed"
            # Mark the virtual file as available
            virtual_file.status = "available"
            db.add(virtual_file)
        db.add(session)

    await db.commit()
    await db.refresh(chunk)
    return chunk


async def _retire_file_chunks(db: AsyncSession, file_id: UUID) -> None:
    """
    Queue a file's chunks for removal:
    - uploaded chunks  -> `pending_deletion` (cleanup job deletes them from Drive & frees bytes)
    - never-uploaded   -> `deleted` immediately, and their reserved bytes are released
    """
    chunks = (await db.execute(
        select(FileChunk).where(FileChunk.file_id == file_id, FileChunk.status != "deleted")
    )).scalars().all()
    for chunk in chunks:
        if chunk.status in ("complete", "verified", "pending_deletion") and chunk.provider_file_id:
            chunk.status = "pending_deletion"
        else:
            if chunk.status in ("pending", "uploading") and chunk.storage_account_id:
                await db.execute(
                    update(StorageAccount)
                    .where(StorageAccount.id == chunk.storage_account_id)
                    .values(reserved_bytes=StorageAccount.reserved_bytes - chunk.size)
                )
            chunk.status = "deleted"
        db.add(chunk)


async def cancel_upload(db: AsyncSession, file_id: UUID, user_id: UUID) -> None:
    """Cancel an in-progress upload (upload tray ✕). Releases reservations, queues uploaded chunks."""
    virtual_file = await db.get(VirtualFile, file_id)
    if not virtual_file or virtual_file.user_id != user_id:
        raise NotFoundError("Upload not found")
    if virtual_file.status != "uploading":
        raise ConflictError("This file is not uploading")

    await _retire_file_chunks(db, file_id)
    virtual_file.status = "deleted"
    db.add(virtual_file)
    session = (await db.execute(select(UploadSession).where(UploadSession.file_id == file_id))).scalars().first()
    if session:
        session.status = "failed"
        db.add(session)
    await db.commit()


# ---------------------------------------------------------------------------
# Download preparation
# ---------------------------------------------------------------------------

async def build_chunk_downloads(
    db: AsyncSession,
    virtual_file: VirtualFile,
    token_cache: Optional[dict] = None,
) -> List[dict]:
    """
    Ordered chunk download descriptors (URL + short-lived Bearer token) for one file.
    `token_cache` (account_id -> (token, expires_at)) is shared across files in a folder download.
    Raises ValueError if any chunk is not downloadable.
    """
    token_cache = token_cache if token_cache is not None else {}
    chunks = (await db.execute(
        select(FileChunk)
        .where(FileChunk.file_id == virtual_file.id, FileChunk.status.in_(["complete", "verified"]))
        .order_by(FileChunk.chunk_index)
    )).scalars().all()

    if sum(c.size for c in chunks) != virtual_file.size:
        raise ValueError("Some parts of this file are missing")

    chunk_downloads = []
    for chunk in chunks:
        if not chunk.provider_file_id or not chunk.storage_account_id:
            raise ValueError(f"Chunk {chunk.chunk_index} has no provider file ID")

        if chunk.storage_account_id not in token_cache:
            account = await db.get(StorageAccount, chunk.storage_account_id)
            if not account or not account.encrypted_refresh_token or account.status in ("disconnected", "deleting"):
                raise ValueError(f"The drive holding part {chunk.chunk_index} of this file is unavailable")
            provider = ProviderFactory.get_provider(account.provider)
            access_token, expires_at = await provider.get_access_token(account.encrypted_refresh_token)
            token_cache[chunk.storage_account_id] = (provider, access_token, expires_at)

        provider, access_token, expires_at = token_cache[chunk.storage_account_id]
        chunk_downloads.append({
            "chunk_id": str(chunk.id),
            "index": chunk.chunk_index,
            "offset": chunk.offset,
            "size": chunk.size,
            "download_url": provider.build_download_url(chunk.provider_file_id),
            "access_token": access_token,  # Short-lived — frontend attaches as Authorization header
            "token_expires_at": expires_at,
            "checksum": chunk.checksum,
        })
    return chunk_downloads


async def prepare_download(
    db: AsyncSession,
    file_id: UUID,
    user_id: UUID,
) -> Tuple[VirtualFile, List[dict]]:
    """
    Prepare a download by generating short-lived download URLs for each chunk.
    Returns the virtual file metadata and an ordered list of chunk download descriptors.
    The frontend fetches each chunk in parallel and streams them to disk in order.

    If Google returns 404 for a chunk, the frontend shows the "rescue" prompt
    (restore from Drive trash) or calls DELETE /files/{id}?permanent=true.
    """
    virtual_file, _ = await require_file(db, file_id, user_id, required="viewer")

    if virtual_file.status != "available":
        raise ConflictError(f"File is not available for download (status: {virtual_file.status})")

    chunk_downloads = await build_chunk_downloads(db, virtual_file)
    return virtual_file, chunk_downloads


# ---------------------------------------------------------------------------
# Update (rename / star / move)
# ---------------------------------------------------------------------------

async def update_file(
    db: AsyncSession,
    file_id: UUID,
    user_id: UUID,
    name: Optional[str] = None,
    starred: Optional[bool] = None,
    folder_id=_UNSET,
) -> VirtualFile:
    """
    - rename: owner, or editor of the containing folder
    - star:   owner only
    - move:   owner, or editor of the containing folder; requires editor on the target.
              `folder_id=None` moves to the owner's root; omit to leave unchanged.
    """
    virtual_file, role = await require_file(db, file_id, user_id, required="editor")

    if name is not None:
        virtual_file.name = name.strip()
    if starred is not None:
        if role != "owner":
            raise ForbiddenError("Only the owner can star this file")
        virtual_file.starred = starred
    if folder_id is not _UNSET:
        if folder_id is None:
            if role != "owner":
                raise ForbiddenError("Only the owner can move this file to their root")
        else:
            target_role = await get_folder_role(db, folder_id, user_id)
            if target_role is None:
                raise NotFoundError("Target folder not found")
            if not role_at_least(target_role, "editor"):
                raise ForbiddenError("You need editor access on the target folder")
        virtual_file.folder_id = folder_id

    db.add(virtual_file)
    await db.commit()
    await db.refresh(virtual_file)
    return virtual_file


async def rename_file(db: AsyncSession, file_id: UUID, user_id: UUID, new_name: str) -> Optional[VirtualFile]:
    """Rename a virtual file (kept for backwards compatibility)."""
    return await update_file(db, file_id, user_id, name=new_name)


# ---------------------------------------------------------------------------
# Trash / restore / delete forever
# ---------------------------------------------------------------------------

async def trash_file(db: AsyncSession, file_id: UUID, user_id: UUID) -> None:
    """Move a file to the trash (owner, or editor of its folder). Recoverable for TRASH_RETENTION_DAYS."""
    from datetime import datetime, timezone
    virtual_file, _ = await require_file(db, file_id, user_id, required="editor")
    if virtual_file.status == "uploading":
        raise ConflictError("Cancel the upload instead of trashing it")
    virtual_file.is_deleted = True
    virtual_file.deleted_at = datetime.now(timezone.utc)
    db.add(virtual_file)
    await db.commit()


async def restore_file(db: AsyncSession, file_id: UUID, user_id: UUID) -> VirtualFile:
    """Restore a trashed file. If its folder is gone or trashed, it is restored to the root."""
    virtual_file = await db.get(VirtualFile, file_id)
    if (
        not virtual_file or virtual_file.user_id != user_id
        or not virtual_file.is_deleted or virtual_file.status == "deleted"
    ):
        raise NotFoundError("File not found in trash")

    if virtual_file.folder_id:
        folder = await db.get(VirtualFolder, virtual_file.folder_id)
        if not folder or folder.is_deleted:
            virtual_file.folder_id = None

    virtual_file.is_deleted = False
    virtual_file.deleted_at = None
    db.add(virtual_file)
    await db.commit()
    await db.refresh(virtual_file)
    return virtual_file


async def purge_file(db: AsyncSession, virtual_file: VirtualFile) -> None:
    """Permanently delete a file (no permission checks — callers must check)."""
    from datetime import datetime, timezone
    await _retire_file_chunks(db, virtual_file.id)
    virtual_file.status = "deleted"
    virtual_file.is_deleted = True
    virtual_file.deleted_at = virtual_file.deleted_at or datetime.now(timezone.utc)
    db.add(virtual_file)
    await db.commit()


async def delete_file_forever(db: AsyncSession, file_id: UUID, user_id: UUID) -> None:
    """
    Permanently delete a file (owner only). Works from the trash or directly — the latter is
    used by the "I can't restore it. Delete this broken file." button in the 404 rescue flow.
    Chunks still on other drives are removed by the cleanup job.
    """
    virtual_file = await db.get(VirtualFile, file_id)
    if not virtual_file or virtual_file.status == "deleted" or virtual_file.user_id != user_id:
        raise NotFoundError("File not found")
    await purge_file(db, virtual_file)


async def delete_file(db: AsyncSession, file_id: UUID, user_id: UUID) -> bool:
    """Backwards-compatible alias: deleting a file moves it to the trash."""
    await trash_file(db, file_id, user_id)
    return True
