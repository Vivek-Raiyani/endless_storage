from sqlalchemy import Column, String, BigInteger, ForeignKey, UUID, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base, SoftDeleteMixin


class VirtualFile(SoftDeleteMixin, Base):
    """
    A virtual file that may be physically split across multiple storage accounts.
    This is the user-facing file abstraction.
    """
    __tablename__ = "virtual_files"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Original filename and MIME type
    name = Column(String(512), nullable=False)
    mime_type = Column(String(128), nullable=True)

    # Total size in bytes of the original file
    size = Column(BigInteger, nullable=False, default=0)

    # SHA-256 hash of the full file for integrity verification
    content_hash = Column(String(64), nullable=True)

    # "pending" | "uploading" | "available" | "error" | "deleted"
    status = Column(String(32), default="pending", nullable=False, index=True)

    # Optional: parent folder ID (None = root)
    folder_id = Column(
        UUID(as_uuid=True),
        ForeignKey("virtual_folders.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Metadata enhancements
    starred = Column(Boolean, default=False, nullable=False)
    # Relationships
    owner = relationship("User", foreign_keys=[user_id], lazy="select")
    folder = relationship("VirtualFolder", back_populates="files", lazy="select")
    chunks = relationship("FileChunk", back_populates="virtual_file", lazy="select", order_by="FileChunk.chunk_index")
    upload_session = relationship("UploadSession", back_populates="virtual_file", uselist=False, lazy="select")


class FileChunk(Base):
    """
    One fixed-size physical chunk of a VirtualFile, stored on a specific StorageAccount.
    The placement engine decides which account each chunk goes to.
    """
    __tablename__ = "file_chunks"

    file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("virtual_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    storage_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("storage_accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # The account this chunk is migrating to (if any)
    target_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("storage_accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Position in the logical file (0-indexed)
    chunk_index = Column(BigInteger, nullable=False)

    # Byte offset within the original file
    offset = Column(BigInteger, nullable=False)

    # Actual size of this chunk (last chunk may be smaller)
    size = Column(BigInteger, nullable=False)

    # Google Drive file ID for this chunk object
    provider_file_id = Column(String(256), nullable=True)

    # Google Drive resumable upload session URI (valid for ~1 week)
    upload_session_uri = Column(Text, nullable=True)

    # SHA-256 of the chunk bytes for corruption detection
    checksum = Column(String(64), nullable=True)

    # "pending" | "uploading" | "complete" | "verified" | "error"
    status = Column(String(32), default="pending", nullable=False, index=True)

    # Relationships
    virtual_file = relationship("VirtualFile", back_populates="chunks")
    storage_account = relationship("StorageAccount", foreign_keys=[storage_account_id], back_populates="chunks")


class UploadSession(Base):
    """
    Tracks the lifecycle of a multi-chunk upload initiated by the frontend.
    The frontend polls this to know which chunks are done and which need retry.
    """
    __tablename__ = "upload_sessions"

    file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("virtual_files.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Total number of chunks expected
    total_chunks = Column(BigInteger, nullable=False)

    # Number of chunks that have been confirmed complete + verified
    completed_chunks = Column(BigInteger, default=0, nullable=False)

    # "created" | "uploading" | "completed" | "verified" | "failed"
    status = Column(String(32), default="created", nullable=False, index=True)

    # Relationships
    virtual_file = relationship("VirtualFile", back_populates="upload_session")
    user = relationship("User", foreign_keys=[user_id], lazy="select")
