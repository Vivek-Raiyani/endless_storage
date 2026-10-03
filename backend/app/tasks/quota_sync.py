import logging
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.storage_account import StorageAccount
from app.models.virtual_file import FileChunk, VirtualFile

logger = logging.getLogger(__name__)

async def sync_app_used_bytes_all_accounts(db: AsyncSession) -> None:
    """
    Periodically checks the exact size of all chunks stored in each account
    and updates the app_used_bytes column to fix any drift.
    """
    # Get all accounts
    result = await db.execute(select(StorageAccount))
    accounts = result.scalars().all()

    for account in accounts:
        # Sum all chunk sizes for this account that are complete or pending deletion
        stmt = (
            select(func.coalesce(func.sum(FileChunk.size), 0))
            .where(
                FileChunk.storage_account_id == account.id,
                FileChunk.status.in_(["complete", "pending_deletion"])
            )
        )
        sum_result = await db.execute(stmt)
        actual_used_bytes = sum_result.scalar()

        if actual_used_bytes != account.app_used_bytes:
            logger.info(
                f"Drift detected for account {account.id}. "
                f"Updating app_used_bytes from {account.app_used_bytes} to {actual_used_bytes}."
            )
            account.app_used_bytes = actual_used_bytes
            db.add(account)

    await db.commit()
    logger.info("Periodic quota sync completed.")
