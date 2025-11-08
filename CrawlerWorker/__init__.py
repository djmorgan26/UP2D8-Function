import os
import asyncio
import azure.functions as func
from dotenv import load_dotenv
import pymongo
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import datetime
from shared.key_vault_client import get_secret_client
from shared.backend_client import BackendAPIClient
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

    # Initialize backend API client
    backend_client = BackendAPIClient()

    try:

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

        # --- 4. Store Article via Backend API ---
        article_data = {
            'title': title.strip(),
            'link': url,
            'summary': summary,
            'published': datetime.datetime.utcnow().isoformat(),
            'tags': [],  # TODO: Add AI-based tagging for crawled articles
            'source': 'intelligent_crawler',
            'content': article_text  # Full content for future use
        }

        try:
            result = backend_client.create_article(article_data)
            if "created successfully" in result.get("message", ""):
                logger.info("Article created via API", link=url, id=result.get("id"))
            else:
                logger.info("Article already exists", link=url)
        except Exception as e:
            logger.error("Failed to create article via API", link=url, error=str(e))

    except Exception as e:
        logger.error("An unexpected error occurred in CrawlerWorker", url=url, error=str(e))