from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class StorageAccountOut(BaseModel):
    id: UUID
    provider: str
    provider_account_email: Optional[str]
    display_name: Optional[str]
    status: str
    status_message: Optional[str] = None
    total_bytes: int
    used_bytes: int
    reserved_bytes: int
    available_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_computed(cls, account):
        data = {
            "id": account.id,
            "provider": account.provider,
            "provider_account_email": account.provider_account_email,
            "display_name": account.display_name,
            "status": account.status,
            "status_message": account.status_message,
            "total_bytes": account.total_bytes,
            "used_bytes": account.used_bytes,
            "reserved_bytes": account.reserved_bytes,
            "available_bytes": account.available_bytes,
            "created_at": account.created_at,
        }
        return cls(**data)


class ChunkInfo(BaseModel):
    chunk_id: str
    index: int
    offset: int
    size: int
    upload_url: str
    storage_account_id: str


class InitiateUploadRequest(BaseModel):
    name: str
    size: int
    mime_type: Optional[str] = "application/octet-stream"
    folder_id: Optional[UUID] = None


class InitiateUploadResponse(BaseModel):
    upload_id: str       # upload session ID
    file_id: str
    chunk_size: int      # the fixed chunk size configured on the server
    total_chunks: int
    chunks: list[ChunkInfo]


class ConfirmChunkRequest(BaseModel):
    chunk_index: int
    provider_file_id: str
    checksum: Optional[str] = None


class ChunkDownloadInfo(BaseModel):
    chunk_id: str
    index: int
    offset: int
    size: int
    download_url: str
    access_token: str
    checksum: Optional[str]


class VirtualFileOut(BaseModel):
    id: UUID
    name: str
    mime_type: Optional[str]
    size: int
    status: str
    folder_id: Optional[UUID] = None
    starred: bool
    content_hash: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DownloadPrepareResponse(BaseModel):
    file_id: str
    name: str
    size: int
    mime_type: Optional[str]
    chunks: list[ChunkDownloadInfo]


class RenameFileRequest(BaseModel):
    name: str


class UploadSessionOut(BaseModel):
    id: UUID
    file_id: UUID
    total_chunks: int
    completed_chunks: int
    status: str

    model_config = {"from_attributes": True}


class VirtualFolderOut(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID]
    color: Optional[str]
    starred: bool
    shared: bool
    
    model_config = {"from_attributes": True}

class CreateFolderRequest(BaseModel):
    name: str
    parent_id: Optional[UUID] = None
    color: Optional[str] = None

class UpdateFolderRequest(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None
    color: Optional[str] = None
    starred: Optional[bool] = None

class ShareFolderRequest(BaseModel):
    target_user_email: str
    role: str = "viewer"


class FileDownloadItem(BaseModel):
    file_id: str
    name: str
    size: int
    mime_type: Optional[str]
    relative_path: str
    chunks: List[ChunkDownloadInfo]


class FolderDownloadPrepareResponse(BaseModel):
    folder_id: str
    folder_name: str
    total_size: int
    files: List[FileDownloadItem]


class DisconnectPreviewResponse(BaseModel):
    can_migrate: bool
    affected_files_count: int
    total_bytes_to_move: int
    available_bytes_elsewhere: int


class DisconnectRequest(BaseModel):
    action: str  # "migrate" or "delete"
