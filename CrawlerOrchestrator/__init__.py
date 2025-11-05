import os
import azure.functions as func
from dotenv import load_dotenv
import pymongo
from langchain_community.utilities import GoogleSearchAPIWrapper
from shared.key_vault_client import get_secret_client
import structlog
from shared.logger_config import configure_logger

def main(timer: func.TimerRequest):
    """
    Orchestrator function to find new articles based on user topics and queue them for crawling.

    This function is triggered on a timer. It performs the following steps:
    1. Fetches all user-subscribed topics from the database.
    2. Uses a search tool to find relevant article URLs for each topic.
    3. Compares the found URLs against the existing articles in the database.
    4. Returns a list of new, unique URLs, which are then placed on a storage queue
       by the Azure Function's output binding for the CrawlerWorker to process.
    """
    load_dotenv()
    logger.info("CrawlerOrchestrator function executing.")

    try:
        # --- 1. Configuration and Database Connection ---
        secret_client = get_secret_client()
        
        # Get secrets from Key Vault
        cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
        google_api_key = secret_client.get_secret("GOOGLE-CUSTOM-SEARCH-API").value
        google_cse_id = os.getenv("GOOGLE-CSE-ID")

        os.environ["GOOGLE_API_KEY"] = google_api_key
        os.environ["GOOGLE_CSE_ID"] = google_cse_id

        # Connect to Cosmos DB
        client = pymongo.MongoClient(cosmos_db_connection_string)
        db = client.up2d8
        users_collection = db.users
        articles_collection = db.articles

        # --- 2. Fetch User Topics ---
        all_topics = set()
        for user in users_collection.find({}, {"topics": 1}):
            for topic in user.get("topics", []):
                all_topics.add(topic)
        
        if not all_topics:
            logger.warning("No user topics found. Orchestrator finished without searching.")
            return []

        logger.info("Found unique user topics", topics=list(all_topics))

        # --- 3. Search for Articles ---
        search = GoogleSearchAPIWrapper()
        all_found_urls = set()

        for topic in all_topics:
            logger.info("Searching for articles", topic=topic)
            # The search tool returns a string, not a list. We can use a simple split.
            # A more robust solution would use a dedicated parser if the format was complex.
            try:
                search_results_str = search.run(f"latest articles about {topic}")
                # Simple split based on observed output format
                results = search_results_str.strip("[]").split("), (")
                for res in results:
                    # Extract link which is usually the second element
                    parts = res.split(", '")
                    if len(parts) > 1:
                        link = parts[1].strip().strip("'")
                        if link.startswith("http"):
                            all_found_urls.add(link)
            except Exception as e:
                logger.error("Error during search for topic", topic=topic, error=str(e))

        if not all_found_urls:
            logger.warning("Search did not return any URLs.")
            return []
        
        logger.info("Found total URLs from search", count=len(all_found_urls))

        # --- 4. Deduplicate against existing articles ---
        existing_links = set()
        for article in articles_collection.find({"link": {"$in": list(all_found_urls)}}, {"link": 1}):
            existing_links.add(article["link"])
        
        logger.info("Found existing articles in DB", count=len(existing_links))

        new_urls_to_crawl = list(all_found_urls - existing_links)

        logger.info("Queuing new URLs for crawling", count=len(new_urls_to_crawl))

        # --- 5. Return URLs for Queueing ---
        return new_urls_to_crawl

    except Exception as e:
        logger.error("An unexpected error occurred in CrawlerOrchestrator", error=str(e))
        return []
