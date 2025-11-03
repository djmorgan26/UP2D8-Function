import os
import feedparser
import pymongo
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import azure.functions as func
from dotenv import load_dotenv
from shared.key_vault_client import get_secret_client
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
    logger.info('Python timer trigger function ran', past_due=timer.past_due)
    logger.info('DailyArticleScraper function is executing.')

    try:
        # Get configuration from environment variables and Key Vault
        secret_client = get_secret_client()

        cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
        
        # Connect to Cosmos DB
        client = pymongo.MongoClient(cosmos_db_connection_string)
        db = client.up2d8
        articles_collection = db.articles
        rss_feeds_collection = db.rss_feeds # New: Connect to rss_feeds collection

        # Fetch RSS feeds from Cosmos DB
        rss_feeds = [feed['url'] for feed in rss_feeds_collection.find({})]
        if not rss_feeds:
            logging.warning("No RSS feeds found in Cosmos DB. DailyArticleScraper will not run.")
            return

        # Create a unique index on the 'link' field to prevent duplicates
        articles_collection.create_index([("link", pymongo.ASCENDING)], unique=True)

        new_articles_count = 0
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

                    article = {
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.summary,
                        'published': entry.published,
                        'processed': False,
                        'tags': tags # Add the new tags field
                    }
                    articles_collection.insert_one(article)
                    new_articles_count += 1
                except pymongo.errors.DuplicateKeyError:
                    logger.warning('Article already exists', link=entry.link)
                except Exception as e:
                    logger.error('Error processing article', link=entry.link, error=str(e))

        logger.info('Added new articles', count=new_articles_count)

    except Exception as e:
        logger.error('An error occurred in DailyArticleScraper', error=str(e))

    logger.info('DailyArticleScraper function execution finished.')
