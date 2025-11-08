import os
import feedparser
import pymongo
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import azure.functions as func
from dotenv import load_dotenv
from shared.key_vault_client import get_secret_client
from shared.backend_client import BackendAPIClient
import structlog
from shared.logger_config import configure_logger

# Configure structlog
configure_logger()
logger = structlog.get_logger()

# Define a simple keyword-based tagging system
TAG_KEYWORDS = {
    "AI": ["ai", "artificial intelligence", "machine learning", "deep learning", "neural network"],
    "Tech": ["technology", "software", "hardware", "startup", "innovation"],
    "Science": ["science", "research", "discovery", "biology", "physics", "chemistry"],
    "Business": ["business", "economy", "finance", "market", "investment"],
    "Health": ["health", "medical", "medicine", "wellness", "fitness"],
    "Environment": ["environment", "climate", "sustainability", "ecology"],
}

def assign_tags(title: str, summary: str) -> list[str]:
    assigned_tags = []
    content = (title + " " + summary).lower()
    for tag, keywords in TAG_KEYWORDS.items():
        if any(keyword in content for keyword in keywords):
            assigned_tags.append(tag)
    return assigned_tags

def main(timer: func.TimerRequest) -> None:
    load_dotenv()
    start_time = datetime.now()
    logger.info('Python timer trigger function ran', past_due=timer.past_due)
    logger.info('DailyArticleScraper function is executing.')

    try:
        # Initialize backend API client
        backend_client = BackendAPIClient()

        # Get configuration from environment variables and Key Vault
        secret_client = get_secret_client()
        cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value

        # Connect to Cosmos DB (still needed for RSS feeds)
        client = pymongo.MongoClient(cosmos_db_connection_string)
        db = client.up2d8
        rss_feeds_collection = db.rss_feeds

        # Fetch RSS feeds from Cosmos DB
        rss_feeds = [feed['url'] for feed in rss_feeds_collection.find({})]
        if not rss_feeds:
            logger.warning("No RSS feeds found in Cosmos DB. DailyArticleScraper will not run.")
            return

        new_articles_count = 0
        failed_articles_count = 0
        duplicate_articles_count = 0

        for feed_url in rss_feeds:
            logger.info('Parsing feed', feed_url=feed_url)
            try:
                feed = feedparser.parse(feed_url)
                if feed.bozo:
                    logger.warning('Malformed feed detected', feed_url=feed_url, bozo_exception=str(feed.bozo_exception))
                    continue
            except Exception as e:
                logger.error('Error parsing feed', feed_url=feed_url, error=str(e))
                continue

            for entry in feed.entries:
                try:
                    # Assign tags to the article
                    tags = assign_tags(entry.title, entry.summary)

                    article_data = {
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.summary,
                        'published': entry.published,
                        'tags': tags,
                        'source': 'rss'
                    }

                    # Use backend API instead of direct DB write
                    result = backend_client.create_article(article_data)

                    if "created successfully" in result.get("message", ""):
                        new_articles_count += 1
                        logger.info("Article created via API", link=entry.link, id=result.get("id"))
                    elif "already exists" in result.get("message", ""):
                        duplicate_articles_count += 1
                        logger.debug("Article already exists", link=entry.link)

                except Exception as e:
                    failed_articles_count += 1
                    logger.error('Error processing article', link=entry.link, error=str(e))

        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()

        # Log scraping metrics to backend analytics
        backend_client.log_analytics("daily_scrape_completed", {
            "new_articles": new_articles_count,
            "duplicate_articles": duplicate_articles_count,
            "failed_articles": failed_articles_count,
            "feeds_processed": len(rss_feeds),
            "execution_time_seconds": execution_time
        })

        logger.info('Daily scraping completed',
                   new_articles=new_articles_count,
                   duplicates=duplicate_articles_count,
                   failures=failed_articles_count,
                   execution_time=execution_time)

    except Exception as e:
        logger.error('An error occurred in DailyArticleScraper', error=str(e))

    logger.info('DailyArticleScraper function execution finished.')
