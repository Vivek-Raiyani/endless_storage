from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base
import uuid


class Asset(Base):
    __tablename__ = "assets"

    # Who owns this asset
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Logical grouping (e.g. "assets/profile", "assets/documents")
    folder = Column(String, nullable=False, default="assets/common")

    # Original filename as uploaded
    filename = Column(String, nullable=False)

    # The storage key / relative path used to identify the object in storage
    # e.g.  "users/<uuid>/assets/profile/avatar.png"
    storage_key = Column(String, nullable=False)

    # Persisted public/presigned URL (refreshed on read for cloud)
    file_url = Column(String, nullable=False)

    # Optional metadata
    content_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
