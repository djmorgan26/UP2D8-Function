# UP2D8 Integration Architecture

**Created**: 2025-11-08
**Purpose**: Connect UP2D8-Function (serverless automation) with UP2D8-BACKEND (FastAPI) and up2d8-frontend (React Native)

---

## Current State Analysis

### UP2D8-Function (Azure Functions)
**Purpose**: Automated article scraping and newsletter generation
**Collections Used**:
- `articles` - Stores scraped articles with tags
- `rss_feeds` - RSS feed sources
- `users` - User subscriptions and preferences

**Functions**:
1. **DailyArticleScraper** - Scrapes RSS feeds, stores articles directly in Cosmos DB
2. **NewsletterGenerator** - Generates personalized newsletters using Gemini
3. **CrawlerOrchestrator** - Orchestrates web crawling tasks
4. **CrawlerWorker** - Executes individual crawl tasks
5. **ManualTrigger** - Manual trigger for orchestration

**Current Issues**:
- ❌ Direct Cosmos DB writes (bypasses backend API)
- ❌ No analytics/metrics tracking
- ❌ No health monitoring
- ❌ No user preference change detection
- ❌ No data archival/cleanup

### UP2D8-BACKEND (FastAPI)
**Purpose**: RESTful API for frontend and external integrations
**Endpoints**:
- `/api/articles` - GET articles (read-only, no POST)
- `/api/users` - Full CRUD for users
- `/api/rss_feeds` - Full CRUD for RSS feeds
- `/api/analytics` - POST analytics events
- `/api/feedback` - POST user feedback
- `/api/chat` - Chat with Gemini

