import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.database import SessionLocal
from app.tasks.quota_sync import sync_app_used_bytes_all_accounts
from app.tasks.cleanup import cleanup_orphaned_chunks

logger = logging.getLogger(__name__)

async def run_quota_sync_job():
    logger.info("Starting scheduled quota sync job...")
    async with SessionLocal() as db:
        try:
            await sync_app_used_bytes_all_accounts(db)
        except Exception as e:
            logger.error(f"Error during quota sync job: {e}")

async def run_migration_job():
    logger.info("Starting scheduled migration job...")
    from app.tasks.migration import process_pending_migrations
    try:
        await process_pending_migrations()
    except Exception as e:
        logger.error(f"Error during migration job: {e}")

async def run_cleanup_job():
    logger.info("Starting scheduled cleanup job...")
    async with SessionLocal() as db:
        try:
            await cleanup_orphaned_chunks(db)
        except Exception as e:
            logger.error(f"Error during cleanup job: {e}")


def setup_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    
    # Run every night at 2:00 AM (server time)
    scheduler.add_job(
        run_quota_sync_job,
        trigger=CronTrigger(hour=2, minute=0),
        id="quota_sync",
        name="Nightly Quota Sync",
        replace_existing=True
    )
    
    # Run every night at 3:00 AM (server time)
    scheduler.add_job(
        run_cleanup_job,
        trigger=CronTrigger(hour=3, minute=0),
        id="cleanup_orphaned",
        name="Nightly Orphaned Chunk Cleanup",
        replace_existing=True
    )
    
    # Run every 30 minutes
    scheduler.add_job(
        run_migration_job,
        trigger="interval",
        minutes=30,
        id="process_migrations",
        name="Process Storage Account Migrations",
        replace_existing=True
    )
    
    return scheduler