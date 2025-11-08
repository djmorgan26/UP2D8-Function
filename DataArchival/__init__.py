import azure.functions as func
from datetime import datetime, timedelta, UTC
import pymongo
from dotenv import load_dotenv
from shared.key_vault_client import get_secret_client
from shared.backend_client import BackendAPIClient
import structlog
from shared.logger_config import configure_logger

# Configure structlog
configure_logger()
logger = structlog.get_logger()

def main(timer: func.TimerRequest) -> None:
    """
    Weekly timer-triggered function to archive/delete old data.

    Schedule: 0 0 * * 0 (Every Sunday at midnight UTC)

    Performs:
    - Archives processed articles older than 90 days
    - Deletes old analytics events older than 180 days
    - Logs archival metrics to backend analytics
    """
    load_dotenv()
    logger.info("DataArchival function executing", past_due=timer.past_due)

    try:
        # Initialize clients
        secret_client = get_secret_client()
        backend_client = BackendAPIClient()

        cosmos_connection = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
        client = pymongo.MongoClient(cosmos_connection)
        db = client.up2d8

        # --- Archive processed articles older than 90 days ---
        article_cutoff_date = datetime.now(UTC) - timedelta(days=90)

        result = db.articles.delete_many({
            "processed": True,
            "created_at": {"$lt": article_cutoff_date}
        })

        archived_articles_count = result.deleted_count
        logger.info("Archived old processed articles", count=archived_articles_count)

        # --- Delete old analytics events (keep 180 days) ---
        analytics_cutoff = datetime.now(UTC) - timedelta(days=180)

        analytics_result = db.analytics.delete_many({
            "timestamp": {"$lt": analytics_cutoff}
        })

        archived_analytics_count = analytics_result.deleted_count
        logger.info("Archived old analytics events", count=archived_analytics_count)

        # --- Log archival metrics to backend ---
        backend_client.log_analytics("data_archival_completed", {
            "articles_archived": archived_articles_count,
            "analytics_archived": archived_analytics_count,
            "article_cutoff_days": 90,
            "analytics_cutoff_days": 180,
            "article_cutoff_date": article_cutoff_date.isoformat(),
            "analytics_cutoff_date": analytics_cutoff.isoformat()
        })

        logger.info(
            "DataArchival completed successfully",
            articles_archived=archived_articles_count,
            analytics_archived=archived_analytics_count
        )

    except Exception as e:
        logger.error("DataArchival failed", error=str(e))
        # Try to log the failure to analytics
        try:
            backend_client = BackendAPIClient()
            backend_client.log_analytics("data_archival_failed", {
                "error": str(e)
            })
        except:
            pass  # Don't fail the function if analytics logging fails

    logger.info("DataArchival function execution finished.")
