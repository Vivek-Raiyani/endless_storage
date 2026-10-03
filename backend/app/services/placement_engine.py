"""
Placement Engine
================
Decides how to distribute fixed-size chunks of a file across available StorageAccounts.

Algorithm:
1. Calculate how many fixed-size chunks the file needs.
2. Sort available storage accounts by available_bytes (descending).
3. Round-robin assign chunks to accounts that have enough space,
   atomically reserving bytes as we go to prevent race conditions.

The result is a list of PlacedChunk objects, each describing:
  - chunk_index
  - offset in the original file
  - size (may be smaller for the last chunk)
  - which storage_account_id it goes to
"""
import math
import logging
from dataclasses import dataclass
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.storage_account import StorageAccount
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PlacedChunk:
    chunk_index: int
    offset: int
    size: int
    storage_account_id: UUID


class InsufficientStorageError(Exception):
    """Raised when there is not enough total free space across all accounts."""
    pass


class PlacementEngine:
    """Stateless placement engine — receives accounts list and file size, returns placements."""

    def __init__(self, chunk_size: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE_BYTES

    def calculate_chunks(self, file_size: int) -> int:
        """Total number of fixed-size chunks needed for this file."""
        return math.ceil(file_size / self.chunk_size)

    def plan(
        self,
        file_size: int,
        accounts: List[StorageAccount],
    ) -> List[PlacedChunk]:
        """
        Pure planning step — does NOT write to the DB. Returns a placement plan.
        The caller is responsible for atomically reserving capacity afterwards.

        Raises InsufficientStorageError if total available space < file_size.
        """
        total_available = sum(a.available_bytes for a in accounts)
        if total_available < file_size:
            raise InsufficientStorageError(
                f"Need {file_size:,} bytes but only {total_available:,} available "
                f"across {len(accounts)} account(s)."
            )

        num_chunks = self.calculate_chunks(file_size)

        # Sort by available capacity, largest first
        sorted_accounts = sorted(accounts, key=lambda a: a.available_bytes, reverse=True)

        # Track in-memory reserved bytes per account (for planning only)
        in_flight: dict[UUID, int] = {a.id: 0 for a in sorted_accounts}

        placements: List[PlacedChunk] = []

        for i in range(num_chunks):
            offset = i * self.chunk_size
            chunk_size = min(self.chunk_size, file_size - offset)

            # Find the account with the most space available (accounting for in-flight)
            chosen = None
            for account in sorted_accounts:
                effective_available = account.available_bytes - in_flight[account.id]
                if effective_available >= chunk_size:
                    chosen = account
                    break

            if chosen is None:
                raise InsufficientStorageError(
                    f"Could not place chunk {i} (size {chunk_size:,} bytes): "
                    f"no single account has enough free space."
                )

            in_flight[chosen.id] += chunk_size
            placements.append(PlacedChunk(
                chunk_index=i,
                offset=offset,
                size=chunk_size,
                storage_account_id=chosen.id,
            ))

        logger.info(
            f"Placement plan: {num_chunks} chunks for {file_size:,} bytes "
            f"across {len(set(p.storage_account_id for p in placements))} account(s)"
        )
        return placements


async def reserve_capacity(
    db: AsyncSession,
    placements: List[PlacedChunk],
) -> None:
    """
    Atomically increment reserved_bytes on each storage account for the planned chunks.
    This prevents double-booking when multiple uploads start simultaneously.
    """
    # Aggregate reservation per account
    reservations: dict[UUID, int] = {}
    for p in placements:
        reservations[p.storage_account_id] = (
            reservations.get(p.storage_account_id, 0) + p.size
        )

    for account_id, bytes_to_reserve in reservations.items():
        await db.execute(
            update(StorageAccount)
            .where(StorageAccount.id == account_id)
            .values(reserved_bytes=StorageAccount.reserved_bytes + bytes_to_reserve)
        )
    await db.commit()


async def release_reservation(
    db: AsyncSession,
    account_id: UUID,
    bytes_to_release: int,
) -> None:
    """Release reserved bytes when a chunk upload completes or fails."""
    await db.execute(
        update(StorageAccount)
        .where(StorageAccount.id == account_id)
        .values(
            reserved_bytes=StorageAccount.reserved_bytes - bytes_to_release,
        )
    )
    await db.commit()


# Module-level singleton
placement_engine = PlacementEngine()
