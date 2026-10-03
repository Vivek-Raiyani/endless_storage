from app.services.providers.base import StorageProvider
from app.services.providers.google import GoogleDriveProvider

class ProviderFactory:
    """
    Factory to retrieve the correct StorageProvider implementation
    based on the provider name string from the database.
    """
    
    @staticmethod
    def get_provider(provider_name: str) -> StorageProvider:
        if provider_name == "google_drive":
            return GoogleDriveProvider()
        # elif provider_name == "onedrive":
        #     return OneDriveProvider()
        # elif provider_name == "dropbox":
        #     return DropboxProvider()
        else:
            raise ValueError(f"Unknown storage provider: {provider_name}")
