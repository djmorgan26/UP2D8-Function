---
type: component
name: Backend API Client
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - shared/backend_client.py
related:
  - .ai/knowledge/features/daily-article-scraper.md
  - .ai/knowledge/features/crawler-worker.md
  - .ai/knowledge/features/health-monitor.md
  - .ai/knowledge/features/data-archival.md
tags: [http-client, integration, api, backend, analytics]
---

# Backend API Client

## What It Does
HTTP client for communicating with the UP2D8-BACKEND FastAPI service. Provides centralized methods for creating articles, logging analytics events, performing health checks, and fetching users/RSS feeds. Replaces direct Cosmos DB writes with API calls to establish a single source of truth.

## How It Works
The `BackendAPIClient` class provides a typed HTTP interface to the backend API using the `requests` library. Automatically retrieves the backend URL from environment variables with a default fallback. All methods include proper error handling, timeout configuration, and structured logging.

**Key files:**
- `shared/backend_client.py:1-183` - Complete implementation with 5 public methods

## Architecture

### Initialization
```python
class BackendAPIClient:
    def __init__(self):
        self.base_url = os.environ.get(
            "BACKEND_API_URL",
            "https://up2d8-backend.azurewebsites.net"
        )
        self.base_url = self.base_url.rstrip('/')
```

- Reads `BACKEND_API_URL` from environment (allows environment-specific endpoints)
- Defaults to production URL if not specified
- Strips trailing slashes for consistent URL construction
- Logs initialization with base URL for debugging

### Public Methods

#### 1. `create_article(article_data: Dict[str, Any]) -> Dict[str, Any]`
**Purpose**: Post new articles to backend API

**Expected article_data structure**:
```python
{
    "title": str,           # Required
    "link": str,            # Required (must be unique)
    "summary": str,         # Required
    "published": str,       # Required (ISO format)
    "tags": list[str],      # Optional (default: [])
    "source": str,          # Optional (rss | intelligent_crawler | manual)
    "content": str          # Optional (full article text for crawled articles)
}
```

**Returns**:
```python
{
    "message": "Article created successfully." | "Article already exists.",
    "id": str  # Article ID (UUID)
}
```

**Behavior**:
- POST to `/api/articles`
- 30-second timeout for large payloads
- Auto-deduplication on backend (by link field)
- Logs success with article link and ID
- Raises `requests.RequestException` on failure

**Error Handling**:
- Logs error with status code, link, and error message
- Re-raises exception for caller to handle
- Structured logging for analytics

#### 2. `log_analytics(event_type: str, details: Dict[str, Any], user_id: str = "system") -> Optional[Dict[str, Any]]`
**Purpose**: Log analytics events to backend

**Parameters**:
- `event_type`: Event name (e.g., "daily_scrape_completed")
- `details`: Event-specific data dictionary
- `user_id`: User identifier or "system" for automated events