**Current Issues**:
- ❌ No POST endpoint for articles (scrapers can't write through API)
- ❌ No webhook/event system for user preference changes
- ❌ No health check endpoints

### up2d8-frontend (React Native)
**Purpose**: Mobile app for users
**Current Issues**:
- ❌ No push notification system
- ❌ Limited integration with backend

---

## Integration Strategy

### Phase 1: Backend API Enhancement (HIGH PRIORITY)

#### 1.1 Add Article POST Endpoint
**File**: `UP2D8-BACKEND/api/articles.py`

```python
from pydantic import BaseModel, HttpUrl

class ArticleCreate(BaseModel):
    title: str
    link: HttpUrl
    summary: str
    published: str
    tags: list[str] = []
    source: str = "rss"  # rss, intelligent_crawler, manual
    content: str | None = None  # Full content for crawled articles

@router.post("/api/articles", status_code=status.HTTP_201_CREATED)
async def create_article(article: ArticleCreate, db=Depends(get_db_client)):
    articles_collection = db.articles

    # Check for duplicates
    existing = articles_collection.find_one({"link": str(article.link)})
    if existing:
        return {"message": "Article already exists.", "id": existing.get("id")}

    article_id = str(uuid.uuid4())
    new_article = {
        "id": article_id,
        "title": article.title,
        "link": str(article.link),
        "summary": article.summary,
        "published": article.published,
        "tags": article.tags,
        "source": article.source,
        "content": article.content,
        "processed": False,
        "created_at": datetime.now(UTC)
    }

    articles_collection.insert_one(new_article)

    # Log analytics
    analytics_collection = db.analytics
    analytics_collection.insert_one({
        "event_type": "article_scraped",
        "details": {
            "article_id": article_id,
            "source": article.source,
            "tags": article.tags
        },
        "timestamp": datetime.now(UTC)
    })

    return {"message": "Article created successfully.", "id": article_id}
```

#### 1.2 Add Health Check Endpoint
**File**: `UP2D8-BACKEND/api/health.py` (NEW)

```python
from fastapi import APIRouter, status, Depends
from dependencies import get_db_client
from datetime import datetime, UTC

router = APIRouter()

@router.get("/api/health", status_code=status.HTTP_200_OK)
async def health_check(db=Depends(get_db_client)):
    try:
        # Test database connection
        db.command('ping')

        # Get stats
        articles_count = db.articles.count_documents({})
        users_count = db.users.count_documents({})
        rss_feeds_count = db.rss_feeds.count_documents({})

        return {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "database": "connected",
            "collections": {
                "articles": articles_count,
                "users": users_count,
                "rss_feeds": rss_feeds_count
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat()
        }
```

#### 1.3 Add User Preference Change Webhook
**File**: `UP2D8-BACKEND/api/users.py` (MODIFY)

```python
# Add this to the update_user function after successful update:

# Trigger webhook for Azure Functions
from azure.storage.queue import QueueClient
import os

# After successful user update:
if "topics" in update_fields or "preferences" in update_fields:
    # Send message to Azure Queue for Functions to process
    queue_client = QueueClient.from_connection_string(
        os.environ["AZURE_STORAGE_CONNECTION_STRING"],
        "user-preference-changes"
    )

    message = {
        "user_id": user_id,
        "updated_fields": list(update_fields.keys()),
        "timestamp": datetime.now(UTC).isoformat()
    }

    queue_client.send_message(json.dumps(message))
```

---

### Phase 2: Azure Functions Integration (HIGH PRIORITY)

#### 2.1 Create Shared HTTP Client
**File**: `UP2D8-Function/shared/backend_client.py` (NEW)

```python
import os
import requests
from typing import Dict, Any, List
from shared.key_vault_client import get_secret_client
import structlog

logger = structlog.get_logger()

class BackendAPIClient:
    """Client for communicating with UP2D8-BACKEND FastAPI service."""

    def __init__(self):
        secret_client = get_secret_client()
        self.base_url = os.environ.get("BACKEND_API_URL", "https://up2d8-backend.azurewebsites.net")
        # Optional: Add API key if backend requires authentication
        # self.api_key = secret_client.get_secret("BACKEND-API-KEY").value

    def create_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post a new article to the backend API."""
        try:
            response = requests.post(
                f"{self.base_url}/api/articles",
                json=article_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error("Failed to create article via API", error=str(e), article=article_data.get("link"))
            raise

    def log_analytics(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log an analytics event."""
        try:
            response = requests.post(
                f"{self.base_url}/api/analytics",
                json={
                    "user_id": "system",  # System events
                    "event_type": event_type,
                    "details": details
                },
                timeout=10
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning("Failed to log analytics", error=str(e))

    def health_check(self) -> Dict[str, Any]:
        """Check backend API health."""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error("Backend health check failed", error=str(e))
            return {"status": "unhealthy", "error": str(e)}
```

#### 2.2 Update DailyArticleScraper to Use Backend API
**File**: `UP2D8-Function/DailyArticleScraper/__init__.py` (MODIFY)

```python
from shared.backend_client import BackendAPIClient

def main(timer: func.TimerRequest) -> None:
    # ... existing setup code ...

    backend_client = BackendAPIClient()

    # ... existing RSS parsing code ...

    for entry in feed.entries:
        try:
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
                logger.info("Article created", link=entry.link, id=result.get("id"))
            else:
                logger.info("Article already exists", link=entry.link)

        except Exception as e:
            logger.error('Error processing article', link=entry.link, error=str(e))

    # Log scraping metrics
    backend_client.log_analytics("daily_scrape_completed", {
        "new_articles": new_articles_count,
        "feeds_processed": len(rss_feeds),
        "execution_time_seconds": (datetime.now() - start_time).total_seconds()
    })
```

#### 2.3 Update CrawlerWorker to Use Backend API
**File**: `UP2D8-Function/CrawlerWorker/__init__.py` (MODIFY)

```python
from shared.backend_client import BackendAPIClient

async def main(msg: func.QueueMessage) -> None:
    # ... existing playwright scraping code ...

    backend_client = BackendAPIClient()

    article_data = {
        'title': title.strip(),
        'link': url,
        'summary': summary,
        'published': datetime.datetime.utcnow().isoformat(),
        'tags': [],  # TODO: Add AI-based tagging
        'source': 'intelligent_crawler',
        'content': article_text
    }

    try:
        result = backend_client.create_article(article_data)
        logger.info("Article created via API", link=url, id=result.get("id"))
    except Exception as e:
        logger.error("Failed to create article via API", link=url, error=str(e))
```

#### 2.4 Create UserPreferenceListener Function (NEW)
**File**: `UP2D8-Function/UserPreferenceListener/__init__.py` (NEW)

```python
import azure.functions as func
import json
import pymongo
from dotenv import load_dotenv
from shared.key_vault_client import get_secret_client
from shared.backend_client import BackendAPIClient
import structlog
from shared.logger_config import configure_logger

configure_logger()
logger = structlog.get_logger()

async def main(msg: func.QueueMessage) -> None:
    """
    Listens for user preference changes and triggers re-processing of articles.
    """
    load_dotenv()
    message_body = json.loads(msg.get_body().decode('utf-8'))
    logger.info("UserPreferenceListener triggered", message=message_body)

    user_id = message_body.get("user_id")
    updated_fields = message_body.get("updated_fields", [])

    # If topics changed, we might want to:
    # 1. Re-tag existing articles
    # 2. Trigger a manual crawl for new topics
    # 3. Update newsletter preferences

    if "topics" in updated_fields:
        logger.info("User topics updated, triggering re-processing", user_id=user_id)

        # TODO: Implement topic-based article re-processing
        # For now, just log the event
        backend_client = BackendAPIClient()
        backend_client.log_analytics("user_topics_changed", {
            "user_id": user_id,
            "updated_fields": updated_fields
        })
```

**File**: `UP2D8-Function/UserPreferenceListener/function.json` (NEW)

```json
{
  "bindings": [
    {
      "name": "msg",
      "type": "queueTrigger",
      "direction": "in",
      "queueName": "user-preference-changes",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```

#### 2.5 Create HealthMonitor Function (NEW)
**File**: `UP2D8-Function/HealthMonitor/__init__.py` (NEW)

```python
import azure.functions as func
from dotenv import load_dotenv
from shared.backend_client import BackendAPIClient
from shared.key_vault_client import get_secret_client
import pymongo
import structlog
from shared.logger_config import configure_logger

configure_logger()
logger = structlog.get_logger()

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP-triggered health check endpoint for monitoring.
    """
    load_dotenv()
    logger.info("HealthMonitor function triggered")

    health_status = {
        "function_app": "healthy",
        "checks": {}
    }

    try:
        # Check Cosmos DB connection
        secret_client = get_secret_client()
        cosmos_connection = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
        client = pymongo.MongoClient(cosmos_connection, serverSelectionTimeoutMS=5000)
        client.server_info()  # Will raise exception if can't connect
        health_status["checks"]["cosmos_db"] = "connected"
    except Exception as e:
        health_status["function_app"] = "unhealthy"
        health_status["checks"]["cosmos_db"] = f"failed: {str(e)}"

    try:
        # Check backend API
        backend_client = BackendAPIClient()
        backend_health = backend_client.health_check()
        health_status["checks"]["backend_api"] = backend_health.get("status", "unknown")
    except Exception as e:
        health_status["checks"]["backend_api"] = f"failed: {str(e)}"

    try:
        # Check Key Vault
        secret_client = get_secret_client()
        secret_client.get_secret("UP2D8-GEMINI-API-Key")
        health_status["checks"]["key_vault"] = "accessible"
    except Exception as e:
        health_status["function_app"] = "unhealthy"
        health_status["checks"]["key_vault"] = f"failed: {str(e)}"

    status_code = 200 if health_status["function_app"] == "healthy" else 503

    return func.HttpResponse(
        body=json.dumps(health_status, indent=2),
        status_code=status_code,
        mimetype="application/json"
    )
```

**File**: `UP2D8-Function/HealthMonitor/function.json` (NEW)

```json
{
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["get"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

#### 2.6 Create DataArchival Function (NEW)
**File**: `UP2D8-Function/DataArchival/__init__.py` (NEW)

```python
import azure.functions as func
from datetime import datetime, timedelta, UTC
import pymongo
from dotenv import load_dotenv
from shared.key_vault_client import get_secret_client
from shared.backend_client import BackendAPIClient
import structlog
from shared.logger_config import configure_logger

configure_logger()
logger = structlog.get_logger()

def main(timer: func.TimerRequest) -> None:
    """
    Weekly timer-triggered function to archive/delete old data.
    Schedule: 0 0 * * 0 (Every Sunday at midnight)
    """
    load_dotenv()
    logger.info("DataArchival function executing")

    try:
        secret_client = get_secret_client()
        cosmos_connection = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value

        client = pymongo.MongoClient(cosmos_connection)
        db = client.up2d8

        # Archive processed articles older than 90 days
        cutoff_date = datetime.now(UTC) - timedelta(days=90)

        result = db.articles.delete_many({
            "processed": True,
            "created_at": {"$lt": cutoff_date}
        })

        archived_count = result.deleted_count
        logger.info("Archived old articles", count=archived_count)

        # Delete old analytics events (keep 180 days)
        analytics_cutoff = datetime.now(UTC) - timedelta(days=180)

        analytics_result = db.analytics.delete_many({
            "timestamp": {"$lt": analytics_cutoff}
        })

        logger.info("Archived analytics events", count=analytics_result.deleted_count)

        # Log archival metrics
        backend_client = BackendAPIClient()
        backend_client.log_analytics("data_archival_completed", {
            "articles_archived": archived_count,
            "analytics_archived": analytics_result.deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        })

    except Exception as e:
        logger.error("DataArchival failed", error=str(e))
```

**File**: `UP2D8-Function/DataArchival/function.json` (NEW)

```json
{
  "bindings": [
    {
      "name": "timer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 0 * * 0"
    }
  ]
}
```

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         UP2D8 ECOSYSTEM                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│  UP2D8-Function      │         │  UP2D8-BACKEND       │
│  (Azure Functions)   │◄────────┤  (FastAPI)           │
│                      │  HTTP   │                      │
│  • DailyArticle      │  API    │  • POST /api/articles│
│    Scraper           ├────────►│  • GET /api/health   │
│  • Crawler           │         │  • POST /api/        │
│    Worker            │         │    analytics         │
│  • Newsletter        │         │  • User Management   │
│    Generator         │         │                      │
│  • Health            │         │                      │
│    Monitor           │         │                      │
│  • Data              │         │                      │
│    Archival          │         │                      │
│  • Preference        │         │                      │
│    Listener          │         │                      │
└──────────┬───────────┘         └──────────┬───────────┘
           │                                │
           │      ┌─────────────────┐      │
           └─────►│   Cosmos DB     │◄─────┘
                  │   (MongoDB API) │
                  │                 │
                  │  • articles     │
                  │  • users        │
                  │  • rss_feeds    │
                  │  • analytics    │
                  └─────────────────┘
                          ▲
                          │
                  ┌───────┴───────┐
                  │ up2d8-frontend│
                  │ (React Native)│
                  │               │
                  │ • News Feed   │
                  │ • Profile     │
                  │ • Settings    │
                  └───────────────┘
```

---

## Implementation Checklist

### Backend Enhancements
- [ ] Add POST /api/articles endpoint
- [ ] Add GET /api/health endpoint
- [ ] Add user preference change queue integration
- [ ] Update requirements.txt with azure-storage-queue
- [ ] Add environment variable AZURE_STORAGE_CONNECTION_STRING

### Function App Enhancements
- [ ] Create shared/backend_client.py
- [ ] Update DailyArticleScraper to use backend API
- [ ] Update CrawlerWorker to use backend API
- [ ] Create UserPreferenceListener function
- [ ] Create HealthMonitor function
- [ ] Create DataArchival function
- [ ] Update requirements.txt with requests
- [ ] Add environment variable BACKEND_API_URL

### Configuration Changes
- [ ] Add AZURE_STORAGE_CONNECTION_STRING to both repos
- [ ] Add BACKEND_API_URL to Function App
- [ ] Create Azure Storage Queue: "user-preference-changes"
- [ ] Update Cosmos DB indexes if needed

### Testing
- [ ] Test article creation via API
- [ ] Test health check endpoints
- [ ] Test user preference webhook
- [ ] Test analytics logging
- [ ] Test data archival (with test data)
- [ ] Integration testing between repos

### Documentation
- [ ] Update .ai/knowledge with new functions
- [ ] Document API contracts
- [ ] Document deployment process
- [ ] Run /capture for all new features

---

## Next Steps

1. **Immediate**: Implement Backend API enhancements (POST /api/articles, health endpoint)
2. **High Priority**: Create shared backend_client.py and update scrapers
3. **Medium Priority**: Add new Azure Functions (HealthMonitor, UserPreferenceListener)
4. **Low Priority**: Implement DataArchival and advanced features

---

## Benefits of This Architecture

✅ **Centralized Data Access**: All writes go through backend API
✅ **Analytics Tracking**: All operations logged for monitoring
✅ **Health Monitoring**: Proactive system health checks
✅ **User Responsiveness**: React to preference changes in real-time
✅ **Data Management**: Automated cleanup and archival
✅ **Scalability**: Clear separation of concerns
✅ **Maintainability**: Single source of truth for business logic

