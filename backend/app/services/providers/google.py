import logging
from typing import Tuple, List

import httpx

from app.core.encryption import decrypt_token
from app.core.config import settings
from app.services.providers.base import StorageProvider

logger = logging.getLogger(__name__)

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_DRIVE_FILES_URL = "https://www.googleapis.com/drive/v3/files"
GOOGLE_DRIVE_UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files"
GOOGLE_DRIVE_ABOUT_URL = "https://www.googleapis.com/drive/v3/about"


class GoogleDriveProvider(StorageProvider):
    """
    Google Drive implementation of the StorageProvider interface.
    """

    async def _refresh_access_token(self, encrypted_refresh_token: str) -> str:
        """
        Exchange the stored (encrypted) refresh token for a short-lived access token.
        """
        refresh_token = decrypt_token(encrypted_refresh_token)
        if not refresh_token:
            raise ValueError("Could not decrypt refresh token")

        async with httpx.AsyncClient() as client:
            resp = await client.post(GOOGLE_TOKEN_URL, data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            })
            resp.raise_for_status()
            data = resp.json()
            return data["access_token"]

    async def get_quota(self, encrypted_refresh_token: str) -> dict:
        access_token = await self._refresh_access_token(encrypted_refresh_token)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                GOOGLE_DRIVE_ABOUT_URL,
                params={"fields": "storageQuota"},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            quota = resp.json().get("storageQuota", {})
            return {
                "limit": int(quota.get("limit", 0)),
                "usage": int(quota.get("usage", 0)),
                "usage_in_drive": int(quota.get("usageInDrive", 0)),
            }

    async def ensure_app_folder(self, encrypted_refresh_token: str, folder_name: str = "EndlessStorage") -> str:
        access_token = await self._refresh_access_token(encrypted_refresh_token)
        async with httpx.AsyncClient() as client:
            # Search for existing folder
            query = (
                f"name='{folder_name}' "
                f"and mimeType='application/vnd.google-apps.folder' "
                f"and trashed=false"
            )
            resp = await client.get(
                GOOGLE_DRIVE_FILES_URL,
                params={"q": query, "fields": "files(id,name)"},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            files = resp.json().get("files", [])
            if files:
                return files[0]["id"]

            # Create folder
            resp = await client.post(
                GOOGLE_DRIVE_FILES_URL,
                json={
                    "name": folder_name,
                    "mimeType": "application/vnd.google-apps.folder",
                },
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            return resp.json()["id"]

    async def create_resumable_upload_session(
        self,
        encrypted_refresh_token: str,
        folder_id: str,
        filename: str,
        mime_type: str,
        file_size: int,
    ) -> str:
        access_token = await self._refresh_access_token(encrypted_refresh_token)

        metadata = {
            "name": filename,
            "parents": [folder_id],
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GOOGLE_DRIVE_UPLOAD_URL}?uploadType=resumable",
                json=metadata,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "X-Upload-Content-Type": mime_type or "application/octet-stream",
                    "X-Upload-Content-Length": str(file_size),
                },
            )
            resp.raise_for_status()

        session_uri = resp.headers.get("Location")
        if not session_uri:
            raise ValueError("Google Drive did not return a resumable session URI")

        return session_uri

    async def get_download_url(
        self,
        encrypted_refresh_token: str,
        provider_file_id: str,
    ) -> Tuple[str, str]:
        access_token = await self._refresh_access_token(encrypted_refresh_token)
        download_url = f"{GOOGLE_DRIVE_FILES_URL}/{provider_file_id}?alt=media"
        return download_url, access_token

    async def delete_file(self, encrypted_refresh_token: str, provider_file_id: str) -> None:
        access_token = await self._refresh_access_token(encrypted_refresh_token)
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{GOOGLE_DRIVE_FILES_URL}/{provider_file_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if resp.status_code not in (200, 204):
                logger.warning(f"Failed to delete Drive file {provider_file_id}: {resp.status_code}")

    async def batch_delete_files(self, encrypted_refresh_token: str, provider_file_ids: List[str]) -> None:
        if not provider_file_ids:
            return
            
        access_token = await self._refresh_access_token(encrypted_refresh_token)
        boundary = "batch_delete_boundary"
        
        lines = []
        for file_id in provider_file_ids:
            lines.append(f"--{boundary}")
            lines.append("Content-Type: application/http")
            lines.append("")
            lines.append(f"DELETE https://www.googleapis.com/drive/v3/files/{file_id} HTTP/1.1")
            lines.append("")
            lines.append("")
        
        lines.append(f"--{boundary}--")
        body = "\r\n".join(lines) + "\r\n"
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://www.googleapis.com/batch/drive/v3",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": f"multipart/mixed; boundary={boundary}"
                },
                content=body
            )
            if resp.status_code != 200:
                logger.warning(f"Batch delete request failed with status {resp.status_code}: {resp.text}")

    async def share_file(self, encrypted_refresh_token: str, provider_file_id: str, target_email: str) -> None:
        access_token = await self._refresh_access_token(encrypted_refresh_token)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GOOGLE_DRIVE_FILES_URL}/{provider_file_id}/permissions",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"type": "user", "role": "reader", "emailAddress": target_email}
            )
            if resp.status_code not in (200, 201):
                logger.error(f"Failed to share Drive file {provider_file_id}: {resp.status_code} - {resp.text}")
                raise ValueError("Failed to share file")

    async def copy_file(self, encrypted_refresh_token: str, provider_file_id: str, target_folder_id: str, new_name: str) -> str:
        access_token = await self._refresh_access_token(encrypted_refresh_token)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GOOGLE_DRIVE_FILES_URL}/{provider_file_id}/copy",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"parents": [target_folder_id], "name": new_name}
            )
            if resp.status_code not in (200, 201):
                logger.error(f"Failed to copy Drive file {provider_file_id}: {resp.status_code} - {resp.text}")
                raise ValueError("Failed to copy file")
            return resp.json()["id"]
