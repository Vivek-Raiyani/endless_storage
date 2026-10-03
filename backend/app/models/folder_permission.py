from sqlalchemy import Column, String, ForeignKey, UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class FolderPermission(Base):
    """
    Many-to-many join table for folder collaboration.
    Allows users to share a folder with specific other users, granting them viewing or editing rights.
    Because of the VirtualFolder hierarchy, granting permission to a parent folder implicitly
    grants permission to all children inside it.
    """
    __tablename__ = "folder_permissions"

    # The folder being shared
    folder_id = Column(
        UUID(as_uuid=True),
        ForeignKey("virtual_folders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The user receiving the permission
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The level of access granted (e.g., "viewer", "editor")
    role = Column(String(32), nullable=False, default="viewer")

    # Relationships
    folder = relationship("VirtualFolder", back_populates="permissions", lazy="select")
    user = relationship("User", foreign_keys=[user_id], lazy="select")
