import os
import requests
from typing import Dict, Any, Optional
from shared.key_vault_client import get_secret_client
import structlog

logger = structlog.get_logger()

class BackendAPIClient:
    """
    Client for communicating with UP2D8-BACKEND FastAPI service.

    Provides methods to:
    - Create articles via POST /api/articles
    - Log analytics events via POST /api/analytics
    - Check backend health via GET /api/health
    """

    def __init__(self):
        """Initialize the backend API client with base URL from environment."""
        self.base_url = os.environ.get(
            "BACKEND_API_URL",
            "https://up2d8-backend.azurewebsites.net"
        )
        # Remove trailing slash if present
        self.base_url = self.base_url.rstrip('/')

        # Optional: Add API key authentication if backend requires it
        # secret_client = get_secret_client()
        # self.api_key = secret_client.get_secret("BACKEND-API-KEY").value

        logger.info("BackendAPIClient initialized", base_url=self.base_url)

    def create_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post a new article to the backend API.

        Args:
            article_data: Dictionary containing article fields:
                - title (str): Article title
                - link (str): Article URL
                - summary (str): Article summary/description
                - published (str): Publication date (ISO format)
                - tags (list[str], optional): Article tags
                - source (str, optional): Source type (rss, intelligent_crawler, manual)
                - content (str, optional): Full article content

        Returns:
            Dictionary with:
                - message (str): Success or error message
                - id (str): Article ID if created/exists

        Raises:
            requests.RequestException: If the API request fails
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/articles",
                json=article_data,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            logger.info(
                "Article API call successful",
                article_link=article_data.get("link"),
                message=result.get("message")
            )
            return result
        except requests.RequestException as e:
            logger.error(
                "Failed to create article via API",
                error=str(e),
                article=article_data.get("link"),
                status_code=getattr(e.response, 'status_code', None)
            )
            raise

    def log_analytics(
        self,
        event_type: str,
        details: Dict[str, Any],
        user_id: str = "system"
    ) -> Optional[Dict[str, Any]]:
        """
        Log an analytics event to the backend.

        Args:
            event_type: Type of event (e.g., "daily_scrape_completed")
            details: Event details dictionary
            user_id: User ID or "system" for automated events

        Returns:
            Response dictionary or None if request fails
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/analytics",
                json={
                    "user_id": user_id,
                    "event_type": event_type,
                    "details": details
                },
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            logger.debug("Analytics event logged", event_type=event_type)
            return response.json()
        except requests.RequestException as e:
            logger.warning(
                "Failed to log analytics event",
                error=str(e),
                event_type=event_type
            )
            return None

    def health_check(self) -> Dict[str, Any]:
        """
        Check backend API health status.

        Returns:
            Dictionary with health status:
                - status (str): "healthy" or "unhealthy"
                - database (str): Database connection status
                - collections (dict): Collection counts
                - timestamp (str): Check timestamp

        Returns error dict if health check fails.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/health",
                timeout=10
            )
            response.raise_for_status()
            health_data = response.json()
            logger.debug("Backend health check completed", status=health_data.get("status"))
            return health_data
        except requests.RequestException as e:
            logger.error("Backend health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": None
            }

    def get_users(self) -> Optional[list]:
        """
        Fetch all users from the backend API.

        Returns:
            List of user dictionaries or None if request fails
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/users",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error("Failed to fetch users from API", error=str(e))
            return None

    def get_rss_feeds(self) -> Optional[list]:
        """
        Fetch all RSS feeds from the backend API.

        Returns:
            List of RSS feed dictionaries or None if request fails
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/rss_feeds",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error("Failed to fetch RSS feeds from API", error=str(e))
            return None
