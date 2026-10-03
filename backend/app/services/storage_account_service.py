"""
Storage Account Service
=======================
CRUD and business logic for connected Google Drive accounts.
"""
import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.storage_account import StorageAccount
from app.models.virtual_file import FileChunk, VirtualFile
from app.core.encryption import encrypt_token
from app.services.providers.factory import ProviderFactory

logger = logging.getLogger(__name__)


async def get_accounts_for_user(db: AsyncSession, user_id: UUID) -> List[StorageAccount]:
    """Return all active storage accounts for a user."""
    result = await db.execute(
        select(StorageAccount)
        .where(StorageAccount.user_id == user_id)
        .order_by(StorageAccount.created_at)
    )
    return result.scalars().all()


async def get_account(db: AsyncSession, account_id: UUID, user_id: UUID) -> Optional[StorageAccount]:
    """Return a single storage account, scoped to the user."""
    result = await db.execute(
        select(StorageAccount)
        .where(StorageAccount.id == account_id, StorageAccount.user_id == user_id)
    )
    return result.scalars().first()

async def get_user_storage_summary(db: AsyncSession, user_id: UUID) -> dict:
    accounts = await get_accounts_for_user(db, user_id)
    return {
        "accounts_count": len(accounts),
        "active_accounts_count": len([a for a in accounts]),
        "total_bytes": sum(a.total_bytes or 0 for a in accounts),
        "used_bytes": sum(a.used_bytes or 0 for a in accounts),
        "available_bytes": sum(a.available_bytes or 0 for a in accounts),
        "trash_bytes": 0,
    }

async def connect_google_drive_account(
    db: AsyncSession,
    user_id: UUID,
    provider_account_id: str,
    provider_account_email: str,
    refresh_token: str,
) -> StorageAccount:
    """
    Connect a new Google Drive account.
    Encrypts the refresh token, creates the app folder in Drive, then syncs quota.
    """
    # Check if already connected
    existing = await db.execute(
        select(StorageAccount).where(
            StorageAccount.user_id == user_id,
            StorageAccount.provider_account_id == provider_account_id,
        )
    )
    account = existing.scalars().first()

    encrypted = encrypt_token(refresh_token)

    if account:
        # Reconnect — update the refresh token
        account.encrypted_refresh_token = encrypted
        account.status = "active"
        db.add(account)
        await db.commit()
        await db.refresh(account)
    else:
        account = StorageAccount(
            user_id=user_id,
            provider="google_drive",
            provider_account_id=provider_account_id,
            provider_account_email=provider_account_email,
            display_name=provider_account_email,
            encrypted_refresh_token=encrypted,
            status="active",
        )
        db.add(account)
        await db.commit()
        await db.refresh(account)

    # Create app folder in Drive
    try:
        provider = ProviderFactory.get_provider(account.provider)
        folder_id = await provider.ensure_app_folder(encrypted)
        account.root_folder_id = folder_id
        db.add(account)
        await db.commit()
        await db.refresh(account)
    except Exception as e:
        logger.error(f"Failed to create app folder for account {account.id}: {e}")

    # Sync quota
    await sync_quota(db, account)
    return account


async def sync_quota(db: AsyncSession, account: StorageAccount) -> StorageAccount:
    """
    Fetch current quota from Google Drive and update our DB.
    """
    try:
        provider = ProviderFactory.get_provider(account.provider)
        quota = await provider.get_quota(account.encrypted_refresh_token)
        account.total_bytes = quota["limit"]
        account.used_bytes = quota["usage"]
        
        # Default allocation limit to 80% of total space if not set
        if account.allocated_limit_bytes is None and account.total_bytes > 0:
            account.allocated_limit_bytes = int(account.total_bytes * 0.7)
            
        db.add(account)
        await db.commit()
        await db.refresh(account)
        logger.info(
            f"Synced quota for account {account.id}: "
            f"{quota['usage']:,}/{quota['limit']:,} bytes used"
        )
    except Exception as e:
        logger.error(f"Failed to sync quota for account {account.id}: {e}")
        account.status = "error"
        db.add(account)
        await db.commit()
    return account


