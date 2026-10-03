from sqlalchemy import Column, String, BigInteger, ForeignKey, UUID, Text
from sqlalchemy.orm import relationship
from app.models.base import Base


class StorageAccount(Base):
    """
    Represents one Google Drive account connected by a user.
    The backend holds the encrypted refresh token; the frontend never sees it.
    All capacity fields are in bytes.
    """
    __tablename__ = "storage_accounts"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # e.g. "google_drive", "onedrive", "dropbox" (extensible)
    provider = Column(String(64), nullable=False, default="google_drive")

    # Provider-level account identifier (e.g. Google sub / email)
    provider_account_id = Column(String(256), nullable=False)
    provider_account_email = Column(String(256), nullable=True)
    display_name = Column(String(256), nullable=True)

    # Encrypted Google refresh token — never returned to the client
    encrypted_refresh_token = Column(Text, nullable=True)

    # Root folder ID in Google Drive where chunks are stored
    root_folder_id = Column(String(256), nullable=True)

    # "active" | "disconnected" | "error" | "quota_exceeded" | "migrating" | "deleting"
    status = Column(String(32), default="active", nullable=False, index=True)
    status_message = Column(String(256), nullable=True)

    # Capacity accounting (bytes). Updated periodically via Drive quota API.
    total_bytes = Column(BigInteger, default=0, nullable=False)
    used_bytes = Column(BigInteger, default=0, nullable=False)
    reserved_bytes = Column(BigInteger, default=0, nullable=False)  # in-flight uploads

    # Platform allocation limits
    allocated_limit_bytes = Column(BigInteger, nullable=True)  # Max bytes the platform can use
    app_used_bytes = Column(BigInteger, default=0, nullable=False)  # Bytes currently used by the platform

    # Relationships
    owner = relationship("User", foreign_keys=[user_id], lazy="select")
    chunks = relationship("FileChunk", foreign_keys="[FileChunk.storage_account_id]", back_populates="storage_account", lazy="select")

    @property
    def available_bytes(self) -> int:
        # Physical free space on the drive
        physical_free = max(0, self.total_bytes - self.used_bytes - self.reserved_bytes)
        
        # If no limit is set, they can use all physical free space
        if self.allocated_limit_bytes is None:
            return physical_free
            
        # Logical free space based on allocation limit
        logical_free = max(0, self.allocated_limit_bytes - self.app_used_bytes - self.reserved_bytes)
        
        # We can only use the smaller of the two (can't exceed limit, can't exceed physical space)
        return min(physical_free, logical_free)
