"""
Virtual Folder Service
======================
Folder hierarchy, sharing, trash and folder-download preparation.

Access model
------------
Every folder has an owner. Sharing a folder grants a role ("viewer" | "editor") on that
folder **and all of its descendants**. `get_folder_role()` resolves the effective role:

    owner  > editor > viewer > None

Trash model (mirrors Google Drive)
----------------------------------
* Trash        -> `is_deleted=True`, `deleted_at=<ts>` on the folder AND every descendant
                  folder/file that wasn't already trashed (same timestamp = same trash op).
* Restore      -> clears `is_deleted` on every item that shares that `deleted_at` timestamp.
* Delete forever -> files become `status="deleted"`, their chunks `pending_deletion`
                  (removed from Google Drive by the cleanup job); folder rows are removed.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.models.user import User
from app.models.virtual_folder import VirtualFolder
from app.models.folder_permission import FolderPermission
from app.models.virtual_file import VirtualFile, FileChunk
from app.services.errors import NotFoundError, ForbiddenError, ConflictError

logger = logging.getLogger(__name__)

ROLE_RANK = {"viewer": 1, "editor": 2, "owner": 3}
_UNSET = object()


def role_at_least(role: Optional[str], required: str) -> bool:
    return role is not None and ROLE_RANK.get(role, 0) >= ROLE_RANK[required]


# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------

async def get_folder_role(db: AsyncSession, folder_id: UUID, user_id: UUID) -> Optional[str]:
    """
    Walk up the tree and return the user's effective role on a (non-trashed) folder:
    "owner" | "editor" | "viewer" | None. The highest role found on the path wins.
    """
    best: Optional[str] = None
    current_id: Optional[UUID] = folder_id
    visited: Set[UUID] = set()
    while current_id and current_id not in visited:
        visited.add(current_id)
        folder = await db.get(VirtualFolder, current_id)
        if not folder or folder.is_deleted:
            return None
        if folder.user_id == user_id:
            return "owner"
        perm = (await db.execute(
            select(FolderPermission.role).where(
                FolderPermission.folder_id == current_id,
                FolderPermission.user_id == user_id,
            )
        )).scalars().first()
        if perm and ROLE_RANK.get(perm, 0) > ROLE_RANK.get(best, 0):
            best = perm
        current_id = folder.parent_id
    return best


async def has_folder_access(db: AsyncSession, folder_id: UUID, user_id: UUID) -> bool:
    """Backwards-compatible helper: True if the user can at least view the folder."""
    return (await get_folder_role(db, folder_id, user_id)) is not None


async def require_folder(
    db: AsyncSession, folder_id: UUID, user_id: UUID, required: str = "viewer"
) -> tuple[VirtualFolder, str]:
    """Load a non-trashed folder and assert the user has at least `required` role."""
    role = await get_folder_role(db, folder_id, user_id)
    if role is None:
        raise NotFoundError("Folder not found")
    if not role_at_least(role, required):
        raise ForbiddenError(f"You need {required} access to do this")
    folder = await db.get(VirtualFolder, folder_id)
    return folder, role


async def _descendant_folder_ids(db: AsyncSession, root_id: UUID, include_trashed: bool = True) -> List[UUID]:
    """Return root_id plus all descendant folder IDs (breadth-first)."""
    ids = [root_id]
    frontier = [root_id]
    while frontier:
        stmt = select(VirtualFolder.id).where(VirtualFolder.parent_id.in_(frontier))
        if not include_trashed:
            stmt = stmt.where(VirtualFolder.is_deleted == False)
        children = (await db.execute(stmt)).scalars().all()
        ids.extend(children)
        frontier = list(children)
    return ids


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

async def create_folder(
    db: AsyncSession,
    user_id: UUID,
    name: str,
    parent_id: Optional[UUID] = None,
    color: Optional[str] = None,
) -> VirtualFolder:
    """
    Create a new virtual folder. Creating inside a shared folder requires editor access;
    the new folder is owned by the parent folder's owner so it stays inside their tree.
    """
    owner_id = user_id
    if parent_id:
        parent, _ = await require_folder(db, parent_id, user_id, required="editor")
        owner_id = parent.user_id

    folder = VirtualFolder(
        user_id=owner_id,
        name=name.strip(),
        parent_id=parent_id,
        color=color,
    )
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder


async def search_folders(db: AsyncSession, user_id: UUID, query: str) -> List[VirtualFolder]:
    if not query.strip():
        return []
    q = f"%{query}%"
    result = await db.execute(
        select(VirtualFolder)
        .where(
            VirtualFolder.user_id == user_id,
            VirtualFolder.is_deleted == False,
            VirtualFolder.name.ilike(q)
        )
        .order_by(VirtualFolder.name)
        .limit(50)
    )
    return list(result.scalars().all())


async def list_folders(
    db: AsyncSession,
    user_id: UUID,
    parent_id: Optional[UUID] = None,
    sort_by: str = "name",
    order: str = "asc",
) -> List[VirtualFolder]:
    """List non-trashed folders in a parent (root = the user's own top-level folders)."""
    if parent_id:
        if not await has_folder_access(db, parent_id, user_id):
            raise NotFoundError("Folder not found")
        stmt = select(VirtualFolder).where(
            VirtualFolder.parent_id == parent_id, VirtualFolder.is_deleted == False
        )
    else:
        stmt = select(VirtualFolder).where(
            VirtualFolder.user_id == user_id,
            VirtualFolder.parent_id == None,
            VirtualFolder.is_deleted == False,
        )
    column = {
        "name": VirtualFolder.name,
        "created_at": VirtualFolder.created_at,
        "updated_at": VirtualFolder.updated_at,
    }.get(sort_by, VirtualFolder.name)
    stmt = stmt.order_by(column.desc() if order == "desc" else column.asc())
    return (await db.execute(stmt)).scalars().all()


async def get_folder(
    db: AsyncSession,
    folder_id: UUID,
    user_id: UUID,
) -> Optional[VirtualFolder]:
    """Get a folder the user can view (owner or shared). Returns None if not accessible."""
    if not await has_folder_access(db, folder_id, user_id):
        return None
    return await db.get(VirtualFolder, folder_id)


async def get_folder_path(db: AsyncSession, folder_id: UUID, user_id: UUID) -> List[VirtualFolder]:
    """
    Breadcrumbs from the top-most folder the user can see down to `folder_id`.
    For owners this starts at their root; for sharees it starts at the shared folder.
    """
    if not await has_folder_access(db, folder_id, user_id):
        raise NotFoundError("Folder not found")

    chain: List[VirtualFolder] = []
    current_id: Optional[UUID] = folder_id
    while current_id:
        folder = await db.get(VirtualFolder, current_id)
        if not folder or folder.is_deleted:
            break
        if folder.user_id != user_id and not await has_folder_access(db, folder.id, user_id):
            break
        chain.append(folder)
        # Stop at the shared root for sharees (don't leak the owner's parent folders)
        if folder.user_id != user_id:
            direct = (await db.execute(
                select(FolderPermission.id).where(
                    FolderPermission.folder_id == folder.id, FolderPermission.user_id == user_id
                )
            )).scalars().first()
            if direct:
                break
        current_id = folder.parent_id
    return list(reversed(chain))


async def _is_descendant(db: AsyncSession, candidate_id: UUID, ancestor_id: UUID) -> bool:
    """True if candidate_id == ancestor_id or lies beneath it."""
    current_id: Optional[UUID] = candidate_id
    visited: Set[UUID] = set()
    while current_id and current_id not in visited:
        if current_id == ancestor_id:
            return True
        visited.add(current_id)
        folder = await db.get(VirtualFolder, current_id)
        current_id = folder.parent_id if folder else None
    return False


async def update_folder(
    db: AsyncSession,
    folder_id: UUID,
    user_id: UUID,
    name: Optional[str] = None,
    parent_id=_UNSET,
    color: Optional[str] = None,
    starred: Optional[bool] = None,
) -> VirtualFolder:
    """
    Rename / recolor / star / move a folder.
    - rename, recolor: editor or owner
    - star, move: owner only (moving changes who can see it)
    - `parent_id=None` moves to the root; omit (`_UNSET`) to leave it unchanged.
    """
    folder, role = await require_folder(db, folder_id, user_id, required="editor")

    if name is not None:
        folder.name = name.strip()
    if color is not None:
        folder.color = color
    if starred is not None:
        if role != "owner":
            raise ForbiddenError("Only the owner can star this folder")
        folder.starred = starred

    if parent_id is not _UNSET:
        if role != "owner":
            raise ForbiddenError("Only the owner can move this folder")
        if parent_id is not None:
            target, _ = await require_folder(db, parent_id, user_id, required="owner")
            if await _is_descendant(db, parent_id, folder_id):
                raise ConflictError("Cannot move a folder into itself or one of its sub-folders")
        folder.parent_id = parent_id

    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder


# ---------------------------------------------------------------------------
# Trash / restore / delete forever
# ---------------------------------------------------------------------------

async def trash_folder(db: AsyncSession, folder_id: UUID, user_id: UUID) -> None:
    """Move a folder (and everything inside it) to the trash. Owner only."""
    folder, _ = await require_folder(db, folder_id, user_id, required="owner")

    now = datetime.now(timezone.utc)
    folder_ids = await _descendant_folder_ids(db, folder_id, include_trashed=False)

    await db.execute(
        update(VirtualFolder)
        .where(VirtualFolder.id.in_(folder_ids), VirtualFolder.is_deleted == False)
        .values(is_deleted=True, deleted_at=now)
    )
    await db.execute(
        update(VirtualFile)
        .where(
            VirtualFile.folder_id.in_(folder_ids),
            VirtualFile.is_deleted == False,
            VirtualFile.status != "deleted",
        )
        .values(is_deleted=True, deleted_at=now)
    )
    await db.commit()


async def _get_owned_trashed_folder(db: AsyncSession, folder_id: UUID, user_id: UUID) -> VirtualFolder:
    folder = await db.get(VirtualFolder, folder_id)
    if not folder or folder.user_id != user_id or not folder.is_deleted:
        raise NotFoundError("Folder not found in trash")
    return folder


async def restore_folder(db: AsyncSession, folder_id: UUID, user_id: UUID) -> VirtualFolder:
    """
    Restore a trashed folder and everything that was trashed together with it.
    If the original parent is gone/trashed, the folder is restored to the root (like Drive).
    """
    folder = await _get_owned_trashed_folder(db, folder_id, user_id)
    trashed_at = folder.deleted_at

    folder_ids = await _descendant_folder_ids(db, folder_id, include_trashed=True)

    # Only restore items that were trashed in the same operation
    await db.execute(
        update(VirtualFolder)
        .where(VirtualFolder.id.in_(folder_ids), VirtualFolder.deleted_at == trashed_at)
        .values(is_deleted=False, deleted_at=None)
    )
    await db.execute(
        update(VirtualFile)
        .where(
            VirtualFile.folder_id.in_(folder_ids),
            VirtualFile.deleted_at == trashed_at,
            VirtualFile.status != "deleted",
        )
        .values(is_deleted=False, deleted_at=None)
    )

    if folder.parent_id:
        parent = await db.get(VirtualFolder, folder.parent_id)
        if not parent or parent.is_deleted:
            folder.parent_id = None
            db.add(folder)

    await db.commit()
    await db.refresh(folder)
    return folder


async def purge_folder_tree(db: AsyncSession, folder_id: UUID) -> int:
    """
    Permanently delete a folder tree (no permission checks — callers must check).
    Files are marked deleted and their chunks queued for removal from Google Drive.
    Returns the number of files purged.
    """
    folder_ids = await _descendant_folder_ids(db, folder_id, include_trashed=True)
    file_ids = (await db.execute(
        select(VirtualFile.id).where(VirtualFile.folder_id.in_(folder_ids))
    )).scalars().all()

    now = datetime.now(timezone.utc)
    if file_ids:
        await db.execute(
            update(FileChunk)
            .where(FileChunk.file_id.in_(file_ids), FileChunk.status != "deleted")
            .values(status="pending_deletion")
        )
        # Detach from folders so removing folder rows can't cascade-delete chunk records
        # before the cleanup job has removed them from Google Drive.
        await db.execute(
            update(VirtualFile)
            .where(VirtualFile.id.in_(file_ids))
            .values(status="deleted", is_deleted=True, deleted_at=now, folder_id=None)
        )

    await db.execute(delete(FolderPermission).where(FolderPermission.folder_id.in_(folder_ids)))
    await db.execute(delete(VirtualFolder).where(VirtualFolder.id.in_(folder_ids)))
    await db.commit()
    return len(file_ids)


async def delete_folder_forever(db: AsyncSession, folder_id: UUID, user_id: UUID) -> None:
    """Permanently delete a trashed folder. Owner only; folder must be in the trash."""
    await _get_owned_trashed_folder(db, folder_id, user_id)
    await purge_folder_tree(db, folder_id)


async def delete_folder(db: AsyncSession, folder_id: UUID, user_id: UUID) -> bool:
    """Backwards-compatible alias: deleting a folder moves it to the trash."""
    await trash_folder(db, folder_id, user_id)
    return True


# ---------------------------------------------------------------------------
# Sharing
# ---------------------------------------------------------------------------

async def share_folder(
    db: AsyncSession,
    folder_id: UUID,
    owner_id: UUID,
    target_email: str,
    role: str = "viewer"
) -> bool:
    """Share a folder with another user by email. Re-sharing updates the role."""
    folder, _ = await require_folder(db, folder_id, owner_id, required="owner")
    if role not in ("viewer", "editor"):
        raise ValueError("Role must be 'viewer' or 'editor'")

    target_user = (await db.execute(
        select(User).where(User.email == target_email.strip().lower())
    )).scalars().first()
    if not target_user:
        # Fall back to case-sensitive match for legacy rows
        target_user = (await db.execute(select(User).where(User.email == target_email))).scalars().first()
    if not target_user:
        raise NotFoundError("User with that email does not exist.")
    if target_user.id == owner_id:
        raise ValueError("You cannot share a folder with yourself.")

    existing = (await db.execute(
        select(FolderPermission).where(
            FolderPermission.folder_id == folder_id,
            FolderPermission.user_id == target_user.id,
        )
    )).scalars().first()
    if existing:
        existing.role = role
        db.add(existing)
    else:
        db.add(FolderPermission(folder_id=folder_id, user_id=target_user.id, role=role))

    folder.shared = True
    db.add(folder)
    await db.commit()
    return True


async def list_folder_permissions(db: AsyncSession, folder_id: UUID, user_id: UUID) -> List[dict]:
    """Who has access to this folder (for the Share dialog). Viewable by anyone with access."""
    await require_folder(db, folder_id, user_id, required="viewer")
    rows = (await db.execute(
        select(FolderPermission, User)
        .join(User, User.id == FolderPermission.user_id)
        .where(FolderPermission.folder_id == folder_id)
        .order_by(User.email)
    )).all()
    return [
        {
            "user_id": u.id,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "role": p.role,
        }
        for p, u in rows
    ]


async def get_shared_folders(db: AsyncSession, user_id: UUID) -> List[VirtualFolder]:
    """Get all (non-trashed) folders that have been shared directly with this user."""
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
    """
    Revoke a user's access to a shared folder.
    Allowed for the owner, or for a sharee removing themselves ("Remove" in Shared with me).
    """
    target_user = (await db.execute(select(User).where(User.email == target_email))).scalars().first()
    if not target_user:
        raise NotFoundError("User with that email does not exist.")

    folder = await db.get(VirtualFolder, folder_id)
    if not folder:
        raise NotFoundError("Folder not found")
    if folder.user_id != owner_id and target_user.id != owner_id:
        raise ForbiddenError("Only the owner can remove other people's access")

    perm = (await db.execute(
        select(FolderPermission).where(
            FolderPermission.folder_id == folder_id,
            FolderPermission.user_id == target_user.id
        )
    )).scalars().first()
    if perm:
        await db.delete(perm)
        await db.flush()
        remaining = (await db.execute(
            select(FolderPermission.id).where(FolderPermission.folder_id == folder_id)
        )).scalars().first()
        if not remaining:
            folder.shared = False
            db.add(folder)
        await db.commit()
    return True


# ---------------------------------------------------------------------------
# Folder download (client-side streaming ZIP — see internal/doubts-plan.md)
# ---------------------------------------------------------------------------

async def prepare_folder_download(
    db: AsyncSession,
    folder_id: UUID,
    user_id: UUID,
) -> dict:
    """
    Build the manifest the frontend needs to stream a ZIP to disk (StreamSaver.js + fflate):
    every sub-folder path (so empty folders survive), every downloadable file with its
    relative path and chunk URLs/tokens, plus a list of files that can't be downloaded.

    One broken file (e.g. its drive is disconnected) no longer fails the whole folder.
    Access tokens are cached per drive account, so a 50GB folder costs a handful of
    OAuth calls instead of one per chunk. Tokens expire (~1h): for long downloads the
    frontend re-calls GET /files/{id}/download for fresh tokens.
    """
    folder, _ = await require_folder(db, folder_id, user_id, required="viewer")

    folder_paths: Dict[UUID, str] = {folder_id: ""}
    frontier = [folder_id]
    while frontier:
        children = (await db.execute(
            select(VirtualFolder).where(
                VirtualFolder.parent_id.in_(frontier),
                VirtualFolder.is_deleted == False,
            )
        )).scalars().all()
        next_frontier = []
        for child in children:
            parent_path = folder_paths[child.parent_id]
            folder_paths[child.id] = f"{parent_path}{child.name}/"
            next_frontier.append(child.id)
        frontier = next_frontier

    files_q = await db.execute(
        select(VirtualFile)
        .where(
            VirtualFile.folder_id.in_(list(folder_paths.keys())),
            VirtualFile.is_deleted == False,
            VirtualFile.status == "available",
        )
        .order_by(VirtualFile.name)
    )
    virtual_files = files_q.scalars().all()

    from app.services.virtual_file_service import build_chunk_downloads

    token_cache: dict = {}
    files, unavailable = [], []
    total_size = 0
    for vf in virtual_files:
        rel_path = folder_paths[vf.folder_id] + vf.name
        try:
            chunk_downloads = await build_chunk_downloads(db, vf, token_cache)
        except Exception as e:
            logger.warning(f"Folder download: skipping file {vf.id}: {e}")
            unavailable.append({"file_id": str(vf.id), "relative_path": rel_path, "reason": str(e)})
            continue
        total_size += vf.size
        files.append({
            "file_id": str(vf.id),
            "name": vf.name,
            "size": vf.size,
            "mime_type": vf.mime_type,
            "relative_path": rel_path,
            "chunks": chunk_downloads,
        })

    return {
        "folder_id": str(folder.id),
        "folder_name": folder.name,
        "total_size": total_size,
        "folders": sorted(p for p in folder_paths.values() if p),
        "files": files,
        "unavailable_files": unavailable,
    }
