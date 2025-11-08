import os
import azure.functions as func
from dotenv import load_dotenv
import structlog
from shared.orchestration_logic import find_new_articles
from shared.logger_config import configure_logger
from azure.storage.queue import QueueClient, TextBase64EncodePolicy

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP-triggered function that invokes the core orchestration logic and manually queues new articles.
    """
    load_dotenv()
    logger = structlog.get_logger()
    logger.info("ManualTrigger function executing via HTTP trigger.")
    
    # Find new articles to crawl using the shared logic
    new_urls = find_new_articles()
    
    # Manually send the URLs to the storage queue
    queued_count = 0
    if new_urls:
        try:
            connection_string = os.getenv("UP2D8_STORAGE_CONNECTION_STRING")
            if not connection_string:
                raise ValueError("UP2D8_STORAGE_CONNECTION_STRING is not set.")

            queue_client = QueueClient.from_connection_string(
                conn_str=connection_string, 
                queue_name="crawling-tasks-queue",
                message_encode_policy=TextBase64EncodePolicy() # Recommended for Azure Functions
            )

            for url in new_urls:
                queue_client.send_message(url)
                queued_count += 1
            
            logger.info("Successfully sent messages to the queue", count=queued_count)

        except Exception as e:
            logger.error("Failed to send messages to queue", error=str(e))
            return func.HttpResponse(
                "Error: Orchestration ran, but failed to queue messages for crawling.",
                status_code=500
            )

    # Return a confirmation HTTP response to the caller.
    return func.HttpResponse(
        f"Orchestration complete. Found and queued {queued_count} new URLs for crawling.",
        status_code=200
    )
