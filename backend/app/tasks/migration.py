import logging
import asyncio
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.models.storage_account import StorageAccount
from app.models.virtual_file import FileChunk, VirtualFile
from app.services.providers.factory import ProviderFactory

logger = logging.getLogger(__name__)

async def process_pending_migrations(db: AsyncSession = None) -> None:
    # If no db session is provided, create one
    if db is None:
        async with SessionLocal() as session:
            await _run_migrations(session)
    else:
        await _run_migrations(db)

async def _run_migrations(db: AsyncSession) -> None:
    # Get all accounts that are migrating or deleting
    result = await db.execute(
        select(StorageAccount).where(StorageAccount.status.in_(["migrating", "deleting"]))
    )
    accounts = result.scalars().all()
    
    if not accounts:
        return
        
    for account in accounts:
        if account.status == "deleting":
            await _process_deleting_account(db, account)
        elif account.status == "migrating":
            await _process_migrating_account(db, account)

async def _process_deleting_account(db: AsyncSession, account: StorageAccount):
    # Process chunks for this account
    count_result = await db.execute(
        select(func.count(FileChunk.id)).where(FileChunk.storage_account_id == account.id)
    )
    total_chunks = count_result.scalar()
    
    if total_chunks == 0:
        logger.info(f"Account {account.id} successfully deleted.")
        await db.delete(account)
        await db.commit()
        return
        
    # Limit to processing 1000 chunks per run to avoid memory and timeout issues
    result = await db.execute(
        select(FileChunk).where(FileChunk.storage_account_id == account.id).limit(1000)
    )
    chunks = result.scalars().all()
        
    provider = ProviderFactory.get_provider(account.provider)
    deleted_count = 0
    
    # Process in batches of 100
    for i in range(0, len(chunks), 100):
        batch = chunks[i:i+100]
        provider_ids = [c.provider_file_id for c in batch if c.provider_file_id]
        
        try:
            if provider_ids:
                if hasattr(provider, 'batch_delete_files'):
                    await provider.batch_delete_files(account.encrypted_refresh_token, provider_ids)
                else:
                    for p_id in provider_ids:
                        await provider.delete_file(account.encrypted_refresh_token, p_id)
            
            for chunk in batch:
                await db.delete(chunk)
            deleted_count += len(batch)
        except Exception as e:
            logger.error(f"Failed to delete batch of chunks from drive: {e}")
            
        # Sleep to prevent Google Drive API rate limiting
        await asyncio.sleep(5)
            
    if deleted_count > 0:
        account.status_message = f"Deleting chunks... ({total_chunks - deleted_count} remaining)"
        db.add(account)
        await db.commit()
    elif total_chunks > 0:
        account.status_message = f"Deleting chunks failed. Check logs. ({total_chunks} remaining)"
        db.add(account)
        await db.commit()

async def _process_migrating_account(db: AsyncSession, account: StorageAccount):
    count_result = await db.execute(
        select(func.count(FileChunk.id)).where(FileChunk.storage_account_id == account.id)
    )
    total_chunks = count_result.scalar()
    
    if total_chunks == 0:
        logger.info(f"Account {account.id} successfully migrated and disconnected.")
        await db.delete(account)
        await db.commit()
        return
        
    # Get only the 20 chunks we will process in this run
    result = await db.execute(
        select(FileChunk).where(FileChunk.storage_account_id == account.id).limit(20)
    )
    chunks = result.scalars().all()
        
    provider = ProviderFactory.get_provider(account.provider)
    migrated_count = 0
    for chunk in chunks: # Batch size 20
        try:
            if not chunk.target_account_id:
                logger.error(f"Chunk {chunk.id} has no target_account_id set.")
                continue
                
            # Fetch the pre-assigned target account
            target_account = await db.get(StorageAccount, chunk.target_account_id)
            if not target_account or target_account.status != "active":
                account.status = "error"
                account.status_message = "Migration stalled: target account unavailable."
                db.add(account)
                await db.commit()
                return

            # Share & Copy
            target_provider = ProviderFactory.get_provider(target_account.provider)
            await provider.share_file(
                account.encrypted_refresh_token, 
                chunk.provider_file_id, 
                target_account.provider_account_email
            )
            
            new_provider_file_id = await target_provider.copy_file(
                target_account.encrypted_refresh_token,
                chunk.provider_file_id,
                target_account.root_folder_id,
                f"migrated_chunk_{chunk.id}"
            )
            
            # Delete original
            await provider.delete_file(account.encrypted_refresh_token, chunk.provider_file_id)
            
            # Update chunk
            chunk.storage_account_id = target_account.id
            chunk.target_account_id = None
            chunk.provider_file_id = new_provider_file_id
            db.add(chunk)
            
            # Update target account used bytes & free the reserved bytes
            target_account.used_bytes += chunk.size
            target_account.app_used_bytes += chunk.size
            target_account.reserved_bytes = max(0, target_account.reserved_bytes - chunk.size)
            db.add(target_account)
            
            # Update source account used bytes
            account.used_bytes -= chunk.size
            account.app_used_bytes -= chunk.size
            db.add(account)
            
            migrated_count += 1
            await db.commit() 
        except Exception as e:
            logger.error(f"Failed to migrate chunk {chunk.id}: {e}")
            
    if migrated_count > 0:
        account.status_message = f"Migrating chunks... ({total_chunks - migrated_count} remaining)"
        db.add(account)
        await db.commit()
    elif total_chunks > 0:
        account.status_message = f"Migrating chunks failed. Check logs. ({total_chunks} remaining)"
        db.add(account)
        await db.commit()
