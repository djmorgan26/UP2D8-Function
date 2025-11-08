import os
import pymongo
from langchain_community.utilities import GoogleSearchAPIWrapper
from shared.key_vault_client import get_secret_client
import structlog

logger = structlog.get_logger()

def find_new_articles() -> list[str]:
    """
    Core orchestration logic to find new articles based on user topics.
    This function is designed to be called by different triggers.
    """
    try:
        # --- 1. Configuration and Database Connection ---
        secret_client = get_secret_client()
        
        cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
        google_api_key = secret_client.get_secret("GOOGLE-CUSTOM-SEARCH-API").value
        google_cse_id = os.getenv("GOOGLE_CSE_ID")

        if not google_cse_id:
            logger.warning("GOOGLE_CSE_ID is not set. Orchestration cannot run.")
            return []

        os.environ["GOOGLE_API_KEY"] = google_api_key
        os.environ["GOOGLE_CSE_ID"] = google_cse_id

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
            try:
                search_results = search.results(f"latest articles about {topic}", num_results=5)
                for res in search_results:
                    if "link" in res:
                        all_found_urls.add(res["link"])
            except Exception as e:
                logger.error("Error during search for topic", topic=topic, error=str(e))

        if not all_found_urls:
            logger.warning("Search did not return any URLs.")
            return []
        
        logger.info("Found total URLs from search", count=len(all_found_urls))

        # --- 4. Deduplicate against existing articles ---
        existing_links = {article["link"] for article in articles_collection.find({"link": {"$in": list(all_found_urls)}}, {"link": 1})}
        
        logger.info("Found existing articles in DB", count=len(existing_links))

        new_urls_to_crawl = list(all_found_urls - existing_links)

        logger.info("Queuing new URLs for crawling", count=len(new_urls_to_crawl))

        return new_urls_to_crawl

    except Exception as e:
        logger.error("An unexpected error occurred in orchestration logic", error=str(e))
        return []
