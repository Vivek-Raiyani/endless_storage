import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.user import User
from app.models.virtual_folder import VirtualFolder
from app.models.folder_permission import FolderPermission
from app.models.virtual_file import VirtualFile, FileChunk

logger = logging.getLogger(__name__)


async def create_folder(
    db: AsyncSession,
    user_id: UUID,
    name: str,
    parent_id: Optional[UUID] = None,
    color: Optional[str] = None,
) -> VirtualFolder:
    """Create a new virtual folder."""
    folder = VirtualFolder(
        user_id=user_id,
        name=name,
        parent_id=parent_id,
        color=color,
    )
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder


async def list_folders(
    db: AsyncSession,
    user_id: UUID,
    parent_id: Optional[UUID] = None,
) -> List[VirtualFolder]:
    """List all folders in the specified parent folder."""
    if parent_id:
        has_access = await has_folder_access(db, parent_id, user_id)
        if not has_access:
            return []
            
        result = await db.execute(
            select(VirtualFolder)
            .where(VirtualFolder.parent_id == parent_id, VirtualFolder.is_deleted == False)
            .order_by(VirtualFolder.name)
        )
        return result.scalars().all()
    else:
        # Root folder - only own folders
        result = await db.execute(
            select(VirtualFolder)
            .where(
                VirtualFolder.user_id == user_id,
                VirtualFolder.parent_id == None,
                VirtualFolder.is_deleted == False
            )
            .order_by(VirtualFolder.name)
        )
        return result.scalars().all()


async def get_folder(
    db: AsyncSession,
    folder_id: UUID,
    user_id: UUID,
) -> Optional[VirtualFolder]:
    """Get a specific folder."""
    result = await db.execute(
        select(VirtualFolder)
        .where(
            VirtualFolder.id == folder_id,
            VirtualFolder.user_id == user_id,
            VirtualFolder.is_deleted == False
        )
    )
    return result.scalars().first()


async def update_folder(
    db: AsyncSession,
    folder_id: UUID,
    user_id: UUID,
    name: Optional[str] = None,
    parent_id: Optional[UUID] = None,
    color: Optional[str] = None,
    starred: Optional[bool] = None,
) -> Optional[VirtualFolder]:
    """Update metadata or move a folder."""
    folder = await get_folder(db, folder_id, user_id)
    if not folder:
        return None

    if name is not None:
        folder.name = name
    # Moving the folder changes the parent_id
    # Note: To safely move to root, parent_id must be explicitly handled. 
    # Usually an API passes a specific flag or "null" string to move to root, 
    # here we assume if it's passed it's an intended update.
    if parent_id is not None:
        folder.parent_id = parent_id
    if color is not None:
        folder.color = color
    if starred is not None:
        folder.starred = starred

    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder


async def delete_folder(
    db: AsyncSession,
    folder_id: UUID,
    user_id: UUID,
) -> bool:
    """
    Soft-delete a folder and all its contents.
    Marks files as deleted and their chunks as pending_deletion for the cleanup job.
    """
    folder = await get_folder(db, folder_id, user_id)
    if not folder:
        return False
        
    folders_to_delete = [folder_id]
    
    current_ids = [folder_id]
    while current_ids:
        result = await db.execute(select(VirtualFolder.id).where(VirtualFolder.parent_id.in_(current_ids)))
        child_ids = result.scalars().all()
        if not child_ids:
            break
        folders_to_delete.extend(child_ids)
        current_ids = child_ids
        
    result = await db.execute(select(VirtualFile.id).where(VirtualFile.folder_id.in_(folders_to_delete)))
    file_ids = result.scalars().all()
    
    now = datetime.now(timezone.utc)
    
    if file_ids:
        await db.execute(
            update(FileChunk)
            .where(FileChunk.file_id.in_(file_ids))
            .values(status="pending_deletion")
        )
        
        await db.execute(
            update(VirtualFile)
            .where(VirtualFile.id.in_(file_ids))
            .values(is_deleted=True, deleted_at=now, status="deleted")
        )
        
    await db.execute(
        update(VirtualFolder)
        .where(VirtualFolder.id.in_(folders_to_delete))
        .values(is_deleted=True, deleted_at=now)
    )

    await db.commit()
    return True


async def share_folder(
    db: AsyncSession,
    folder_id: UUID,
    owner_id: UUID,
    target_email: str,
    role: str = "viewer"
) -> bool:
    """Share a folder with another user by email."""
    # Ensure owner actually owns the folder
    folder = await get_folder(db, folder_id, owner_id)
    if not folder:
        raise ValueError("Folder not found or permission denied.")

    # Find the target user
    result = await db.execute(select(User).where(User.email == target_email))
    target_user = result.scalars().first()
    if not target_user:
        raise ValueError("User with that email does not exist.")

    if target_user.id == owner_id:
        raise ValueError("You cannot share a folder with yourself.")

    # Create the permission record
    perm = FolderPermission(
        folder_id=folder_id,
        user_id=target_user.id,
        role=role
    )
    db.add(perm)
    
    # Update the folder's basic shared boolean for quick UI reference
    folder.shared = True
    db.add(folder)
    
    await db.commit()
    return True


