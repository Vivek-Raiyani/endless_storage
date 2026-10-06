"""
Files API
=========
Routes for virtual file management: listing, upload initiation,
chunk confirmation, download preparation, renaming, and deletion.
"""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.virtual_file import VirtualFile
from app.core.config import settings
from app.models.user import User
from app.schemas.storage import (
    VirtualFileOut,
    InitiateUploadRequest,
    InitiateUploadResponse,
    ChunkInfo,
    ConfirmChunkRequest,
    DownloadPrepareResponse,
    ChunkDownloadInfo,
    UpdateFileRequest,
    UploadSessionOut,
)
from app.schemas.response import DataResponse, MessageResponse
from app.services import virtual_file_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/recent", response_model=DataResponse[List[VirtualFileOut]])
async def list_recent_files(
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """List 20 most recent files for the user."""
    stmt = select(VirtualFile).where(
        VirtualFile.user_id == current_user.id,
        VirtualFile.status == "available",
        VirtualFile.is_deleted == False
    ).order_by(VirtualFile.created_at.desc()).limit(20)
    files = (await db.execute(stmt)).scalars().all()
    return DataResponse(data=files)

@router.get("/trash", response_model=DataResponse[List[VirtualFileOut]])
async def list_trashed_files(
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """List all soft-deleted files for the user."""
    stmt = select(VirtualFile).where(
        VirtualFile.user_id == current_user.id,
        VirtualFile.is_deleted == True,
        VirtualFile.status != "deleted" # "deleted" means permanently deleted chunks
    ).order_by(VirtualFile.deleted_at.desc())
    files = (await db.execute(stmt)).scalars().all()
    return DataResponse(data=files)

@router.get("/shared", response_model=DataResponse[List[VirtualFileOut]])
async def list_shared_files(
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """List files shared with the user (placeholder for now)."""
    # Endless Storage doesn't support true cross-user sharing yet
    return DataResponse(data=[])

@router.get("/", response_model=DataResponse[List[VirtualFileOut]])
async def list_files(
    folder_id: Optional[UUID] = Query(default=None, description="Folder ID to list files from (None for root)"),
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """List all virtual files in a folder for the current user."""
    files = await virtual_file_service.list_files(db, current_user.id, folder_id)
    return DataResponse(data=files)


@router.post("/upload", response_model=DataResponse[InitiateUploadResponse])
async def initiate_upload(
    body: InitiateUploadRequest,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Step 1 of the upload flow.

    The frontend sends file metadata; the backend runs the placement engine,
    creates Google Drive resumable upload sessions for each chunk, and returns
    the chunk plan with upload URLs. The frontend then PUTs bytes directly to
    Google Drive — no file bytes pass through this server.
    """
    try:
        virtual_file, session, chunk_infos = await virtual_file_service.initiate_upload(
            db=db,
            user_id=current_user.id,
            name=body.name,
            size=body.size,
            mime_type=body.mime_type,
            folder_id=body.folder_id,
            thumbnail=body.thumbnail,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return DataResponse(data=InitiateUploadResponse(
        upload_id=str(session.id),
        file_id=str(virtual_file.id),
        chunk_size=settings.CHUNK_SIZE_BYTES,
        total_chunks=session.total_chunks,
        chunks=[ChunkInfo(**c) for c in chunk_infos],
    ))


@router.post("/{file_id}/chunks/confirm", response_model=MessageResponse)
async def confirm_chunk(
    file_id: UUID,
    body: ConfirmChunkRequest,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Step 2 of the upload flow — called by the frontend after each chunk is
    successfully PUT to Google Drive.
    Reports the Drive file ID and optional checksum back to the backend.
    When all chunks are confirmed, the file status becomes 'available'.
    """
    try:
        chunk = await virtual_file_service.confirm_chunk_uploaded(
            db=db,
            file_id=file_id,
            chunk_index=body.chunk_index,
            user_id=current_user.id,
            provider_file_id=body.provider_file_id,
            checksum=body.checksum,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return MessageResponse(message=f"Chunk {body.chunk_index} confirmed")


@router.get("/{file_id}/upload-status", response_model=DataResponse[UploadSessionOut])
async def get_upload_status(
    file_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Poll the upload session status and chunk completion count."""
    session = await virtual_file_service.get_upload_session(db, file_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Upload session not found")
    return DataResponse(data=session)


@router.get("/{file_id}/download", response_model=DataResponse[DownloadPrepareResponse])
async def prepare_download(
    file_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """
    Prepare a download.

    Returns ordered chunk descriptors with short-lived Google Drive download URLs
    and access tokens. The frontend fetches each chunk in parallel (with controlled
    concurrency), verifies checksums, and streams them to disk in order.
    The full file is never assembled on this server.
    """
    try:
        virtual_file, chunk_downloads = await virtual_file_service.prepare_download(
            db, file_id, current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return DataResponse(data=DownloadPrepareResponse(
        file_id=str(virtual_file.id),
        name=virtual_file.name,
        size=virtual_file.size,
        mime_type=virtual_file.mime_type,
        chunks=[ChunkDownloadInfo(**c) for c in chunk_downloads],
    ))


@router.get("/{file_id}", response_model=DataResponse[VirtualFileOut])
async def get_file(
    file_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Get metadata for a single virtual file."""
    virtual_file = await virtual_file_service.get_file(db, file_id, current_user.id)
    if not virtual_file:
        raise HTTPException(status_code=404, detail="File not found")
    return DataResponse(data=virtual_file)


@router.patch("/{file_id}", response_model=DataResponse[VirtualFileOut])
async def update_file(
    file_id: UUID,
    body: UpdateFileRequest,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Rename, move, or change metadata of a virtual file."""
    update_data = body.model_dump(exclude_unset=True)
    
    kwargs = {}
    if "name" in update_data:
        kwargs["name"] = update_data["name"]
    if "starred" in update_data:
        kwargs["starred"] = update_data["starred"]
    if "folder_id" in update_data:
        kwargs["folder_id"] = update_data["folder_id"]

    virtual_file = await virtual_file_service.update_file(
        db=db,
        file_id=file_id,
        user_id=current_user.id,
        **kwargs
    )
    if not virtual_file:
        raise HTTPException(status_code=404, detail="File not found")
    return DataResponse(data=virtual_file)


@router.delete("/{file_id}", response_model=MessageResponse)
async def delete_file(
    file_id: UUID,
    permanent: bool = Query(False, description="Permanently delete the file"),
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Delete a virtual file and optionally remove all its chunks from Google Drive."""
    if permanent:
        await virtual_file_service.delete_file_forever(db, file_id, current_user.id)
        return MessageResponse(message="File deleted permanently")
    else:
        success = await virtual_file_service.delete_file(db, file_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        return MessageResponse(message="File moved to trash")

@router.post("/{file_id}/restore", response_model=DataResponse[VirtualFileOut])
async def restore_file(
    file_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Restore a virtual file from trash."""
    try:
        virtual_file = await virtual_file_service.restore_file(db, file_id, current_user.id)
        return DataResponse(data=virtual_file)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