async def sync_all_user_quotas(db: AsyncSession, user_id: UUID) -> List[StorageAccount]:
    """Sync quotas for all of a user's accounts."""
    accounts = await get_accounts_for_user(db, user_id)
    for account in accounts:
        await sync_quota(db, account)
    return accounts


async def preview_disconnect(db: AsyncSession, account_id: UUID, user_id: UUID) -> dict:
    account = await get_account(db, account_id, user_id)
    if not account:
        raise ValueError("Account not found")

    other_accounts_result = await db.execute(
        select(StorageAccount).where(
            StorageAccount.user_id == user_id,
            StorageAccount.id != account_id,
            StorageAccount.status == "active"
        )
    )
    other_accounts = other_accounts_result.scalars().all()
    available_bytes_elsewhere = sum(acc.available_bytes for acc in other_accounts)

    chunks_result = await db.execute(
        select(FileChunk).where(
            FileChunk.storage_account_id == account_id,
            FileChunk.status.in_(["complete", "verified"])
        )
    )
    chunks = chunks_result.scalars().all()
    
    total_bytes_to_move = sum(chunk.size for chunk in chunks)
    affected_files = set(chunk.file_id for chunk in chunks)

    # Bin Packing Simulation
    account_capacities = {acc.id: acc.available_bytes for acc in other_accounts}
    chunk_sizes = [(chunk.id, chunk.size) for chunk in chunks]
    # Sort chunks by size descending (largest first)
    chunk_sizes.sort(key=lambda x: x[1], reverse=True)
    
    can_migrate = True
    allocation_plan = {} # chunk_id -> target_acc_id
    reservations = {} # target_acc_id -> total_bytes_reserved
    
    for chunk_id, size in chunk_sizes:
        placed = False
        # Use Worst Fit to spread chunks out across drives
        best_acc_id = None
        max_cap = -1
        
        for acc_id, cap in account_capacities.items():
            if cap >= size and cap > max_cap:
                max_cap = cap
                best_acc_id = acc_id
                
        if best_acc_id:
            account_capacities[best_acc_id] -= size
            allocation_plan[chunk_id] = best_acc_id
            reservations[best_acc_id] = reservations.get(best_acc_id, 0) + size
            placed = True
        else:
            can_migrate = False
            break

    return {
        "can_migrate": can_migrate,
        "affected_files_count": len(affected_files),
        "total_bytes_to_move": total_bytes_to_move,
        "available_bytes_elsewhere": available_bytes_elsewhere,
        "allocation_plan": allocation_plan if can_migrate else {},
        "reservations": reservations if can_migrate else {}
    }


async def disconnect_account(db: AsyncSession, account_id: UUID, user_id: UUID, action: str) -> StorageAccount:
    """Mark an account as migrating or deleting."""
    account = await get_account(db, account_id, user_id)
    if not account:
        raise ValueError("Account not found")
        
    if account.status in ("migrating", "deleting"):
        return account

    if action == "migrate":
        preview = await preview_disconnect(db, account_id, user_id)
        if not preview["can_migrate"]:
            raise ValueError("Not enough space on other drives to migrate.")
            
        # Apply the allocation plan to chunks
        for chunk_id, target_acc_id in preview["allocation_plan"].items():
            logger.info(f"Assigning target_account_id {target_acc_id} to chunk {chunk_id} for migration")
            await db.execute(
                update(FileChunk)
                .where(FileChunk.id == chunk_id)
                .values(target_account_id=target_acc_id)
            )
            
        # Add to reserved_bytes of the other accounts
        for target_acc_id, reserved_amount in preview["reservations"].items():
            await db.execute(
                update(StorageAccount)
                .where(StorageAccount.id == target_acc_id)
                .values(reserved_bytes=StorageAccount.reserved_bytes + reserved_amount)
            )

        account.status = "migrating"
        account.status_message = "Migration queued..."
    elif action == "delete":
        account.status = "deleting"
        account.status_message = "Deletion queued..."
    else:
        raise ValueError("Invalid action")

    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account
