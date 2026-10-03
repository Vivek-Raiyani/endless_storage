from sqlalchemy import Column, String, ForeignKey, UUID, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base, SoftDeleteMixin


class VirtualFolder(SoftDeleteMixin, Base):
    """
    Represents a folder in the user's virtual file system.
    This replaces path-based strings and uses the Adjacency List pattern
    for infinite nesting and instant renames.
    """
    __tablename__ = "virtual_folders"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("virtual_folders.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    name = Column(String(256), nullable=False)
    
    # Metadata enhancements
    color = Column(String(32), nullable=True)  # e.g., "#FF5733"
    starred = Column(Boolean, default=False, nullable=False)
    shared = Column(Boolean, default=False, nullable=False)

    # Relationships
    owner = relationship("User", foreign_keys=[user_id], lazy="select")
    
    # Self-referential relationship for parent-child folder hierarchy
    children = relationship(
        "VirtualFolder",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    parent = relationship(
        "VirtualFolder",
        back_populates="children",
        remote_side="[VirtualFolder.id]"
    )
    
    
    # Files contained within this folder
    files = relationship("VirtualFile", back_populates="folder", cascade="all, delete")

    # Collaboration permissions
    permissions = relationship("FolderPermission", back_populates="folder", cascade="all, delete-orphan")
