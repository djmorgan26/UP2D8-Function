import logging
import os
import feedparser
import pymongo
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import azure.functions as func
from dotenv import load_dotenv
from shared.key_vault_client import get_secret_client

def main(timer: func.TimerRequest) -> None:
    load_dotenv()
    logging.info('Python timer trigger function ran at %s', timer.past_due)
    logging.info('DailyArticleScraper function is executing.')

    try:
        # Get configuration from environment variables and Key Vault
        secret_client = get_secret_client()

        cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
        
        # Read RSS feeds from file
        with open('rss_feeds.txt', 'r') as f:
            rss_feeds = [line.strip() for line in f if line.strip()]

        # Connect to Cosmos DB
        client = pymongo.MongoClient(cosmos_db_connection_string)
        db = client.up2d8
        articles_collection = db.articles

        # Create a unique index on the 'link' field to prevent duplicates
        articles_collection.create_index([("link", pymongo.ASCENDING)], unique=True)

        new_articles_count = 0
        for feed_url in rss_feeds:
            logging.info(f'Parsing feed: {feed_url}')
            try:
                feed = feedparser.parse(feed_url)
                if feed.bozo:
                    logging.warning(f'Malformed feed detected for {feed_url}: {feed.bozo_exception}')
                    continue
            except Exception as e:
                logging.error(f'Error parsing feed {feed_url}: {e}')
                continue

            for entry in feed.entries:
                try:
                    article = {
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.summary,
                        'published': entry.published,
                        'processed': False
                    }
                    articles_collection.insert_one(article)
                    new_articles_count += 1
                except pymongo.errors.DuplicateKeyError:
                    logging.warning(f'Article already exists: {entry.link}')
                except Exception as e:
                    logging.error(f'Error processing article {entry.link}: {e}')

        logging.info(f'Added {new_articles_count} new articles.')

    except Exception as e:
        logging.error(f'An error occurred in DailyArticleScraper: {e}')

    logging.info('DailyArticleScraper function execution finished.')
