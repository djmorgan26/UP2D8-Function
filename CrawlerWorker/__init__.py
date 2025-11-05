import os
import asyncio
import azure.functions as func
from dotenv import load_dotenv
import pymongo
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import datetime
from shared.key_vault_client import get_secret_client
import structlog
from shared.logger_config import configure_logger

# Configure logging
configure_logger()
logger = structlog.get_logger()

async def main(msg: func.QueueMessage) -> None:
    """
    Worker function to crawl a single URL received from a queue message.

    This function is triggered by a message on the `crawling-tasks-queue`. It performs:
    1. Receives a URL to crawl.
    2. Uses Playwright to launch a headless browser and fetch the page content.
    3. Parses the HTML with BeautifulSoup to extract title and main text.
    4. Saves the extracted content as a new document in the `articles` collection.
    """
    load_dotenv()
    url = msg.get_body().decode('utf-8')
    logger.info("CrawlerWorker function executing.", url=url)

    try:
        # --- 1. Configuration and Database Connection ---
        secret_client = get_secret_client()
        cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value

        client = pymongo.MongoClient(cosmos_db_connection_string)
        db = client.up2d8
        articles_collection = db.articles
        # Ensure index exists to prevent duplicates
        articles_collection.create_index([("link", pymongo.ASCENDING)], unique=True)

        # --- 2. Crawl with Playwright ---
        html_content = ""
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(url, wait_until='domcontentloaded', timeout=60000) # 60s timeout
                html_content = await page.content()
                await browser.close()
            except Exception as e:
                logger.error("Playwright failed to get content", url=url, error=str(e))
                # End execution if crawling fails; the message will be removed from the queue.
                return

        if not html_content:
            logger.warning("No HTML content found.", url=url)
            return

        # --- 3. Parse with BeautifulSoup ---
        soup = BeautifulSoup(html_content, 'lxml')

        title = soup.title.string if soup.title else "No Title Found"

        # Heuristics to find the main article text
        article_text = ""
        for tag in ['article', 'main', '.post-content', '.article-body', '#content']:
            element = soup.select_one(tag)
            if element:
                article_text = element.get_text(separator='\n', strip=True)
                break
        
        if not article_text:
            article_text = soup.get_text(separator='\n', strip=True) # Fallback to all text

        summary = ' '.join(article_text.splitlines()[:15]) + '...' # Create a summary

        # --- 4. Store Article in Cosmos DB ---
        article_doc = {
            'title': title.strip(),
            'link': url,
            'summary': summary,
            'published': datetime.datetime.utcnow().isoformat(),
            'processed': False,
            'source': 'intelligent_crawler',
            'content': article_text # Storing full content for future use
        }

        try:
            articles_collection.insert_one(article_doc)
            logger.info("Successfully inserted new article", link=url)
        except pymongo.errors.DuplicateKeyError:
            logger.warning("Article already exists, skipping.", link=url)

    except Exception as e:
        logger.error("An unexpected error occurred in CrawlerWorker", url=url, error=str(e))