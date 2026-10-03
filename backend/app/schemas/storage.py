from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Storage accounts
# ---------------------------------------------------------------------------

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
    # Platform allocation (the slice of the drive Endless Storage is allowed to use)
    allocated_limit_bytes: Optional[int] = None
    app_used_bytes: int = 0
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
            "allocated_limit_bytes": account.allocated_limit_bytes,
            "app_used_bytes": account.app_used_bytes or 0,
            "created_at": account.created_at,
        }
        return cls(**data)


class StorageSummaryOut(BaseModel):
    """Aggregated "endless" pool — powers the Drive-style storage meter in the sidebar."""
    accounts_count: int
    active_accounts_count: int
    total_bytes: int          # sum of allocated limits (or physical totals when no limit)
    used_bytes: int           # bytes used by Endless Storage files
    available_bytes: int      # what new uploads can actually use right now
    trash_bytes: int          # bytes held by items in the trash


class DisconnectPreviewResponse(BaseModel):
    can_migrate: bool
    affected_files_count: int
    total_bytes_to_move: int
    available_bytes_elsewhere: int


class DisconnectRequest(BaseModel):
    action: Literal["migrate", "delete"]


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

class ChunkInfo(BaseModel):
    chunk_id: str
    index: int
    offset: int
    size: int
    upload_url: str
    storage_account_id: str


class InitiateUploadRequest(BaseModel):
    name: str = Field(min_length=1, max_length=512)
    size: int = Field(gt=0)
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


class UploadSessionOut(BaseModel):
    id: UUID
    file_id: UUID
    total_chunks: int
    completed_chunks: int
    status: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

class ChunkDownloadInfo(BaseModel):
    chunk_id: str
    index: int
    offset: int
    size: int
    download_url: str
    access_token: str
    # When access_token expires. For long downloads (e.g. 50GB folder zips) the frontend
    # must re-call GET /files/{id}/download for fresh tokens once this passes.
    token_expires_at: Optional[datetime] = None
    checksum: Optional[str]


class DownloadPrepareResponse(BaseModel):
    file_id: str
    name: str
    size: int
    mime_type: Optional[str]
    chunks: list[ChunkDownloadInfo]


class FileDownloadItem(BaseModel):
    file_id: str
    name: str
    size: int
    mime_type: Optional[str]
    relative_path: str
    chunks: List[ChunkDownloadInfo]


class UnavailableFileItem(BaseModel):
    """A file inside the folder that cannot be downloaded right now (e.g. its drive is disconnected)."""
    file_id: str
    relative_path: str
    reason: str


class FolderDownloadPrepareResponse(BaseModel):
    folder_id: str
    folder_name: str
    total_size: int
    # Relative paths of every sub-folder (so empty folders are preserved in the ZIP)
    folders: List[str] = []
    files: List[FileDownloadItem]
    # Files skipped because they can't be downloaded — the zip still succeeds without them
    unavailable_files: List[UnavailableFileItem] = []


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------

class VirtualFileOut(BaseModel):
    id: UUID
    name: str
    mime_type: Optional[str]
    size: int
    status: str
    folder_id: Optional[UUID] = None
    owner_id: UUID = Field(validation_alias="user_id")
    starred: bool
    content_hash: Optional[str]
    is_deleted: bool = False          # True = in trash
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class UpdateFileRequest(BaseModel):
    """
    PATCH /files/{id}. Only fields that are sent are applied.
    To move a file to the root, send `"folder_id": null` explicitly.
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=512)
    starred: Optional[bool] = None
    folder_id: Optional[UUID] = None


# Kept for backwards compatibility with older clients
RenameFileRequest = UpdateFileRequest


# ---------------------------------------------------------------------------
# Folders
# ---------------------------------------------------------------------------

class VirtualFolderOut(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID]
    owner_id: UUID = Field(validation_alias="user_id")
    color: Optional[str]
    starred: bool
    shared: bool
    is_deleted: bool = False          # True = in trash
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class BreadcrumbItem(BaseModel):
    id: UUID
    name: str


class CreateFolderRequest(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    parent_id: Optional[UUID] = None
    color: Optional[str] = None


class UpdateFolderRequest(BaseModel):
    """
    PATCH /folders/{id}. Only fields that are sent are applied.
    To move a folder to the root, send `"parent_id": null` explicitly.
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=256)
    parent_id: Optional[UUID] = None
    color: Optional[str] = None
    starred: Optional[bool] = None


class ShareFolderRequest(BaseModel):
    target_user_email: str
    role: Literal["viewer", "editor"] = "viewer"


class FolderPermissionOut(BaseModel):
    user_id: UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str


# ---------------------------------------------------------------------------
# Drive-style views (search / recent / starred / trash)
# ---------------------------------------------------------------------------

class DriveItemsOut(BaseModel):
    folders: List[VirtualFolderOut]
    files: List[VirtualFileOut]
