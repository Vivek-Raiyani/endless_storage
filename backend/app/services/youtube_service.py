import httpx
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)
from app.core.config import settings

class YouTubeService:
    BASE_URL = "https://www.googleapis.com/youtube/v3/videos"

    async def fetch_video_stats(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches the viewCount for a given YouTube video ID.
        """
        if not settings.YOUTUBE_API_KEY:
            # Cannot fetch without an API key
            return None

        params = {
            "part": "statistics",
            "id": video_id,
            "key": settings.YOUTUBE_API_KEY
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

                if "items" in data and len(data["items"]) > 0:
                    stats = data["items"][0].get("statistics", {})
                    # The user requested only viewCount for now
                    return {
                        "viewCount": int(stats.get("viewCount", 0))
                    }
                return None
            except Exception as e:
                logger.error(f"Error fetching YouTube stats for {video_id}: {e}")
                return None

youtube_service = YouTubeService()
