import azure.functions as func
from dotenv import load_dotenv
import structlog
from shared.orchestration_logic import find_new_articles
from shared.logger_config import configure_logger

# Configure logging
configure_logger()
logger = structlog.get_logger()

def main(timer: func.TimerRequest):
    """
    Timer-triggered function that invokes the core orchestration logic to find and queue new articles.
    """
    load_dotenv()
    logger.info("CrawlerOrchestrator function executing via timer trigger.")
    
    new_urls = find_new_articles()
    
    return new_urls