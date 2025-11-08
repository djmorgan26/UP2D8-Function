import json
import azure.functions as func
from dotenv import load_dotenv
from shared.backend_client import BackendAPIClient
from shared.key_vault_client import get_secret_client
import pymongo
import structlog
from shared.logger_config import configure_logger

# Configure structlog
configure_logger()
logger = structlog.get_logger()

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP-triggered health check endpoint for monitoring Azure Functions.

    Tests:
    - Cosmos DB connectivity
    - Backend API connectivity and health
    - Azure Key Vault accessibility

    Returns:
        JSON response with health status (200 if healthy, 503 if unhealthy)
    """
    load_dotenv()
    logger.info("HealthMonitor function triggered")

    health_status = {
        "function_app": "healthy",
        "checks": {}
    }

    # --- Check 1: Cosmos DB Connection ---
    try:
        secret_client = get_secret_client()
        cosmos_connection = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
        client = pymongo.MongoClient(cosmos_connection, serverSelectionTimeoutMS=5000)
        client.server_info()  # Will raise exception if can't connect
        health_status["checks"]["cosmos_db"] = "connected"
        logger.debug("Cosmos DB health check passed")
    except Exception as e:
        health_status["function_app"] = "unhealthy"
        health_status["checks"]["cosmos_db"] = f"failed: {str(e)}"
        logger.error("Cosmos DB health check failed", error=str(e))

    # --- Check 2: Backend API ---
    try:
        backend_client = BackendAPIClient()
        backend_health = backend_client.health_check()
        health_status["checks"]["backend_api"] = {
            "status": backend_health.get("status", "unknown"),
            "database": backend_health.get("database", "unknown")
        }

        if backend_health.get("status") != "healthy":
            health_status["function_app"] = "degraded"

        logger.debug("Backend API health check completed", status=backend_health.get("status"))
    except Exception as e:
        health_status["function_app"] = "degraded"
        health_status["checks"]["backend_api"] = f"failed: {str(e)}"
        logger.error("Backend API health check failed", error=str(e))

    # --- Check 3: Key Vault ---
    try:
        secret_client = get_secret_client()
        secret_client.get_secret("UP2D8-GEMINI-API-Key")
        health_status["checks"]["key_vault"] = "accessible"
        logger.debug("Key Vault health check passed")
    except Exception as e:
        health_status["function_app"] = "unhealthy"
        health_status["checks"]["key_vault"] = f"failed: {str(e)}"
        logger.error("Key Vault health check failed", error=str(e))

    # Determine HTTP status code
    if health_status["function_app"] == "healthy":
        status_code = 200
    elif health_status["function_app"] == "degraded":
        status_code = 200  # Still operational, just degraded
    else:
        status_code = 503  # Service unavailable

    logger.info("Health check completed", status=health_status["function_app"], status_code=status_code)

    return func.HttpResponse(
        body=json.dumps(health_status, indent=2),
        status_code=status_code,
        mimetype="application/json"
    )
