from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple

class StorageProvider(ABC):
    """
    Abstract base class for all storage providers (Google Drive, OneDrive, Dropbox, etc).
    All provider-specific implementations must inherit from this class and implement these methods.
    """

    @abstractmethod
    async def get_quota(self, encrypted_refresh_token: str) -> dict:
        """
        Fetch storage quota from the provider.
        Returns dict with 'limit', 'usage', etc. (in bytes).
        """
        pass

    @abstractmethod
    async def ensure_app_folder(self, encrypted_refresh_token: str, folder_name: str = "EndlessStorage") -> str:
        """
        Ensure the app folder exists in the provider's root.
        Returns the provider's folder ID.
        """
        pass

    @abstractmethod
    async def create_resumable_upload_session(
        self,
        encrypted_refresh_token: str,
        folder_id: str,
        filename: str,
        mime_type: str,
        file_size: int,
    ) -> str:
        """
        Ask the provider to create a resumable upload session.
        Returns the session URI that the frontend will PUT bytes to directly.
        """
        pass

    @abstractmethod
    async def get_download_url(
        self,
        encrypted_refresh_token: str,
        provider_file_id: str,
    ) -> Tuple[str, str]:
        """
        Get a short-lived direct download URL for a chunk.
        Returns a tuple of (download_url, access_token).
        The access_token is typically attached as a Bearer token by the frontend.
        """
        pass

    @abstractmethod
    async def delete_file(self, encrypted_refresh_token: str, provider_file_id: str) -> None:
        """
        Permanently delete a chunk file from the provider.
        Must treat "already deleted" (404) as success and raise on any other failure.
        """
        pass

    @abstractmethod
    async def get_access_token(self, encrypted_refresh_token: str) -> Tuple[str, datetime]:
        """
        Return a short-lived access token and its UTC expiry time.
        Implementations should cache tokens until shortly before expiry.
        """
        pass

    @abstractmethod
    def build_download_url(self, provider_file_id: str) -> str:
        """Return the direct-download URL for a chunk (used with a Bearer access token)."""
        pass
