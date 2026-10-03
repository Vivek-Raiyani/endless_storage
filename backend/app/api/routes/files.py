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

from app.api import deps
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
    RenameFileRequest,
    UploadSessionOut,
)
from app.schemas.response import DataResponse, MessageResponse
from app.services import virtual_file_service

logger = logging.getLogger(__name__)

router = APIRouter()


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
async def rename_file(
    file_id: UUID,
    body: RenameFileRequest,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Rename a virtual file."""
    virtual_file = await virtual_file_service.rename_file(db, file_id, current_user.id, body.name)
    if not virtual_file:
        raise HTTPException(status_code=404, detail="File not found")
    return DataResponse(data=virtual_file)


@router.delete("/{file_id}", response_model=MessageResponse)
async def delete_file(
    file_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    """Delete a virtual file and remove all its chunks from Google Drive."""
    success = await virtual_file_service.delete_file(db, file_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return MessageResponse(message="File deleted successfully")