**Returns**:
- Response dictionary on success
- `None` on failure (non-critical, doesn't raise)

**Behavior**:
- POST to `/api/analytics`
- 10-second timeout (analytics is non-critical)
- Silent failure with warning log (doesn't block main operation)
- Used for metrics, monitoring, and usage tracking

**Common Event Types**:
- `daily_scrape_completed` - After DailyArticleScraper runs
- `data_archival_completed` - After DataArchival runs
- `data_archival_failed` - When archival encounters errors
- `health_check_performed` - System health checks
- Custom events as needed

#### 3. `health_check() -> Dict[str, Any]`
**Purpose**: Check backend API health status

**Returns on success**:
```python
{
    "status": "healthy",
    "database": "connected",
    "collections": {
        "articles": int,
        "users": int,
        "rss_feeds": int
    },
    "timestamp": str  # ISO format
}
```

**Returns on failure**:
```python
{
    "status": "unhealthy",
    "error": str,
    "timestamp": None
}
```

**Behavior**:
- GET to `/api/health`
- 10-second timeout
- Catches all exceptions and returns error dict
- Used by HealthMonitor function for system monitoring

#### 4. `get_users() -> Optional[list]`
**Purpose**: Fetch all users from backend

**Returns**:
- List of user dictionaries on success
- `None` on failure

**Behavior**:
- GET to `/api/users`
- 10-second timeout
- Used by functions that need user data (e.g., NewsletterGenerator)

#### 5. `get_rss_feeds() -> Optional[list]`
**Purpose**: Fetch all RSS feeds from backend

**Returns**:
- List of RSS feed dictionaries on success
- `None` on failure

**Behavior**:
- GET to `/api/rss_feeds`
- 10-second timeout
- Currently, DailyArticleScraper still reads from Cosmos DB directly
- Available for future migration to fully API-based data fetching

## Important Decisions

### Decision 1: Use Requests Library Instead of aiohttp
**Rationale**:
- Most Azure Functions are synchronous timer triggers
- Only CrawlerWorker is async
- Mixing sync/async HTTP clients adds complexity
- `requests` is simpler and sufficient for current needs
- Can migrate to async client later if needed

### Decision 2: Silent Analytics Failures
**Rationale**:
- Analytics logging is non-critical
- Shouldn't block article creation or scraping operations
- Returns `None` instead of raising exceptions
- Logs warnings for monitoring but doesn't halt execution

### Decision 3: No API Key Authentication (Yet)
**Rationale**:
- Backend API is currently public
- Backend performs its own validation
- Authentication can be added later via Key Vault
- Lines 28-30 show where to add API key if needed

### Decision 4: Centralized Base URL Configuration
**Rationale**:
- Single environment variable controls all API calls
- Easy to switch between dev/staging/prod environments
- Default production URL for convenience
- Override with `BACKEND_API_URL` environment variable

## Usage Examples

### Creating Articles (DailyArticleScraper)
```python
backend_client = BackendAPIClient()

article_data = {
    'title': entry.title,
    'link': entry.link,
    'summary': entry.summary,
    'published': entry.published,
    'tags': tags,
    'source': 'rss'
}

result = backend_client.create_article(article_data)

if "created successfully" in result.get("message", ""):
    new_articles_count += 1
    logger.info("Article created", link=entry.link, id=result.get("id"))
elif "already exists" in result.get("message", ""):
    duplicate_articles_count += 1
```

### Logging Analytics
```python
backend_client.log_analytics("daily_scrape_completed", {
    "new_articles": new_articles_count,
    "feeds_processed": len(rss_feeds),
    "execution_time_seconds": (datetime.now() - start_time).total_seconds(),
    "failed_articles": failed_articles_count,
    "duplicate_articles": duplicate_articles_count
})
```

### Health Checks (HealthMonitor)
```python
backend_client = BackendAPIClient()
backend_health = backend_client.health_check()

health_status["checks"]["backend_api"] = {
    "status": backend_health.get("status", "unknown"),
    "database": backend_health.get("database", "unknown")
}

if backend_health.get("status") != "healthy":
    health_status["function_app"] = "degraded"
```

## Testing

**Manual Testing**:
1. Set `BACKEND_API_URL` to local/dev endpoint
2. Run DailyArticleScraper with test RSS feeds
3. Verify articles appear in backend database
4. Check analytics collection for logged events

**Integration Testing**:
- Test article creation with duplicate links (should not fail)
- Test analytics logging failures (should not block)
- Test health check with backend down (should return error dict)
- Test timeout scenarios (30s for articles, 10s for others)

**Test Files**: None yet (manual testing only)

## Common Issues

### Issue: Backend API Unreachable
**Symptoms**: `create_article()` raises `requests.RequestException`
**Solution**:
- Check `BACKEND_API_URL` environment variable
- Verify backend is running (check health endpoint)
- Check network connectivity from Azure Functions
- Review backend logs for errors

### Issue: Article Creation Fails Silently
**Symptoms**: Function completes but articles missing
**Solution**:
- Check structured logs for error messages
- Verify article data format matches backend schema
- Check backend API response codes (400 = validation, 500 = server error)
- Ensure `link` field is a valid URL

### Issue: Analytics Not Logging
**Symptoms**: No analytics events in database
**Solution**:
- This is expected behavior (silent failures)
- Check warning logs for analytics failures
- Verify backend `/api/analytics` endpoint is working
- Not critical - main operations should continue

## Related Knowledge
- [DailyArticleScraper](../features/daily-article-scraper.md) - Uses `create_article()` and `log_analytics()`
- [CrawlerWorker](../features/crawler-worker.md) - Uses `create_article()` for crawled articles
- [HealthMonitor](../features/health-monitor.md) - Uses `health_check()` for system monitoring
- [DataArchival](../features/data-archival.md) - Uses `log_analytics()` for archival metrics
- [Integration Architecture](../../../INTEGRATION_ARCHITECTURE.md) - Overall integration design

## Future Ideas
- [ ] Add async version (`BackendAPIClientAsync`) for CrawlerWorker
- [ ] Implement API key authentication via Key Vault
- [ ] Add retry logic with exponential backoff for transient failures
- [ ] Add circuit breaker pattern for backend unavailability
- [ ] Implement request caching for `get_users()` and `get_rss_feeds()`
- [ ] Add Prometheus metrics for API call latencies
- [ ] Add bulk article creation endpoint support
- [ ] Implement response pagination for large data sets
