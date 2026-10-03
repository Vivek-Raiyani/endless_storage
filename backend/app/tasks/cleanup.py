import logging
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.virtual_file import FileChunk
from app.models.storage_account import StorageAccount
from app.services.providers.factory import ProviderFactory

logger = logging.getLogger(__name__)

async def cleanup_orphaned_chunks(db: AsyncSession) -> None:
    """
    Finds any chunks stuck in 'pending_deletion' status, attempts to delete them
    from Google Drive, and if successful, marks them 'deleted' and frees capacity.
    """
    result = await db.execute(
        select(FileChunk, StorageAccount)
        .join(StorageAccount, FileChunk.storage_account_id == StorageAccount.id)
        .where(FileChunk.status == "pending_deletion")
    )
    rows = result.all()
    
    if not rows:
        return
        
    logger.info(f"Found {len(rows)} orphaned chunks to clean up.")

    # Group chunks by account to use batch deletes
    from collections import defaultdict
    account_groups = defaultdict(list)
    for chunk, account in rows:
        if account.encrypted_refresh_token and chunk.provider_file_id:
            account_groups[account].append(chunk)

    for account, chunks in account_groups.items():
        provider = ProviderFactory.get_provider(account.provider)
        
        # Process in batches of 100
        for i in range(0, len(chunks), 100):
            batch = chunks[i:i+100]
            provider_ids = [c.provider_file_id for c in batch]
            
            try:
                # Issue 1 batch HTTP request for up to 100 files
                if hasattr(provider, 'batch_delete_files'):
                    await provider.batch_delete_files(account.encrypted_refresh_token, provider_ids)
                else:
                    # Fallback for providers that don't support batching
                    for p_id in provider_ids:
                        await provider.delete_file(account.encrypted_refresh_token, p_id)
                
                # If successful (or Google returned 200 OK for the batch), update DB
                for chunk in batch:
                    chunk.status = "deleted"
                    account.used_bytes -= chunk.size
                    account.app_used_bytes -= chunk.size
                    db.add(chunk)
                
                db.add(account)
                logger.info(f"Successfully cleaned up {len(batch)} orphaned chunks for account {account.id}")
                
            except Exception as e:
                logger.error(f"Failed to clean up batch of chunks for account {account.id}: {e}")
                
            # Sleep to prevent Google Drive API rate limiting (20,000 req / 100s)
            await asyncio.sleep(5)

    await db.commit()
    logger.info("Periodic orphaned chunk cleanup completed.")
