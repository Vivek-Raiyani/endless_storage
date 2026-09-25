import os
from abc import ABC, abstractmethod
from app.core.config import settings


class StorageProvider(ABC):
    """Abstract base class for all storage providers."""

    @abstractmethod
    def upload_file(self, user_id: str, service: str, filename: str, file_bytes: bytes) -> tuple[str, str]:
        """
        Uploads a file.

        Returns:
            (storage_key, file_url) — key is the stable identifier used for
            deletes; file_url is the URL clients can use to access the file.
        """
        pass

    @abstractmethod
    def delete_file(self, storage_key: str) -> bool:
        """Deletes a file by its storage key. Returns True on success."""
        pass

    @abstractmethod
    def get_file_url(self, storage_key: str) -> str:
        """
        Returns the URL to access the file.
        For cloud providers this generates a fresh presigned URL.
        For local storage this returns a static URL.
        """
        pass


class LocalStorageProvider(StorageProvider):
    """Implementation for local file system storage."""

    def __init__(self, base_dir: str = "media"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _storage_key(self, user_id: str, service: str, filename: str) -> str:
        return f"users/{user_id}/{service}/{filename}"

    def upload_file(self, user_id: str, service: str, filename: str, file_bytes: bytes) -> tuple[str, str]:
        key = self._storage_key(user_id, service, filename)
        file_path = os.path.join(self.base_dir, key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        url = self.get_file_url(key)
        return key, url

    def delete_file(self, storage_key: str) -> bool:
        file_path = os.path.join(self.base_dir, storage_key)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def get_file_url(self, storage_key: str) -> str:
        return f"{settings.SERVER_HOST.rstrip('/')}/{self.base_dir}/{storage_key}"


class CloudStorageProvider(StorageProvider):
    """Implementation for AWS S3 cloud storage using presigned URLs."""

    def __init__(self, presigned_expiry: int = 3600):
        import boto3
        from botocore.config import Config
        if not all([
            settings.AWS_ENDPOINT,
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY,
            settings.AWS_REGION_NAME,
            settings.AWS_BUCKET_NAME,
        ]):
            raise ValueError("Missing AWS S3 configuration in settings")
        self.endpoint_url = settings.AWS_ENDPOINT
        self.bucket_name = settings.AWS_BUCKET_NAME
        self.region = settings.AWS_REGION_NAME
        self.presigned_expiry = presigned_expiry  # seconds
        # Backblaze B2 (and other S3-compatible providers) require explicit
        # Signature Version 4; without this boto3 may use SigV2 which B2
        # accepts for uploads but silently ignores for deletes.
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=self.region,
            config=Config(signature_version="s3v4"),
        )

    def _storage_key(self, user_id: str, service: str, filename: str) -> str:
        return f"users/{user_id}/{service}/{filename}"

    def upload_file(self, user_id: str, service: str, filename: str, file_bytes: bytes) -> tuple[str, str]:
        key = self._storage_key(user_id, service, filename)
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=file_bytes,
        )
        url = self.get_file_url(key)
        return key, url

    def delete_file(self, storage_key: str) -> bool:
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=storage_key)
        return True

    def get_file_url(self, storage_key: str) -> str:
        """Generates a fresh presigned URL valid for `presigned_expiry` seconds."""
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": storage_key},
            ExpiresIn=self.presigned_expiry,
        )


def get_storage_provider() -> StorageProvider:
    """Factory to return the configured storage provider."""
    provider = getattr(settings, "STORAGE_PROVIDER", "local").lower()

    if provider == "local":
        return LocalStorageProvider()
    elif provider in ("cloud", "s3"):
        return CloudStorageProvider()
    else:
        raise ValueError(f"Unsupported storage provider: {provider}")


# Singleton — import and use anywhere:
#   from app.utils.storage import storage
#   key, url = storage.upload_file(user_id, service, filename, file_bytes)
storage = get_storage_provider()