async def get_shared_folders(db: AsyncSession, user_id: UUID) -> List[VirtualFolder]:
    """Get all folders that have been shared with this user."""
    result = await db.execute(
        select(VirtualFolder)
        .join(FolderPermission, FolderPermission.folder_id == VirtualFolder.id)
        .where(
            FolderPermission.user_id == user_id,
            VirtualFolder.is_deleted == False
        )
        .order_by(VirtualFolder.name)
    )
    return result.scalars().all()


async def unshare_folder(
    db: AsyncSession,
    folder_id: UUID,
    owner_id: UUID,
    target_email: str,
) -> bool:
    """Revoke a user's access to a shared folder."""
    # Ensure owner actually owns the folder
    folder = await get_folder(db, folder_id, owner_id)
    if not folder:
        raise ValueError("Folder not found or permission denied.")

    # Find the target user
    result = await db.execute(select(User).where(User.email == target_email))
    target_user = result.scalars().first()
    if not target_user:
        raise ValueError("User with that email does not exist.")

    # Find and delete the permission record
    perm_result = await db.execute(
        select(FolderPermission).where(
            FolderPermission.folder_id == folder_id,
            FolderPermission.user_id == target_user.id
        )
    )
    perm = perm_result.scalars().first()
    if perm:
        await db.delete(perm)
        await db.commit()
        
        # Check if there are any other permissions left to update the 'shared' boolean
        remaining_perms = await db.execute(
            select(FolderPermission).where(FolderPermission.folder_id == folder_id)
        )
        if not remaining_perms.scalars().first():
            folder.shared = False
            db.add(folder)
            await db.commit()
            
    return True


async def has_folder_access(db: AsyncSession, folder_id: UUID, user_id: UUID) -> bool:
    """
    Recursively walk up the folder tree to see if the user owns the folder
    or has a FolderPermission for it or any of its parents.
    """
    current_folder_id = folder_id
    while current_folder_id:
        result = await db.execute(
            select(VirtualFolder).where(
                VirtualFolder.id == current_folder_id,
                VirtualFolder.is_deleted == False
            )
        )
        folder = result.scalars().first()
        if not folder:
            return False
            
        if folder.user_id == user_id:
            return True
            
        # check permission table
        perm = await db.execute(
            select(FolderPermission).where(
                FolderPermission.folder_id == current_folder_id,
                FolderPermission.user_id == user_id
            )
        )
        if perm.scalars().first():
            return True
            
        # Move up the tree
        current_folder_id = folder.parent_id
        
    return False


async def prepare_folder_download(
    db: AsyncSession,
    folder_id: UUID,
    user_id: UUID,
) -> dict:
    """
    Prepare a recursive download for a folder.
    Returns the folder metadata and a list of all files with their relative paths
    and chunk download URLs.
    """
    folder = await get_folder(db, folder_id, user_id)
    if not folder:
        raise ValueError("Folder not found")

    folder_paths = {folder_id: ""}
    current_ids = [folder_id]
    
    while current_ids:
        result = await db.execute(
            select(VirtualFolder)
            .where(
                VirtualFolder.parent_id.in_(current_ids),
                VirtualFolder.is_deleted == False
            )
        )
        children = result.scalars().all()
        child_ids = []
        for child in children:
            parent_path = folder_paths[child.parent_id]
            child_path = f"{parent_path}{child.name}/" if parent_path else f"{child.name}/"
            folder_paths[child.id] = child_path
            child_ids.append(child.id)
        current_ids = child_ids

    all_folder_ids = list(folder_paths.keys())
    
    result = await db.execute(
        select(VirtualFile.id)
        .where(
            VirtualFile.folder_id.in_(all_folder_ids),
            VirtualFile.is_deleted == False,
            VirtualFile.status == "available"
        )
    )
    file_ids = result.scalars().all()
    
    from app.services.virtual_file_service import prepare_download
    
    files = []
    total_size = 0
    for fid in file_ids:
        v_file, chunk_downloads = await prepare_download(db, fid, user_id)
        rel_path = folder_paths[v_file.folder_id] + v_file.name
        total_size += v_file.size
        files.append({
            "file_id": str(v_file.id),
            "name": v_file.name,
            "size": v_file.size,
            "mime_type": v_file.mime_type,
            "relative_path": rel_path,
            "chunks": chunk_downloads,
        })
        
    return {
        "folder_id": str(folder.id),
        "folder_name": folder.name,
        "total_size": total_size,
        "files": files,
    }
